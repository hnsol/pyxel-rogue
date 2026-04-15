# TODO.md — Pyxel Rogue

現行本体: `rogue.py`

## 実装済み（Phase 3 完了）

- ✅ ダンジョン生成（3×3セクター、部屋・通路・ドア）
- ✅ モンスター A〜Z 全26種（錆び/毒/ドレイン/混乱/凍結/盗み/再生/飛行等）
- ✅ 戦闘（d20ロール、バンプアタック）
- ✅ ポーション12種・巻物12種・食料2種・武器9種・防具8種（全効果実装）
- ✅ 識別システム（ランダム色名/音節名、使用で判明）
- ✅ インベントリ（最大26個 a〜z）、装備スロット、呪い
- ✅ 空腹度（hungry → weak → faint）
- ✅ BDF フォント / カメラ デッドゾーン / 8方向移動 / ダッシュ
- ✅ オーバーレイ3種（Status / Help / Full Map）

注意: 現行実装は Start+D-pad / X / R / Back を含むが、操作方針は A/B/Start/Select + D-pad 中心に再設計予定。

## Phase 4: ゲームロジック完成（優先度: 高）

目的: Rogue 5.4 のゲームロジックを完成させ、原作と同じ挙動か検証できる状態に近づける。

- [ ] **指輪（Ring）14種** — 2スロット（左右手）、常時効果、ランダム宝石名で識別
  - protection, add strength, sustain strength, searching,
    see invisible, adornment, aggravate monster, dexterity,
    increase damage, regeneration, slow digestion, teleportation,
    stealth, maintain armor
- [ ] **杖（Wand/Staff）14種** — チャージ制、方向指定 zap、ランダム素材名で識別
  - light, invisibility, lightning, fire, cold, polymorph,
    missile, haste monster, slow monster, drain life,
    nothing, teleport away, teleport to, cancellation
- [ ] **罠（Trap）8種** — 隠れていて search で発見、踏むと発動
  - trap door, arrow, sleeping gas, bear trap,
    teleport, dart, rust, mysterious
- [ ] **search コマンド** — 隣接タイルの罠・隠し通路を発見
- [ ] **隠しドア・隠し通路**
- [ ] **Amulet of Yendor** — 26階で出現、1階帰還で勝利
- [ ] 戦闘計算の精密化（元祖 d20 式の完全再現）
- [ ] モンスター sleeping 状態（部屋入室で起きる）
- [ ] モンスター8方向移動
- [ ] 原作 Rogue 5.4 との照合用ロジックテスト整備

## Phase 5: 移植性・UI基盤（優先度: 中）

- [ ] Pyxel Web 対応確認
- [ ] ブラウザ / SteamDeck / 中華ゲーム機向け入力整理
- [ ] 通常8方向移動の整理
- [ ] Start短押しによる斜め移動モード / 8方向移動モード（通常モード）のトグル実装
- [ ] XYLR依存の撤去または任意ショートカット化
- [ ] Select(Back) の正式用途決定（マップまたは補助操作）
- [ ] 可変画面 / レイアウト再計算
- [ ] カメラ追従開始位置の調整
- [ ] 複数 BDF フォント選択 + レイアウト自動再計算
- [ ] 日本語/英語切替（全メッセージ辞書化、umplus_j10r は CJK 対応済み）
- [ ] BGM 導入方式検討
  - `8bit-bgm-generator` 調査
  - `pyxel-hadegame` の `pyxelhg/bgm/bgm_generator.py` 確認
  - Pyxel Webでも破綻しない鳴らし方を検証
- [ ] メッセージ履歴スクロール
- [ ] ダメージフラッシュ等のアニメーション

## Phase 6: バージョン選択（優先度: 低）

- [ ] バージョン別データテーブル分離（3.6 / 5.2 / 5.4）
- [ ] ゲーム開始時にバージョン選択

## Phase 7: 仕上げ（優先度: 低）

- [ ] タイトル画面
- [ ] ハイスコア保存（JSON）
- [ ] 墓石表示（死因）
- [ ] リプレイ（操作ログ保存・再生）

## 既知のバグ・方針変更対象

- [ ] B ボタン競合: ダッシュ（長押し）とキャンセル（単押し）が離した瞬間に誤発火する場合あり
- [ ] Start長押し依存 / Start+D-pad 斜めは方針変更対象
- [ ] 巻物「remove curse」が全アイテムの呪い解除（原作は装備中のみ）
- [ ] 巻物「sleep」がターンスキップ未実装（メッセージのみ）
- [ ] レプラコーン/ニンフが盗んだ後ワープして消える動作が未実装
- [ ] Xeroc（ミミック）のアイテム擬態が未実装
- [ ] 投擲が斜め方向に未対応
