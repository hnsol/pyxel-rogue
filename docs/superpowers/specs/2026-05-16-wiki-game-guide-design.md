# Design: Wiki攻略ページ自動生成

## Context

現行wikiはエッセイ・設計論が中心（Playable-Critical-Edition、Rogue-as-Life-Work等）で攻略情報がない。
Pyxelゲームのソースコードから直接データを読んで生成することで、コードと常に同期した攻略ページを実現する。

## 目標

- `tools/generate_wiki.py` を実行するだけで `wiki/Game-Guide-ja.md` と `wiki/Game-Guide-en.md` を生成
- ゲームの実際の挙動（確率・ダメージ・メッセージ）を正確に反映
- モンスター出現分布を理論値で計算して「カッコいい表」として表示

## 生成物

| ファイル | 説明 |
|---------|------|
| `wiki/Game-Guide-ja.md` | 日本語攻略ページ |
| `wiki/Game-Guide-en.md` | 英語攻略ページ |

## ページ構成（両言語共通）

### 1. フロア別モンスター出現表

全26フロア × 全26モンスターの確率ヒートマップ表。
各セルに確率（%）を表示し、≥20%は強調（**bold**）。

**理論値計算方法:**

`LEVEL_MONSTERS = "KEBSHIROZLCQANYFTWPXUMVGJD"` のindex `d`（0-25）が各モンスターの「深さ位置」。

`randmonster(level)` の確率分布（level=フロア番号1-26）:
```
depth_candidate = level + rnd(10) - 6   # rnd(10) ∈ {0..9}
if depth_candidate < 0:  depth = rnd(5)         # 0..4, 各1/5
if depth_candidate > 25: depth = rnd(5) + 21    # 21..25, 各1/5
else:                    depth = depth_candidate
```

`rnd(10)` が10通り均等なので、各 `d`（0-25）の確率を解析的に計算できる。
モンスター名はBESTIARY、日本語名は `assets/terms/ja.json` から取得。

### 2. 武器一覧（強い順）

近接ダメージ（平均値）の降順でソート。
列：名前(ja)、名前(en)、近接ダメージ、投擲ダメージ、出現確率、価値

```python
# WEAPONS から apply_init_dam() で dam/throw_dam が設定済み
# 平均ダメージ = sum(NxD → N*(D+1)/2)
```

### 3. よろい一覧（強い順）

AC値昇順（低いほど強い）でソート。
列：名前(ja)、名前(en)、AC値、出現確率、価値

### 4. ポーション一覧

出現確率降順。使用時メッセージ（日本語版は ja.json、英語版は en.json）を含む。
列：外見（ランダム色）、名前(ja)、名前(en)、確率、価値、使用メッセージ

**メッセージマッピング:** `assets/messages/{lang}.json` の `potions.*` キーと各ポーション効果を対応付け。対応はゲームコード `rogue.py` の `use_pot()` 関数から追う。

### 5. 巻き物一覧

ポーションと同様。使用時メッセージは `scrolls.*` キー。
Normal は `identify` 巻き物を使う調整表、Classic/Strict は Rogue 5.4.4 表として注記。

### 6. 指輪一覧

列：名前(ja)、名前(en)、確率、価値
食料消費コスト・enchantment特性はコードから `rogue_rings.RINGS` を参照。

### 7. 杖一覧

列：名前(ja)、名前(en)、確率、価値、初期チャージ
`rogue_sticks.initial_charges()` と定数から、light は 10-19、その他は 3-7 として表示。

### 8. 罠一覧

8種の罠名と効果サマリー。

## スクリプト設計

### ファイル: `tools/generate_wiki.py`

```python
# データ取得元
import sys
sys.path.insert(0, repo_root)
import rogue  # POTIONS, SCROLLS, WEAPONS, ARMORS, RINGS, STICKS, BESTIARY
import pyxel_rogue.rogue_monsters as rogue_monsters
import pyxel_rogue.rogue_rings as rogue_rings
import pyxel_rogue.rogue_sticks as rogue_sticks
import json  # assets/messages/{lang}.json, assets/terms/{lang}.json

# 出力
def generate(lang: str) -> str: ...  # Markdown文字列を返す

if __name__ == "__main__":
    for lang in ("ja", "en"):
        output = generate(lang)
        Path(f"wiki/Game-Guide-{lang}.md").write_text(output)
```

### 確率計算関数

```python
def monster_prob_matrix() -> dict[int, dict[str, float]]:
    """floor(1-26) -> {monster_sym -> probability(0-1)}"""
    level_str = rogue_monsters.LEVEL_MONSTERS  # "KEBSHIROZLCQANYFTWPXUMVGJD"
    result = {}
    for level in range(1, 27):
        probs = {}
        for rnd10 in range(10):
            dc = level + rnd10 - 6
            if dc < 0:
                for d5 in range(5):
                    sym = level_str[d5]
                    probs[sym] = probs.get(sym, 0) + (1/10) * (1/5)
            elif dc > 25:
                for d5 in range(5):
                    sym = level_str[21 + d5]
                    probs[sym] = probs.get(sym, 0) + (1/10) * (1/5)
            else:
                sym = level_str[dc]
                probs[sym] = probs.get(sym, 0) + 1/10
        result[level] = probs
    return result
```

### 用語翻訳

`assets/terms/ja.json` に全アイテム・全モンスターの日本語名あり（確認済み）。
- モンスター名: `data["monster"][name]`
- アイテム名: `data["item"][category][name]`（potion/scroll/ring/stick/armor/weapon/food/amulet）

## データソースファイル

| ファイル | 用途 |
|---------|------|
| `rogue.py:434-` | POTIONS, SCROLLS, WEAPONS, ARMORS 定義 |
| `rogue.py:568-` | BESTIARY (MonsterSpec) 定義 |
| `rogue.py:526-527` | RINGS, STICKS (rogue_rings/sticks から生成) |
| `pyxel_rogue/rogue_monsters.py:12` | LEVEL_MONSTERS 文字列 |
| `pyxel_rogue/rogue_rings.py` | RINGS 詳細（food cost, enchant等） |
| `pyxel_rogue/rogue_sticks.py` | STICKS 詳細（charge情報） |
| `assets/messages/ja.json` | 日本語使用メッセージ |
| `assets/messages/en.json` | 英語使用メッセージ |
| `assets/terms/ja.json` | 日本語用語（アイテム名等） |
| `assets/terms/en.json` | 英語用語 |

## wiki構成の再設計

### 現状

現行wikiは「設計論・文化的背景」のエッセイのみ。言語別2セクション構造。

```
## 日本語                          ## English
- 遊べる校訂復刻                    - A Playable Critical Edition
- 校訂版アウトライン                 - Critical Edition Outline
- 近接メッセージログ                  - Proximity Message Log
- ライフワークとしてのRogue            - Rogue as a Life Work
```

### 新構成: 言語別 × コンテンツ種別

各言語セクション内を「攻略情報」と「プロジェクトについて」の2カテゴリに分ける。攻略情報を先頭に置く。

**`wiki/_Sidebar.md` 新構成:**

Home は GitHub Wiki のデフォルトランディングページとして機能するため、サイドバーには載せない。
各言語セクションはフラットに「攻略情報」→「プロジェクトについて」の順で並べる。

```markdown
# Rogue V5 on Pyxel

## 日本語

### 攻略情報
- [攻略ガイド](Game-Guide-ja)

### プロジェクトについて
- [Rogue V5の遊べる校訂復刻](Playable-Critical-Edition-ja)
- [校訂版アウトライン](Critical-Edition-Outline-ja)
- [近接メッセージログ](Proximity-Message-Log-ja)
- [ライフワークとしてのRogue](Rogue-as-Life-Work-ja)

## English

### Game Guide
- [Game Guide](Game-Guide-en)

### About the Project
- [A Playable Critical Edition](Playable-Critical-Edition-en)
- [Critical Edition Outline](Critical-Edition-Outline-en)
- [Proximity Message Log](Proximity-Message-Log-en)
- [Rogue as a Life Work](Rogue-as-Life-Work-en)

## Notes
- [Editorial Notes](Editorial-Notes)
```

**`wiki/Home.md` 更新:**
- 冒頭の説明文に攻略情報への言及を追加
- 日本語・英語の両セクションに攻略ガイドリンクを先頭追加

### 設計理由

- 既存の言語別構造を維持（読者は言語でまず選択するため）
- コンテンツ種別（攻略 vs 設計論）をサブセクションで明示
- 攻略情報を上位に置くことで新規ユーザーの導線を優先
- 将来的に攻略ページを増やしても「攻略情報」セクション内に収まる

## 検証

```bash
# スクリプト実行
python3 tools/generate_wiki.py

# 出力確認
wc -l wiki/Game-Guide-ja.md wiki/Game-Guide-en.md
cat wiki/Game-Guide-ja.md | head -100

# 確率の和が1.0になること
python3 -c "
from tools.generate_wiki import monster_prob_matrix
m = monster_prob_matrix()
for floor, probs in m.items():
    total = sum(probs.values())
    assert abs(total - 1.0) < 1e-9, f'floor {floor}: sum={total}'
print('All probability sums check OK')
"
```
