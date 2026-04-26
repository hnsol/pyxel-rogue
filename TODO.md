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
- ✅ 主要オーバーレイ（Inventory / Help / Death）
- ✅ 最小ロジックテスト基盤（Pyxel mock + `python3 -m unittest`）
- ✅ 薄い日英切替基盤（`TextCatalog`, `PYXEL_ROGUE_LANG`, 代表文言・用語）
- ✅ Rogue 5.4.4 `pickup` オプション相当の自動ピックアップON/OFF
- ✅ 探索済み視界外セルで床上アイテムを表示し、モンスターは非表示にする
- ✅ 投げたアイテムの非ブロッキング飛翔アニメーション
- ✅ ゲーム中の日英切り替え入口（Select補助メニューの Language）
- ✅ Rogue 5.4.4 / Pyxel 固有ログの JSON メッセージカタログ化（`assets/messages/*.json`）
- ✅ Rogue 5.4.4 `chase.c` / `monsters.c` / `fight.c` 寄りのモンスターAI基礎（running、起床、扉接近、R/I特殊攻撃、飛行追加移動）

注意: 現行実装は Start+D-pad / X / R / Back を含むが、操作方針は A/B/Start/Select + D-pad 中心に再設計予定。

## Phase 4: ゲームロジック完成（優先度: 高）

目的: Rogue 5.4.4 のゲームロジックを完成させ、原作と同じ挙動か検証できる状態に近づける。

進め方: ゲームメカニクスは常に Rogue 5.4.4 C ソースを一次情報にする。各 Phase 4 タスクは、該当する原作ファイル・関数・定数・テーブルの確認、Rogue 5.4.4 期待値テスト、実装、英語/日本語テストの順で進める。既知バグや忠実度修正は、現状追認テストではなく Rogue 5.4.4 C ソースに基づく期待値テストを先に追加してから直す。baseline テストは、翻訳層やUI整理で壊れてほしくない現状の保護に使う。

罠・隠し要素の実装では、Rogue 5.4.4 の `new_level.c`, `passages.c`, `command.c`, `move.c` にある生成頻度、発見率、ターン消費、踏んだ時の効果を明示してから実装する。推測、現代ローグライクの慣習、Rogue2.Official、既存 Pyxel 実装をゲーム挙動の正解にしない。

完了条件: 26階で Amulet of Yendor が出現し、所持したまま1階へ帰還すると勝利できること。指輪・杖・罠・隠し要素が Rogue 5.4.4 の主要な攻略判断に影響する形で実装され、既知の忠実度バグを baseline として固定せず期待値テストで修正していること。

推奨順:

1. wandering monster spawn（`daemons.c:swander()` / `rollwand()`, `monsters.c:wanderer()`）
2. armor `wear()` の take off 必須化（`armor.c:wear()`）
3. 呪い生成確率と識別表示の監査（`things.c:new_thing()`, `armor.c:wear()`, `rings.c:ring_num()`, `sticks.c:charge_str()`）
4. run停止条件の再監査（`move.c:do_run()` / `do_move()`, `misc.c:look()`）
5. 杖 bolt 系 / magic missile / drain life / nothing（`sticks.c:do_zap()`）
6. 鑑定・命名・発見リスト忠実度（`wizard.c:whatis()/set_know()`, `command.c:call()`, `misc.c:call_it()`, `things.c:print_disc()`）
7. 通路番号付き passages、Dragon breath / cancellation 連携、Xeroc 擬態細部

- [x] **指輪（Ring）14種** — 2スロット（左右手）、常時効果、ランダム宝石名で識別
  - protection, add strength, sustain strength, searching,
    see invisible, adornment, aggravate monster, dexterity,
    increase damage, regeneration, slow digestion, teleportation,
    stealth, maintain armor
  - [x] `rogue_rings.py` に Pyxel 非依存の Rogue 5.4.4 指輪テーブル、石名シャッフル、生成時の補正/呪い、装備/解除、食料消費を分離
  - [x] インベントリ表示、左右2スロット装備、呪いによる remove 制限、`remove curse` の装備中指輪解除
  - [x] protection / add strength / dexterity / increase damage / slow digestion / regeneration の数値効果を接続
  - [x] searching / see invisible / aggravate monster / teleportation / stealth / maintain armor の効果接続
  - [x] sustain strength / adornment の識別・周辺挙動監査
- [x] **杖（Wand/Staff）14種** — チャージ制、方向指定 zap、ランダム素材名で識別
  - light, invisibility, lightning, fire, cold, polymorph,
    missile, haste monster, slow monster, drain life,
    nothing, teleport away, teleport to, cancellation
  - [x] `rogue_sticks.py` に Pyxel 非依存の Rogue 5.4.4 杖テーブル、wand/staff 素材名、生成時チャージ、基礎ダメージ、識別名を分離
  - [x] アイテム生成の stick 4% 枠、インベントリ名、Zap メニュー、方向指定入口、チャージ消費を接続
  - [x] light の暗い部屋照明、識別、チャージ消費を接続
  - [x] invisibility / polymorph / teleport away / teleport to / cancellation の単体モンスター効果接続
  - [x] Rogue 5.4.4 `sticks.c:do_zap()` `WS_POLYMORPH` 準拠で、polymorph 後も monster pack を保持
  - [x] Rogue 5.4.4 `sticks.c:do_zap()` `WS_POLYMORPH` 準拠で、polymorph 後の monster が見えている時だけ識別
  - [x] Rogue 5.4.4 `sticks.c:do_zap()` `WS_POLYMORPH` 識別条件を `rogue_sticks.py` へ小分割
  - [x] lightning / fire / cold の bolt 反射・命中・ダメージ接続
  - [x] haste monster / slow monster の `ISHASTE` / `ISSLOW` 相当フラグと行動頻度への接続
  - [x] magic missile / drain life / nothing の効果監査と接続
  - [x] Rogue 5.4.4 `sticks.c:WS_MISSILE` / `fight.c:roll_em()` 準拠で、現在武器の `o_dplus` を magic missile damage に加算
  - [x] Rogue 5.4.4 `sticks.c:WS_MISSILE` / `fight.c:roll_em()` の magic missile damage を `rogue_sticks.py` へ小分割
  - [x] Rogue 5.4.4 `sticks.c:drain()` 準拠で、通路内 drain life 対象を隣接限定にしない
  - [x] Rogue 5.4.4 `sticks.c:drain()` の HP半減/対象割りを `rogue_sticks.py` へ小分割
  - [x] Rogue 5.4.4 `sticks.c:WS_TELTO` の `hero + delta` 転移先計算を `rogue_sticks.py` へ小分割
  - [x] Rogue 5.4.4 `sticks.c:WS_LIGHT` 準拠で、既に明るい部屋でも room-lit branch にする
  - [x] Rogue 5.4.4 `sticks.c:WS_LIGHT` の room/gone branch 判定を `rogue_sticks.py` へ小分割
- [x] **罠（Trap）8種** — 隠れていて search で発見、踏むと発動
  - trap door, arrow, sleeping gas, bear trap,
    teleport, dart, rust, mysterious
- [x] **search コマンド** — Select+A / 補助メニュー / `S` から周囲8マス、A空押しから正面1マスを探索し、罠・隠しドア・隠し通路を発見する hook として整備
- [x] **隠しドア・隠し通路**
- [x] **Amulet of Yendor** — 26階で出現、1階帰還で勝利
- [x] 勝利画面 / 勝利状態（Amulet 所持で1階帰還した場合）
- [x] Rogue 5.4.4 `pick_up()` 準拠の拾得基礎（自動拾得、金直接加算、満杯文言、scare monster 再拾得消滅）
- [x] `scroll of scare monster` の床上効果（床に置いた巻物でモンスターが踏み込まない挙動）
- [x] Rogue 5.4.4 `daemons.c:swander()` / `rollwand()` と `monsters.c:wanderer()` 準拠の wandering monster spawn
- [x] Rogue 5.4.4 `armor.c:wear()` 準拠の armor 装備中 wear 拒否（take off 必須）
- [x] Rogue 5.4.4 `things.c:new_thing()` 準拠の呪い生成確率監査（weapon 10%、armor 20%、一部 ring 33%、aggravate/teleport 常時 cursed）
- [x] Rogue 5.4.4 `things.c:new_thing()` / `pick_one()` 相当の food 90/10・カテゴリ重み・potion/weapon/armor 種類重み・weapon/armor enchant 分岐を helper 化
- [x] Rogue 5.4.4 `new_level.c:new_level()` / `put_things()` 相当の `no_food` 強制 food、`MAXOBJ=9` × 36% 物資生成、Amulet 上昇中の物資生成停止を helper 化
- [x] Rogue 5.4.4 `rooms.c:do_rooms()` 相当の room gold、部屋モンスター発生、gone/dark/maze room 選択を helper 化
- [x] Rogue 5.4.4 `fight.c:killed()` 相当の Leprechaun 死亡時 gold drop を helper 化
- [x] Rogue 5.4.4 `monsters.c:new_monster()` / `exp_add()` 相当の Amulet 階層以深モンスター生成 stat/EXP 補正と深層 `ISHASTE` を helper 化
- [x] Rogue 5.4.4 `new_level.c` / `passages.c` / `command.c:search()` / `move.c:be_trapped()` 相当の trap・secret・search・単純trap状態分岐を helper 化
- [x] Rogue 5.4.4 `pack.c:add_pack()` / `pack_room()` 相当の scare monster scroll 拾得消滅と満杯時スタック拒否を helper 化
- [x] 生成時 curse / enchant の非可視性と装備時 `ISKNOW` 相当の識別表示監査
- [x] Rogue 5.4.4 `move.c:do_run()` / `do_move()` と `misc.c:look()` 準拠の run 停止条件再監査
- [x] Rogue 5.4.4 `passages.c` 準拠の浅い階の通路グラフ・余剰エッジ数の固定 seed 監査
- [x] **鑑定・命名・発見リスト忠実度**
  - [x] `IdentTable` に `pg/sg/rg/wg`（型レベル `oi_guess` 相当）追加、`Item` に `o_flags`/`o_label` 追加、`known` を `FLAG_ISKNOW` property 化
  - [x] `things.c:inv_name()/nameit()` 準拠の3層表示（`oi_know` → `oi_guess` → appearance）をポーション/巻物/指輪/杖に実装
  - [x] `wizard.c:whatis()/set_know()` 準拠の対象選択式 identify 実装（`item_confirm()` に "Identify" ブランチ）
  - [x] ring の `ring_num()` と stick の `charge_str()` は種類判明だけでなく個体 `ISKNOW` 後に表示する
  - [x] `command.c:call()` / `misc.c:call_it()` 相当の命名機能（`c` キー）— potion / scroll / ring / stick の `oi_guess` を設定
  - [x] `things.c:print_disc()` 相当の discovered list（`D` キー）— `oi_know`/`oi_guess` 一覧表示
  - [x] `command.c:call()` の weapon / armor 個体ラベル（`o_label`）接続
  - [x] `potions.c:quaff()/do_pot()` 準拠で、使用時に正式判明する/しない potion を分ける
  - [x] `scrolls.c:read_scroll()` 準拠で、使用時に正式判明する/しない scroll を分ける
- [ ] 戦闘計算の精密化（元祖 d20 式の完全再現）
- [x] Rogue 5.4.4 `fight.c:swing()` 相当の d20 命中判定を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `move.c:be_trapped()` / `fight.c:swing()` 準拠の arrow/dart trap 命中式監査（装備中 armor ではなく `pstats.s_arm` を使う）
- [x] モンスター running / 起床の基礎（視界内 mean monster、攻撃時 `runto()`、aggravate）
- [x] Rogue 5.4.4 `extern.c:monsters[]` 準拠で、`ISMEAN` 相当flagsをBESTIARYへ反映
- [x] Rogue 5.4.4 `monsters.c:new_monster()` 準拠で、polymorph 後の `ISMEAN` を新monster specから復元
- [x] Rogue 5.4.4 `extern.c:monsters[]` / `chase.c:do_chase()` 準拠で、Orc `ISGREED` と Leprechaun 金盗みを分離
- [x] Rogue 5.4.4 `extern.c:monsters[]` flags parsing を `rogue_monsters.py` へ小分割
- [x] Rogue 5.4.4 `new_level.c:treas_room()` の treasure room 強制 `ISMEAN` を `rogue_monsters.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` の `!ISCANC` special gate を `rogue_monsters.has_special()` へ寄せる
- [x] Rogue 5.4.4 `ISREGEN` の `ISCANC` gate も `rogue_monsters.has_special()` へ寄せる
- [x] Rogue 5.4.4 `rogue.h:ISGREED` / `monsters.c:wanderer()` / `chase.c:do_chase()` の gold 守備フラグを `rogue_monsters.is_greedy()` へ小分割
- [x] Rogue 5.4.4 `sticks.c:WS_CANCEL` の monster flag / disguise 更新を `rogue_monsters.cancel_monster()` へ小分割
- [x] Rogue 5.4.4 `chase.c:runners()` 相当の起床済みモンスター実行ゲートを `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:runners()` 相当の飛行モンスター追加移動を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `rogue.h:ISFLY` の飛行判定を `rogue_monsters.is_flying()` へ小分割
- [x] Rogue 5.4.4 `rogue.h:ISINVIS` の不可視判定を `rogue_monsters.is_invisible()` へ小分割
- [x] Rogue 5.4.4 `sticks.c:WS_INVIS` の `ISINVIS` 付与を `rogue_monsters.make_invisible()` へ小分割
- [x] Rogue 5.4.4 `monsters.c:wake_monster()` の Medusa gaze gate を `rogue_monsters.medusa_gaze_active()` へ小分割
- [x] Rogue 5.4.4 `monsters.c:wake_monster()` 準拠で hallucination 中は Medusa gaze を受けない
- [x] Rogue 5.4.4 `monsters.c:wake_monster()` 準拠で levitation 中は mean monster が起床しない
- [x] Rogue 5.4.4 `monsters.c:new_monster()` の深層 `ISHASTE` 付与を `rogue_monsters.apply_deep_haste()` へ小分割
- [x] Rogue 5.4.4 `chase.c:runners()` 準拠で、`ISTARGET` モンスターが移動したら target を解除
- [x] Rogue 5.4.4 `chase.c:runners()` 準拠で、`move_monst() == -1` 時は飛行追加移動をしない
- [x] Rogue 5.4.4 `chase.c:move_monst()` 相当の速度ステップ実行を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:move_monst()` 準拠で、held gate は `runners()` 側に限定
- [x] Rogue 5.4.4 `chase.c:runto()` 相当の追跡開始を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:diag_ok()` 相当の斜め移動可否を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:dist()` / `dist_cp()` 相当の二乗距離を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:roomin()` 相当の部屋矩形判定を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:see_monst()` / `cansee()` 相当の盲目/不可視、lamp距離、斜め遮蔽、同室照明ゲートを `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:find_dest()` 相当の carry 目的地選択を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:do_chase()` 相当の Dragon flame gate / 最寄り出口 / greedy 目的地補正 / chasee room 選択を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` 準拠で、door 上の hero は bolt 反射ではなく命中判定にする
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` 準拠で、saved monster miss の `runto()` は hero 発射時だけにする
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` 準拠で、擬態中 Xeroc の saved monster miss は表示/追跡しない
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` / `rip.c` 準拠で、hero 自身の反射 bolt 死亡原因を `bolt` にする
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` saved monster miss の表示/追跡分岐を `rogue_sticks.py` へ小分割
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` / `rip.c` の bolt 死亡原因分岐を `rogue_sticks.py` へ小分割
- [x] Rogue 5.4.4 `sticks.c:fire_bolt()` の DOOR 上 hero 反射例外を `rogue_sticks.py` へ小分割
- [x] Rogue 5.4.4 `chase.c:chase()` 相当の confused / Phantom / Bat ランダム移動ゲート、混乱解除、候補ゲート、距離/tie選択、戻り値条件を `rogue_chase.py` へ小分割
- [x] Rogue 5.4.4 `monsters.c:save_throw()` / `save()` 相当の player/monster セーヴ式と protection ring 補正を helper 化
- [x] Rogue 5.4.4 `move.c:rndmove()` 相当の1回だけのランダム移動試行を `rogue_move.py` へ小分割
- [x] Rogue 5.4.4 `move.c:rust_armor()` 相当の錆び合法判定・保護分岐を `rogue_move.py` へ小分割
- [x] Rogue 5.4.4 `move.c:be_trapped()` `T_MYST` 11択メッセージ表を `rogue_move.py` へ小分割
- [x] モンスター8方向移動（`chase.c` 相当の周囲8マス候補選択、`diag_ok()`、扉回り込み）
- [x] モンスター `ISHASTE` / `ISSLOW` / `ISCANC` 相当の状態土台（速度行動頻度、Medusa視線・特殊攻撃・再生抑止）
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Nymph 盗み対象選択監査（装備品除外 + `rnd(++nobj)==0`）
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Nymph 盗み対象選択を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` / `rogue.h:GOLDCALC` 準拠の Leprechaun 金盗み式監査
- [x] Rogue 5.4.4 `rogue.h:GOLDCALC` 相当の金額ロールを `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Leprechaun 金額減算回数を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:roll_em()` 相当のダメージ式ロールを `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:roll_em()` 相当の部位ごとの命中/ダメージ加算を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:roll_em()` 相当の defender `!ISRUN` 命中補正を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:roll_em()` 相当の weapon/hurl profile 選択を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `extern.c:INIT_STATS` 準拠で、プレイヤー素手ダメージを `"1x4"` に修正
- [x] Rogue 5.4.4 `extern.c:INIT_STATS` 準拠で、プレイヤー初期 HP / max HP を 12 に修正
- [x] Rogue 5.4.4 `init.c:init_player()` 準拠で、初期pack順・+1 ring mail・矢数 `rnd(15)+25` を修正
- [x] Rogue 5.4.4 `init.c:init_player()` の初期pack生成を `rogue_init.py` へ小分割
- [x] Rogue 5.4.4 `weapons.c:init_dam[]` 準拠で、武器ダメージ表を `%dx%d` 表記へ統一
- [x] Rogue 5.4.4 `weapons.c:init_dam[]` を `rogue_weapons.py` へ小分割
- [x] Rogue 5.4.4 `weapons.c:fall()` / `fallpos()` / `init_weapon()` 相当の投擲落下・初期個数 helper を `rogue_weapons.py` へ小分割し、`fallpos()` 選択乱数を `RNG.rnd()` へ統一
- [x] Rogue 5.4.4 `things.c:new_thing()` 準拠で、weapon curse/enchant/初期個数乱数を `RNG.rnd()` へ統一
- [x] Rogue 5.4.4 `fight.c:str_plus[]` / `add_dam[]` 相当の Strength 補正を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Ice monster freeze `no_command += rnd(2)+2` を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Venus Flytrap `vf_hit` 加算を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Venus Flytrap miss 時 `vf_hit` ダメージを `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Rattlesnake poison Strength 低下判定を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Wraith level drain を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Vampire max HP drain を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 相当の Wraith/Vampire drain 発動率を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:killed()` 相当の Venus Flytrap hold 解除を `rogue_fight.py` へ小分割
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Leprechaun purse 0 hit 消滅監査
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Wraith レベルドレイン経験値監査（`e_levels[s_lvl-1]+1`）
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Wraith level 1 drain 経験値監査（`--s_lvl==0`）
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Wraith exp 0 drain 死亡監査（`death('W')`）
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Wraith max_hp drain 死亡監査（`death('W')`）
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Vampire max_hp drain 死亡監査（`death('V')`）
- [x] Rattlesnake / Ice monster の Rogue 5.4.4 準拠寄せ（毒セーヴによるStr低下、命中時凍結）
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Rattlesnake sustain strength save 順序監査
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Rattlesnake sustain strength メッセージ監査
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Rattlesnake 毒低下メッセージ監査
- [x] Rogue 5.4.4 `fight.c:attack()` 準拠の Ice monster freeze メッセージ再表示監査
- [x] Rogue 5.4.4 `move.c:T_DART` 準拠の dart trap poison save 順序監査
- [x] Rogue 5.4.4 `misc.c:add_str()` 準拠の poison potion Strength 下限監査
- [x] Rogue 5.4.4 `potions.c:quaff()` / `misc.c:add_str()` 準拠の potion Strength / healing / extra healing helper 化
- [x] Rogue 5.4.4 `potions.c:raise_level()` / `misc.c:check_level()` 準拠の経験値閾値・d10 HP 増加 helper 化
- [x] Rogue 5.4.4 `misc.c:eat()` 準拠で、ration の good/awful 分岐と slime-mold 文言を `rogue_food.py` へ小分割して接続
- [x] 最小 baseline ロジックテスト整備
- [x] Rogue 5.4.4 `extern.c:monsters[]` / `fight.c:swing` 準拠の戦闘値監査テスト追加
- [ ] 原作 Rogue 5.4.4 との照合用期待値テスト拡充
- [x] **巻物 18種化**（`rogue.h:S_* / MAXSCROLLS=18`、`scrolls.c:read_scroll()`）
  - [x] `S_CONFUSE` monster confusion（次攻撃時にモンスター混乱、`your hands begin to glow red`）
  - [x] `S_ID_POTION` / `S_ID_SCROLL` / `S_ID_WEAPON` / `S_ID_ARMOR` / `S_ID_R_OR_S` の識別分化（インタラクティブ対象選択 UI 実装済み、`wizard.c:whatis()` 準拠）
  - [x] `S_FDET` food detection（階フロアの食料位置一時表示）
  - [x] `S_PROTECT` protect armor（防具の呪い・錆び防止）と現行 enchant armor (= `S_ARMOR`) の区別
- [x] **ポーション 14種化**（`rogue.h:P_* / MAXPOTIONS=14`、`potions.c:quaff()`）
  - 現行 Pyxel 版は 14 種実装済み。
  - [x] `P_LSD` hallucination の効果実装（視覚混乱、search `probinc`、invisible monster 表示への反映）
  - [x] `P_LEVIT` levitation（`ISLEVIT` 相当、罠・階段無効化、床上アイテム拾得不可、`daemons.c:land()` で復帰）
- [x] **treasure room（俗称モンスターハウス）**（`new_level.c:138, 180-231` の `treas_room()`）
  - 1/20 の階で発生。`MINTREAS=2` / `MAXTREAS=10` のアイテムと、次階層相当のモンスター群を `ISMEAN` 付きで配置。部屋内モンスターには `give_pack()` も呼ぶ。
- [x] **モンスター持ち物 `m_carry`**（`monsters.c:217-222 give_pack()`、`extern.c:monsters[]` の `m_carry`）
  - `level >= max_level && rnd(100) < m_carry` でモンスターに `new_thing()` を持たせ、倒した時にドロップさせる。
- [ ] **daemon / fuse 期間管理インフラ**（`daemon.c`, `daemons.c`, `main.c:fuse()/lengthen()/extinguish()`）
  - `doctor / stomach / runners / swander / rollwand / sight / unsee / unconfuse / unblind / unhaste / unring / land / nohaste` などを個別タイマーではなく統一インフラで扱い、`potion of haste self` 等の残ターン管理を Rogue 5.4.4 準拠にする。
  - [x] `rogue_daemons.py` に `fuse` / `lengthen` / `extinguish` / `do_fuses(AFTER)` 相当を分離し、`potion of haste self` の `nohaste` と二重使用時の失神へ接続
  - [x] `see invisible` potion の `unsee` を `fuse` / `lengthen` / `do_fuses(AFTER)` へ接続
  - [x] `hallucination` potion の `come_down` を `fuse` / `lengthen` / `do_fuses(AFTER)` へ接続
  - [x] `levitation` potion の `land` を `fuse` / `lengthen` / `do_fuses(AFTER)` へ接続
  - [x] `confusion` potion の `unconfuse` と `blindness` potion の `sight` を `fuse` / `lengthen` / `do_fuses(AFTER)` へ接続
  - [x] `monster detection` potion の `turn_see` を `fuse` / `lengthen` / `do_fuses(AFTER)` へ接続
  - [x] Rogue 5.4.4 `potions.c:P_MFIND` 準拠で、再使用時も `turn_see` は `lengthen()` せず重複 `fuse()` にする
  - [x] `swander / rollwand` を初回 `fuse(AFTER)`、以後 `start_daemon(BEFORE)` / `fuse(BEFORE)` へ接続
  - [x] `doctor / stomach` を `start_daemon(AFTER)` へ接続
  - [x] `runners` を `start_daemon(AFTER)` へ接続
  - [x] `daemon.c` 準拠で delayed action を unique map ではなく共通スロット列として扱い、daemon/fuse 合計 `MAXDAEMONS=20`、同名 daemon/fuse の重複登録、`kill_daemon()` / `extinguish()` の先頭1件削除を再現
  - [x] `daemons.c:doctor()` / `stomach()` 相当の純ロジックを `rogue_daemons.py` へ小分割し、`Game` / `Player` 側から委譲
  - [x] Rogue 5.4.4 `daemons.c:stomach()` 準拠で、餓死判定時の `food_left--` を helper に反映
  - [x] Rogue 5.4.4 `daemons.c:stomach()` 準拠で、faint 判定を `randrange(5)` ではなく `rnd(5)` に統一
  - [x] `daemons.c:swander()` / `rollwand()` 相当の wandering daemon ロジックを `rogue_daemons.py` へ小分割し、`Game` 側から委譲
  - [x] Rogue 5.4.4 `daemons.c:sight()` 準拠で、healing / extra healing / see invisible の blind 解除時に `sight` fuse を消す
  - [x] Rogue 5.4.4 `daemon.c:do_daemons()` / `do_fuses()` 準拠で、daemon/fuse を due list 後処理ではなく slot順の即時dispatchへ寄せる
  - [x] Rogue 5.4.4 `daemons.c:stomach()` の hungry_state 変化run停止と `misc.c:add_haste()` の nohaste 期間を helper 化
  - [ ] `doctor / stomach / runners / swander / rollwand` など daemon 系を統一インフラへ段階移行

## Phase 5: 移植性・UI基盤（優先度: 中）

- [x] Pyxel Web 対応確認
  - [x] Web Launcher で確認する開発branch名は `/` なしにする（`codex/...` は path と誤解される場合あり）
- [ ] ブラウザ / SteamDeck / 中華ゲーム機向け入力整理
- [x] 通常8方向移動の整理
- [x] Start短押しによる斜め補助モード / 8方向移動モード（通常モード）のトグル実装
- [x] 斜め補助モード中は左上/右上/右下/左下の同時押しだけを NW/NE/SE/SW として扱い、上下左右単体をOFFにする
- [x] 斜め補助モード中でもメニュー / アイテム選択 / 補助メニューの上下カーソル操作は受け付ける
- [x] 斜め補助モード ON/OFF をステータス欄に表示
- [x] D-pad/矢印の横→斜め入力が横移動+斜め移動に分裂する問題を1フレーム保留で抑制
- [x] B短押しメニュー/キャンセルとB長押しダッシュの競合解消
- [x] キーボードでも A/B/Select/Start 相当の最低限操作（Enter, Esc, Tab, Space）を割り当てる
- [ ] pyxapp / 中華ゲーム機向けの Pyxel 終了方法追加（セーブ / システム系インタフェースで扱う）
- [x] Rogue V5 直打ちキーボードショートカット基礎（`t/q/r/e/w/W/T/i/?/s/^/z`。既存メニュー項目への入口として実装し、プレイ中だけ発火）
- [x] Rogue V5 `P` put on ring の直打ち入力を追加する。`c` call は実装済み。英字キーは原作コマンドを優先するため、Pad style では使わない。
- [ ] Item overlay で `a-z` のアイテム letter 直接選択を追加する。プレイ中の Rogue commands とは別レイヤーとして扱い、overlay 中は文字コマンドを発火させない。
- [x] B+D-pad run 開始をホールド方向判定にし、B と D-pad の押下順に依存しないよう修正
- [x] メニュー中のB短押しキャンセルを Pyxel Web / SteamDeck Firefox でも直感通りにする
- [x] Rogue 5.4.4 `do_run()` / `do_move()` / `turn_ok()` 準拠のダッシュ停止・通路角処理へ修正
- [x] Rogue 5.4.4 `door_stop` 相当の部屋内ダッシュ周囲扉停止
- [x] Rogue 5.4.4 `diag_ok()` 相当の斜め移動・斜め近接攻撃・モンスター接触制限
- [x] Rogue 5.4.4 `doctor()` 相当のHP自然回復
- [x] Rogue 5.4.4 `stomach()` 相当の空腹緩和
- [x] ゲームパッド XYLR / ショルダー依存の撤去（キーボード操作は正式対応として維持）
- [x] Select(Back) の補助メニュー化（旧方針ではMap含む）
- [x] Select(Back) 補助メニューから Map と Status を削除し、Inventory / Help / Search に整理
- [x] Select+A search / Select+B quick throw を追加
- [x] Rogue 5.4.4 `^` + 方向相当の Trap Inspect 入力基盤（Select+D-pad / Tab+方向 / 補助メニュー Trap / `^` then direction）
- [x] Assist menu からの日英トグル
- [x] A空押しを正面search、A+Bを足踏み専用として整理
- [x] Rogue 5.4.4 `passages.c` 準拠の通常部屋通路生成へ修正
- [x] 旧コンパクトレイアウト（512×320化で置き換え済み）
- [x] 512×320 基準レイアウトへ変更（旧方針。80桁化で暫定640×320へ移行）
- [x] 内部論理マップを Rogue 5.4.4 準拠の 80×24 座標系へ変更
- [x] 地形・通路・部屋・プレイヤー移動領域を `x=0..79`, `y=1..22` へ制限
- [x] 80×22メインASCIIマップを576×360の16:10寄りレイアウトで表示
- [x] 右サイドHUD（HP/Str/AC/Food/装備/状態異常/入力モード）を追加
- [x] 右HUDの Rogue V5 表記へテストプレイ用改訂スタンプを追加
- [x] HP被ダメージバーをフレームタイマーではなく現在ターン中に残す
- [x] 下ログを画面下部に再配置し7行表示へ拡張
- [x] 通常画面のミニマップを廃止
- [x] Selectから開く全体マップUIを廃止
- [ ] 可変画面 / レイアウト再計算
- [x] **設定オブジェクト導入**
  - 言語、自動拾い、パレット、run 中間表示、レイアウト候補などを `Game` 内の個別フラグから段階的に集約する。
  - 当面は開発・テストプレイ用の切替基盤とし、ゲームメカニクスに影響する設定は持たせない。
- [ ] **開発用オプション基盤**
  - 起動時オプションまたはゲーム中オプションから、テストプレイ用の表示・入力補助設定を切り替えられるようにする。
  - run 中の移動過程を表示するか、非ブロッキング演出をどこまで見せるかなど、同じ操作列でゲーム状態が変わらない項目だけを対象にする。
  - 最終版では検証済みのベスト設定へ固定し、ユーザーに見せるオプションを最小限に絞る。
- [x] 80桁表示、右HUD、下ログを 576×360 / Pyxel Web / 携帯機向けに再調整
- [x] カメラ追従開始位置の調整
- [ ] 複数 BDF フォント選択 + レイアウト自動再計算
- [x] 日本語/英語切替の入口（`PYXEL_ROGUE_LANG=ja`、代表文言・用語）
- [x] Rogue2.Official `mesg_J` / `mesg_E` / `COPYING` を参考データとして `vendor/rogue2_official_messages/` に保持
- [x] HUD短縮名を `TextCatalog.hud_item_kind()` 経由にする
- [x] 日本語/英語切替（ゲームログ / 補助メニュー / 罠名を JSON カタログ化、umplus_j10r は CJK 対応済み）
- [ ] HUD / Inventory / Help / Death の文言辞書化
- [x] Phase 4 追加文言（指輪 / 杖 / 罠 / Amulet / 勝利 / search結果）を新規直書きせず `TextCatalog` 経由にする
- [ ] BGM 導入方式検討
  - `8bit-bgm-generator` 調査
  - `pyxel-hadegame` の `pyxelhg/bgm/bgm_generator.py` 確認
  - Pyxel Webでも破綻しない鳴らし方を検証
- [ ] メッセージ履歴スクロール
- [x] 投擲アイテムの飛翔アニメーション
- [ ] ダメージフラッシュ等のアニメーション
- [ ] GBC風インタフェース刷新（着手条件: Rogue 5.4.4 再現 Phase 4 完了後。詳細は `DESIGN.md` の「将来方針：GBC 美学寄せと 360x240 移行」参照）
  - [ ] 解像度 576×360 → 360×240 移行（80×24 論理座標を維持したままタイル寸法・右HUD幅・下ログ行数を再計算。`可変画面 / レイアウト再計算` の完了が前提）
  - [x] GBC寄りの32色パレット策定・実装（青灰/緑/琥珀/シアン、警告時のみ赤。`GBC_PALETTE` 定数として `rogue.py` に実装済み）
  - [x] 複数パレット定義（3候補）
    - 現行GBC寄り、高コントラスト、Flexoki Light風をデータとして用意し、テストプレイで可読性を比較する。
    - ゲーム中オプションで切り替えられるようにする。
    - 最終的にはベストな1候補へ絞り、ユーザー選択肢として大量に残さない。
  - [ ] マップ全画面オーバーレイ（明示操作時のみ、`self.vis` 準拠で探索済みのみ表示、ターン消費なし）
    - [ ] 入力割当決定（Select長押し / 新規 chord / トグル のいずれか。B長押し+D-padはダッシュで使用中、Start長押しは禁止）
    - [ ] 未探索セルの扱い決定（完全非表示 / 輪郭のみ薄く）
  - [ ] 8bit BGM Generator 導入方針確定（階層ごと固定シード or 毎回ランダム。上記 `BGM 導入方式検討` と合わせて進める）

## Phase 6: バージョン選択（優先度: 低）

短期的には優先度を下げる。現行ターゲットは Rogue 5.4.4 に固定し、将来の Rogue V5 系を含む切替に備えてデータ・文言・ロジックの依存方向だけ整える。

- [ ] バージョン別データテーブル分離（3.6 / 5.2 / 5.4）
- [ ] ゲーム開始時にバージョン選択

## Phase 7: 仕上げ（優先度: 低）

- [ ] タイトル画面
- [x] 死亡画面（墓石/死因/Depth/Level/Gold/Exp/Turn 表示）
- [x] ハイスコア保存（JSON）
- [x] 死亡 / 勝利 / quit 後の Top 10 表示
- [ ] スコア履歴画面
- [ ] リプレイ（操作ログ保存・再生）
- [ ] **Wizard モード**（`wizard.c` / `command.c` の `+` トグル、CTRL-D/A/F/T/E/C/X/~/I 等）— 忠実度監査・バグ再現の検証用途。Pyxel版での入力割当は実装時に検討。
- [ ] **ゲーム中セーブ (`S` コマンド)**（`save.c:save_game()/restore()`）— リプレイとは別枠。Pyxel Web での永続化方式（localStorage 等）は実装時に検討。

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
- [x] 巻物「remove curse」は装備中 weapon / armor / ring のみ呪い解除（原作 `scrolls.c:S_REMOVE` 準拠。全アイテム解除ではない）
- [x] 巻物「sleep」がターンスキップする
- [x] 巻物「scare monster」の床上効果（再拾得消滅に加えて、床上巻物へモンスターが踏み込まない）
- [x] レプラコーン/ニンフが盗んだ後に消える
- [x] Xeroc（ミミック）のアイテム擬態基礎（`monsters.c:new_monster()` / `fight.c:attack()` / `sticks.c:WS_CANCEL` 準拠）
- [x] wandering monster spawn が未実装
- [x] armor 装備中に別 armor を wear できてしまう（原作は take off 必須）
- [x] weapon / armor / ring の呪い生成確率が Rogue 5.4.4 `things.c:new_thing()` と一致しているか未監査
- [x] hallucination potion を `potions.c:P_LSD` / `daemons.c:come_down()` 相当で接続済み
- [x] 投擲が斜め方向に未対応（`misc.c:get_dir()` / `weapons.c:missile()/do_motion()` 準拠の期待値テストで既存対応を確認）
- [x] 迷路部屋 / gone room は生成・接続・視界の初期対応済み
- [x] 暗い部屋の探索済み床 `.` が退室後も残る表示を Rogue 5.4.4 の床消去に寄せて非表示化
- [ ] 通路番号付き passages / Xeroc / cancellation と Dragon breath / bolt 系の完全連携（Dragon breath の同室・直線・射程・`ISCANC` ゲートは `chase.c:do_chase()` / `sticks.c:fire_bolt()` 準拠で接続済み）
- [x] 巻物 18 種化完了（identify 対象選択 UI 含む）
- [x] ポーションを原作 14 種へ更新（hallucination / levitation 接続済み）
- [x] treasure room（モンスターハウス）を `new_level.c:treas_room()` 準拠で接続済み。`rogue_dungeon.py` に個数計算と発生ゲートを分離。

## テスト・基盤タスク

- [x] `tests/test_rogue_baseline.py` で Pyxel mock による import / 初期化 / ダンジョン到達性 / 初期装備 / 翻訳層 baseline を確認
- [x] `python3 -m unittest` でテストを実行可能にする
- [x] RNG helper を導入し、Rogue 5.4.4 準拠・seed 再現性・Pyxel MCP の `random.randint` 警告の扱いを整理する
- [x] Rogue2.Official `mesg_J` / `mesg_E` に基づく文言辞書の拡充
- [x] Rogue 5.4.4 メッセージ全文監査（`vendor/rogue544` の `msg()` / `addmsg()` 抽出と catalog 化）
- [ ] Select(Back) 補助メニューから開くメッセージ履歴ビュー
- [ ] 英語 / 日本語で同じ seed・操作ならゲーム状態が一致するテストケースを増やす
- [ ] 忠実度修正ごとに Rogue 5.4.4 期待値テストを追加
- [x] Rogue 5.4.4 `rogue.h:NUMCOLS/NUMLINES/STATLINE`, `move.c:do_move()`, `rooms.c:bsze` 準拠のマップ寸法・地形領域テスト追加
