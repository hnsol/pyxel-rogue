# rogue.py 分割候補レポート

## 現状

`rogue.py` は約8,600行で、入口、互換re-export、ゲーム状態、入力、描画、オンラインスコア、Rogue 5.4.4 ロジックの一部が同居している。`pyxel_rogue/` には既に原作寄りの小モジュールが多くあるため、次の分割は新規設計より「既存モジュールへ寄せる」方が安全。

テストは `rogue.Item`, `rogue.Game`, `rogue.RNG`, `rogue.MAP_W` など `rogue.<name>` を広く参照している。分割後もしばらく `rogue.py` は公開窓口としてre-exportを維持する。

2026-05-13時点で、品質方針・プロジェクトルール・低リスク分割の主要部分は完了している。美しさ担保タスク全体では、主要な土台と安全な抽出が進み、残りは中リスク境界の切り出しと文書追従が中心。

## 低リスク候補

1. タイトル・variant補助
   - 対象: `normalize_variant`, `variant_*`, `is_nyandor_cat_item`, タイトル定数、タイトルBGM定数
   - 状態: 完了
   - 移動先: `pyxel_rogue/rogue_variant.py`, `pyxel_rogue/rogue_title.py`

2. メッセージトースト配置
   - 対象: `msg_toast_color`, `msg_toast_home_block`, `pick_msg_toast_block`, `msg_toast_block_origin`
   - 状態: 完了
   - 移動先: `pyxel_rogue/rogue_message_toast.py`

3. UI文言・オンラインUI文言
   - 対象: `TextCatalog`, `ONLINE_UI_TEXT`
   - 状態: 完了
   - 移動先: `pyxel_rogue/rogue_text.py`, `pyxel_rogue/rogue_online_ui.py`

4. HUD表示名・装備表示補助
   - 対象: `hud_equip_name`, `hud_weapon_bonus`, `hud_armor_bonus`, `hud_condition_labels`, `hud_condition_chips`
   - 状態: 完了
   - 移動先: `pyxel_rogue/rogue_hud.py`

## 中リスク候補

1. オンラインスコア画面
   - 対象: `ensure_online_score_state` から `online_result_lines`, `draw_online_*`, `upd_online_*`
   - 候補先: `pyxel_rogue/rogue_online_ui.py`
   - 状態: 一部完了。文言、score期間補助、状態初期値一覧、sync due判定、期間score request状態更新、pending/cancel sync状態遷移、pending action状態遷移、score画面ラベル、score行整形・表示行生成・強調判定、guest local best表示行、結果メッセージ分割、sync overlay文言選択、score期間タブ移動は移動済み。描画、更新、登録処理は未分離
   - 理由: ゲームメカニクス外だが、状態変数が多い。状態名と純粋な整形処理から順に移す

2. dash / repeat / count prefix 入力
   - 対象: `dash_*`, `repeat_*`, `count_*`, `dir_press`, `held_dir`
   - 候補先: `pyxel_rogue/rogue_input.py`
   - 状態: 完了。方向入力、方向プロンプト、ホールド方向、Select+方向、count prefix 数字検出、repeat履歴、count prefix / count repeat状態、B/Select短押し状態、dash状態を移動済み
   - 理由: 入力規約と密接。キー状態から意図への変換、Rogue 5.4.4 `command.c` 由来の入力状態、短押し競合状態、dash継続状態を分け、実コマンド実行とマップ判定はGame側に残す

3. trap / search / movement周辺
   - 対象: `do_search`, `trigger_trap`, `inspect_trap`, `try_move`
   - 候補先: 既存 `rogue_search.py`, `rogue_move.py`
   - 状態: 未着手
   - 理由: Rogue 5.4.4 忠実度に直結。移すなら原作関数名との対応を先に明記する

## 高リスク候補

1. `Game` のターン処理
   - 対象: `end_turn`, daemon/fuse処理, monster runner処理
   - 理由: 状態更新の中心。分割前に期待値テストを増やす

2. ポーション・巻物・杖の効果
   - 対象: `use_pot`, `use_scr`, `zap_stick`, `fire_bolt_from`
   - 理由: Rogue 5.4.4 参照が必須。美化目的だけで動かさない

3. ダンジョン生成
   - 対象: `DGen`, `descend`, `_spawn_*`, `_hide_secret_features`
   - 理由: 既に既存モジュールと密接。忠実度修正と一緒に扱う

## 推奨順

1. オンラインスコア画面は、描画前の表示データ生成と状態遷移を分離済み。以後は登録処理や外部I/Oを触る必要が出た時だけ追加分離する
2. 入力処理はキー解釈、repeat / count 状態、短押し状態、dash状態を分離済み。trap / search / movement は次ブランチで Rogue 5.4.4 参照名をテストまたは設計文書から追える状態にしてから分ける
3. trap / search / movement は Rogue 5.4.4 参照名をテストまたは設計文書から追える状態にしてから分ける
4. 高リスク領域は忠実度修正または仕様確認と同時に扱い、美化目的だけでは動かさない

各段階で `rogue.py` はre-exportを残し、既存テストを壊さない。削除は `tools/check_project_rules.py --unused-report` が空であることを確認してから行う。

## 次の実作業

入力分離として、キー状態から方向・count prefix 数字を読む純粋関数、repeat / count 状態、短押し状態、dash状態を `rogue_input.py` へ移した。この入力分離束はここで区切る。次に進むなら、trap / search / movement を別束で扱う。

完了条件:

- 入力規約に沿った期待値テストが先にある
- wrapper比較だけのテストを増やさない
- 既存のオンラインスコアテストが通る
- `tools/check_project_rules.py`, `uvx ruff check .`, 通常/日本語 unittest が通る
