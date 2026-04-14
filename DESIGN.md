# DESIGN.md — 設計判断の記録

## プロジェクトの発端

「ボコスカウォーズに類する黎明期の名作を Pyxel で再現」する企画から、ローグを「コントローラ操作対応リメイク」する方向で決定。その後「過剰にオーバースペックな Pyxel 版」にコンセプトが発展。

最終目標: フォント切替 / 日英切替 / BGM / 拡大画面+マップ / バージョン選択（3.6/5.2/5.4）

## 操作体系: GB シレン準拠

最初 Pyxel は A/B の2ボタンのみと誤認 → 実際は A/B/X/Y/L/R/Start/Back 全対応。GB 版「風来のシレン」が D-pad + 少数ボタンでローグライク全操作を実現しておりシンプルなため採用。

```
D-pad → 移動, L+D-pad → 斜め, B長押し+方向 → ダッシュ
A → 拾う/階段, X → メニュー, Y → 待機
Start → ステータス, Back → マップ, R → ヘルプ
```

**注意**: B がダッシュ（btn ホールド）とキャンセル（btnp ワンショット）を兼務。離した瞬間の誤発火に注意。

## フォント: umplus_j10r.bdf

Pyxel 標準フォント 4×6px → 小さい、H が H に見えない。ユーザーが外部フォント指定可能性を指摘 → `pyxel.Font(path)` で BDF 読込可能と判明。Pyxel 同梱の umplus_j10r.bdf は ASCII 6px / CJK 10px / 7187文字（日本語対応）。タイル 7×12px で 34列×20行の視界（旧19×15の1.8倍）。

```python
import os
font = pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__),
                                "examples", "assets", "umplus_j10r.bdf"))
```

## カメラ: デッドゾーン

1歩ごとの中央追従は酔う。中央付近では不動、端5タイルに来たら追従。

## ダンジョン生成

元祖ローグの3×3セクターグリッドアルゴリズムを再現。48×24マップを16×8セクターに分割、6〜9部屋配置、隣接セクター間を通路接続、flood fill で到達保証。

## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

## 1ファイル方針

配布しやすさ、打ち込み時代の精神。バージョン選択でデータ肥大化したら分離可。

## BGM（しろもふさん自動演奏ツール）

ユーザー言及の方式。`pyxel.sounds[n].set()` / `pyxel.musics[n].set()` で MML 的記法から変換する仕組みと推定。GitHub「shiromofu pyxel」で要検索。

## 元祖ローグのソース参照先

https://github.com/Davidslv/rogue （Rogue 5.4 C ソース）

## ロジックテスト用 mock 手順

`python3` の REPL か `python3 -c` で実行する想定。

```python
import types, sys
p = types.ModuleType('pyxel')
p.btn = p.btnp = lambda *a: False
for k in ['KEY_UP','KEY_DOWN','KEY_LEFT','KEY_RIGHT','KEY_H','KEY_J','KEY_K','KEY_L',
          'KEY_Y','KEY_U','KEY_B','KEY_N','KEY_Z','KEY_X','KEY_C','KEY_S',
          'KEY_ESCAPE','KEY_RETURN','KEY_TAB','KEY_PERIOD','KEY_QUESTION','KEY_SLASH',
          'KEY_R','KEY_SHIFT','KEY_LSHIFT','KEY_RSHIFT','KEY_CTRL','KEY_LCTRL',
          'GAMEPAD1_BUTTON_A','GAMEPAD1_BUTTON_B','GAMEPAD1_BUTTON_X','GAMEPAD1_BUTTON_Y',
          'GAMEPAD1_BUTTON_LEFTSHOULDER','GAMEPAD1_BUTTON_RIGHTSHOULDER',
          'GAMEPAD1_BUTTON_BACK','GAMEPAD1_BUTTON_START',
          'GAMEPAD1_BUTTON_DPAD_UP','GAMEPAD1_BUTTON_DPAD_DOWN',
          'GAMEPAD1_BUTTON_DPAD_LEFT','GAMEPAD1_BUTTON_DPAD_RIGHT']:
    setattr(p, k, 0)
class MockFont:
    def __init__(self, *a, **kw): pass
    def text_width(self, s): return len(s)*6
p.Font = MockFont
p.__file__ = '/usr/local/lib/python3.12/dist-packages/pyxel/__init__.py'
sys.modules['pyxel'] = p
src = open('rogue.py').read()
exec(src.replace('if __name__=="__main__":\n    Game()', 'pass'))

# ダンジョン生成テスト
tm, rooms = DGen.gen(5)
print(f'Rooms: {len(rooms)}')

# アイテムテスト
ident = IdentTable()
for _ in range(5):
    it = make_item(5)
    print(f'  {it.cat}: {ident.name(it)}')

# プレイヤーテスト
inv, w, a = start_inv()
pl = Player(); pl.inv=inv; pl.wpn=w; pl.arm=a; pl.recalc_ac()
print(f'AC={pl.ac}, dmg={pl.melee_dmg()}')
```
