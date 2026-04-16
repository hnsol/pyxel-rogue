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
- ✅ 主要オーバーレイ（Status / Help / Death）
- ✅ 最小ロジックテスト基盤（Pyxel mock + `python3 -m unittest`）
- ✅ 薄い日英切替基盤（`TextCatalog`, `PYXEL_ROGUE_LANG`, 代表文言・用語）
- ✅ Rogue 5.4 `pickup` オプション相当の自動ピックアップON/OFF
- ✅ 探索済み視界外セルで床上アイテムを表示し、モンスターは非表示にする
- ✅ 投げたアイテムの非ブロッキング飛翔アニメーション
- ✅ ゲーム中の日英切り替え入口（Select補助メニューの Language）

注意: 現行実装は Start+D-pad / X / R / Back を含むが、操作方針は A/B/Start/Select + D-pad 中心に再設計予定。

## Phase 4: ゲームロジック完成（優先度: 高）

目的: Rogue 5.4 のゲームロジックを完成させ、原作と同じ挙動か検証できる状態に近づける。

進め方: ゲームメカニクスは常に Rogue 5.4 C ソースを一次情報にする。各 Phase 4 タスクは、該当する原作ファイル・関数・定数・テーブルの確認、Rogue 5.4 期待値テスト、実装、英語/日本語テストの順で進める。既知バグや忠実度修正は、現状追認テストではなく Rogue 5.4 C ソースに基づく期待値テストを先に追加してから直す。baseline テストは、翻訳層やUI整理で壊れてほしくない現状の保護に使う。

罠・隠し要素の実装では、Rogue 5.4 の `new_level.c`, `passages.c`, `command.c`, `move.c` にある生成頻度、発見率、ターン消費、踏んだ時の効果を明示してから実装する。推測、現代ローグライクの慣習、Rogue2.Official、既存 Pyxel 実装をゲーム挙動の正解にしない。

完了条件: 26階で Amulet of Yendor が出現し、所持したまま1階へ帰還すると勝利できること。指輪・杖・罠・隠し要素が Rogue 5.4 の主要な攻略判断に影響する形で実装され、既知の忠実度バグを baseline として固定せず期待値テストで修正していること。

推奨順:

1. search / 隠しドア / 隠し通路 / 罠
2. 指輪
3. 杖と方向指定 zap
4. Amulet of Yendor / 帰還勝利
5. remove curse, sleep, scare monster, Xeroc, 盗み後ワープ, 迷路部屋などの忠実度バグ

- [ ] **指輪（Ring）14種** — 2スロット（左右手）、常時効果、ランダム宝石名で識別
  - protection, add strength, sustain strength, searching,
    see invisible, adornment, aggravate monster, dexterity,
    increase damage, regeneration, slow digestion, teleportation,
    stealth, maintain armor
- [ ] **杖（Wand/Staff）14種** — チャージ制、方向指定 zap、ランダム素材名で識別
  - light, invisibility, lightning, fire, cold, polymorph,
    missile, haste monster, slow monster, drain life,
    nothing, teleport away, teleport to, cancellation
- [x] **罠（Trap）8種** — 隠れていて search で発見、踏むと発動
  - trap door, arrow, sleeping gas, bear trap,
    teleport, dart, rust, mysterious
- [x] **search コマンド** — Select+B / 補助メニュー / `S` から周囲8マス、A空押しから正面1マスを探索し、罠・隠しドア・隠し通路を発見する hook として整備
- [x] **隠しドア・隠し通路**
- [ ] **Amulet of Yendor** — 26階で出現、1階帰還で勝利
- [ ] 勝利画面 / 勝利状態（Amulet 所持で1階帰還した場合）
- [x] Rogue 5.4 `pick_up()` 準拠の拾得基礎（自動拾得、金直接加算、満杯文言、scare monster 再拾得消滅）
- [ ] `scroll of scare monster` の床上効果（床に置いた巻物でモンスターが怯える挙動）
- [ ] 戦闘計算の精密化（元祖 d20 式の完全再現）
- [ ] モンスター sleeping 状態（部屋入室で起きる）
- [ ] モンスター8方向移動
- [x] 最小 baseline ロジックテスト整備
- [ ] 原作 Rogue 5.4 との照合用期待値テスト拡充

## Phase 5: 移植性・UI基盤（優先度: 中）

- [ ] Pyxel Web 対応確認
- [ ] ブラウザ / SteamDeck / 中華ゲーム機向け入力整理
- [x] 通常8方向移動の整理
- [x] Start短押しによる斜め補助モード / 8方向移動モード（通常モード）のトグル実装
- [x] 斜め補助モード中は左上/右上/右下/左下の同時押しだけを NW/NE/SE/SW として扱い、上下左右単体をOFFにする
- [x] 斜め補助モード中でもメニュー / アイテム選択 / 補助メニューの上下カーソル操作は受け付ける
- [x] 斜め補助モード ON/OFF をステータス欄に表示
- [x] D-pad/矢印の横→斜め入力が横移動+斜め移動に分裂する問題を1フレーム保留で抑制
- [x] B短押しメニュー/キャンセルとB長押しダッシュの競合解消
- [x] B+D-pad run 開始をホールド方向判定にし、B と D-pad の押下順に依存しないよう修正
- [x] メニュー中のB短押しキャンセルを Pyxel Web / SteamDeck Firefox でも直感通りにする
- [x] Rogue 5.4 `do_run()` / `do_move()` / `turn_ok()` 準拠のダッシュ停止・通路角処理へ修正
- [x] Rogue 5.4 `door_stop` 相当の部屋内ダッシュ周囲扉停止
- [x] Rogue 5.4 `diag_ok()` 相当の斜め移動・斜め近接攻撃・モンスター接触制限
- [x] Rogue 5.4 `doctor()` 相当のHP自然回復
- [x] Rogue 5.4 `stomach()` 相当の空腹緩和
- [x] ゲームパッド XYLR / ショルダー依存の撤去（キーボード操作は正式対応として維持）
- [x] Select(Back) の補助メニュー化（旧方針ではMap含む）
- [x] Select(Back) 補助メニューから Map を削除し、Status / Help / Search に整理
- [x] Select+A quick throw / Select+B search を追加
- [x] Rogue 5.4 `^` + 方向相当の Trap Inspect 入力基盤（Select+D-pad / 補助メニュー Trap / Shift+6）
- [x] Assist menu からの日英トグル
- [x] A空押しを正面search、A+Bを足踏み専用として整理
- [x] Rogue 5.4 `passages.c` 準拠の通常部屋通路生成へ修正
- [x] 旧コンパクトレイアウト（512×320化で置き換え予定）
- [x] 512×320 基準レイアウトへ変更
- [x] 48×24メインASCIIマップを常時全表示
- [x] 右サイドHUD（HP/Str/AC/Food/装備/状態異常/入力モード）を追加
- [x] 下ログを画面下部に再配置
- [x] 通常画面のミニマップを廃止
- [x] Selectから開く全体マップUIを廃止
- [ ] 可変画面 / レイアウト再計算
- [x] カメラ追従開始位置の調整
- [ ] 複数 BDF フォント選択 + レイアウト自動再計算
- [x] 日本語/英語切替の入口（`PYXEL_ROGUE_LANG=ja`、代表文言・用語）
- [ ] 日本語/英語切替（全メッセージ辞書化、umplus_j10r は CJK 対応済み）
- [ ] HUD / Status / Help / Death の文言辞書化
- [ ] Phase 4 追加文言（指輪 / 杖 / 罠 / Amulet / 勝利 / search結果）を新規直書きせず `TextCatalog` 経由にする
- [ ] BGM 導入方式検討
  - `8bit-bgm-generator` 調査
  - `pyxel-hadegame` の `pyxelhg/bgm/bgm_generator.py` 確認
  - Pyxel Webでも破綻しない鳴らし方を検証
- [ ] メッセージ履歴スクロール
- [x] 投擲アイテムの飛翔アニメーション
- [ ] ダメージフラッシュ等のアニメーション

## Phase 6: バージョン選択（優先度: 低）

短期的には優先度を下げる。現行ターゲットは Rogue 5.4 に固定し、将来の切替に備えてデータ・文言・ロジックの依存方向だけ整える。

- [ ] バージョン別データテーブル分離（3.6 / 5.2 / 5.4）
- [ ] ゲーム開始時にバージョン選択

## Phase 7: 仕上げ（優先度: 低）

- [ ] タイトル画面
- [x] 死亡画面（墓石/死因/Depth/Level/Gold/Exp/Turn 表示）
- [ ] ハイスコア保存（JSON）
- [ ] スコア履歴画面
- [ ] リプレイ（操作ログ保存・再生）

## 既知のバグ・方針変更対象

- [x] B ボタン競合: ダッシュ（長押し）とキャンセル（単押し）が離した瞬間に誤発火する場合あり
- [x] B短押しで開いたメニューがB短押しで閉じない場合がある
- [x] B+D-pad run が開始しない/開始しにくい場合がある
- [x] ダッシュがドア手前で止まらず、通路角では角のひとつ手前で止まる場合がある
- [x] 部屋内で壁沿いに走ったとき、周囲の扉で停止しない場合がある
- [x] HP自然回復が未実装
- [x] 食料切れ直後からHPが減り続けて辛すぎる
- [x] Start長押し依存 / Start+D-pad 斜めは方針変更対象
- [x] 通路生成が部屋内部や壁沿いに不自然な通路を作る場合がある
- [ ] 巻物「remove curse」が全アイテムの呪い解除（原作は装備中のみ）
- [ ] 巻物「sleep」がターンスキップ未実装（メッセージのみ）
- [ ] 巻物「scare monster」の床上効果が未実装（再拾得消滅のみ実装済み）
- [ ] レプラコーン/ニンフが盗んだ後ワープして消える動作が未実装
- [ ] Xeroc（ミミック）のアイテム擬態が未実装
- [ ] 投擲が斜め方向に未対応
- [ ] 迷路部屋 / gone room は未実装

## テスト・基盤タスク

- [x] `tests/test_rogue_baseline.py` で Pyxel mock による import / 初期化 / ダンジョン到達性 / 初期装備 / 翻訳層 baseline を確認
- [x] `python3 -m unittest` でテストを実行可能にする
- [ ] Rogue2.Official `mesg_J` / `mesg_E` に基づく文言辞書の拡充
- [ ] Rogue 5.4 メッセージ全文監査（今回の拾得・ステータス周辺以外）
- [ ] 英語 / 日本語で同じ seed・操作ならゲーム状態が一致するテストケースを増やす
- [ ] 忠実度修正ごとに Rogue 5.4 期待値テストを追加
