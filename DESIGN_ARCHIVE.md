# DESIGN_ARCHIVE.md — 将来候補と旧方針

この文書は、現在の優先方針ではない設計案を退避する場所。

現在の最優先は `Rogue V5 on Pyxel` として Rogue 5.4.4 のゲームメカニクス忠実化を進めること。表示・入力・学習支援は、その忠実化を妨げない範囲で進める。

## 優先度を大きく下げたもの

- GBC風UI
- 360×240 などの狭い画面対応
- 中華ゲーム機向け最適化
- スマートフォン / タブレット前提のUI
- 可変画面 / 複数レイアウト
- 全体マップオーバーレイ復活
- リプレイ
- バージョン選択

これらは「やらない」と決めたものではなく、Rogue 5.4.4 忠実化と PC / SteamDeck 想定の現UI作り込みが進んだ後に再検討する将来候補とする。

## 旧GBC風UI方針

GBC風UI、GBC寄りパレット、360×240移行、小型ゲーム機最適化は、Pyxel らしい方向性として魅力はある。ただし現時点では優先順位を下げる。

当面は現行の 576×360、80×22 ASCII、右HUD、下ログ、Inventory / Help / Death 画面を PC / SteamDeck で読みやすくすることを優先する。

退避した詳細:

- Ghost Babel 風の右情報寄せ、渋い配色、記号で読ませる画面構成
- 360×240 へ移行し、Steam Deck で3倍整数スケールする案
- GBC 32色パレット案
- Flexoki Dark / GBC High Contrast / Flexoki Light の比較
- モンスター色を危険の質で分類する案
- UI配色を低彩度ベース、危険と操作対象だけ高彩度にする案
- 純白はカーソル、点滅、最重要一時表示に限定する案

## 旧マップUI方針

ミニマップと Select から開く全体マップは廃止済み。全体マップオーバーレイ復活も将来候補へ下げる。

探索情報はメインASCII表示に集約する。別レイヤーの地図UIを足す場合は、Rogue 5.4.4 の探索判断を薄めないかを先に確認する。

退避した詳細:

- 全画面オーバーレイを明示操作時のみ一時表示する案
- 表示範囲は `self.vis` の探索済みセルのみ
- ターン非消費
- 入力候補は Select 長押し、新規 chord、トグル

## 旧バージョン選択方針

Rogue 3.6 / 5.2 / 5.4.4 のバージョン選択は、現時点ではほとんど考えない。

5.4.4 準拠だけでも大きな労力であり、identify scroll 問題はバージョン選択ではなく難易度で扱う。`Normal` は Rogue 5.4.5p `idscrl` 準拠、`Strict 5.4.4` は Rogue 5.4.4 準拠チャレンジとする。

## リプレイ

リプレイは現時点では考えない。

ゲーム中セーブは別枠でやりたい候補として残す。将来、セーブ実装に操作ログや状態保存が必要になった場合だけ、リプレイとの関係を再検討する。

## BGM参照候補

- しろもふさん自動演奏ツール: https://github.com/shiromofufactory/8bit-bgm-generator
- Pyxel組み込み例: https://github.com/hnsol/pyxel-hadegame の `pyxelhg/bgm/bgm_generator.py`

タイトルBGMは実装済み。ゲーム中BGMは将来候補だが、Rogue 5.4.4 忠実化より優先しない。

## 鑑定詳細メモ

`DESIGN.md` から退避した詳細監査メモ:

- Potion の正式鑑定は `potions.c:quaff()` / `do_pot()` の分岐ごとに扱う
- Scroll の正式鑑定は `scrolls.c:read_scroll()` の分岐ごとに扱う
- `P_SEEINVIS`、`P_MFIND`、`P_TFIND` などは効果と正式鑑定が一致しない場合がある
- `S_CONFUSE` / `S_SCARE` / `S_REMOVE` / `S_AGGR` などは効果を出しても `oi_know` を直接立てない
- `scrolls.c:read_scroll()` は効果分岐前に `leave_pack(obj, FALSE, FALSE)` を一度だけ呼ぶ

今後は詳細を `TODO.md`、テスト名、該当実装コメントへ寄せ、`DESIGN.md` は現方針の入口に保つ。

## 操作体系詳細メモ

`DESIGN.md` から退避した詳細:

- B はダッシュ（ホールド）とキャンセル/メニュー（単押し）を兼務する
- ダッシュ開始は `btnp()` ではなく、B ホールド中の現在方向で判定する
- Select は chord レイヤーとして扱う
- B短押しメニューは `rogue_ui.py` の `PAD_ACTION_GRID` で管理する
- キーボードは Pad style と Rogue commands を分ける
- A+B は足踏み専用にし、search を兼ねない
- 自動ピックアップは Rogue 5.4.4 の `pickup` オプション相当
- 斜め入力は1フレーム保留で横移動+斜め移動への分裂を抑える
- ダッシュ/走行は `do_run()`, `do_move()`, `turn_ok()`, `look()` の挙動へ寄せる
- 斜め移動・斜め近接攻撃・モンスター接触攻撃は `diag_ok()` 相当で判定する

## ロジックテスト用 mock 手順

単発検証用の古い Pyxel mock 手順は `tests/test_rogue_baseline.py` に集約済み。通常は `python3 -m unittest` を使う。
