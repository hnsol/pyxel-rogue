# Rogue 5.4.4 Fidelity Design

Rogue 5.4.4 Cソースを底本にするゲームメカニクス、原作参照、忠実度監査の詳細仕様。

## ゲームメカニクス準拠の運用

ゲームメカニクスは Rogue 5.4.4 C ソースを一次情報にする。確率、生成数、ターン消費、状態異常、攻撃判定、アイテム効果、罠、隠し要素、モンスターAIなど、ゲーム状態に影響する挙動は、実装前に該当する原作の関数・定数・テーブルを確認する。推測、現代ローグライクの慣習、Rogue2.Official、既存 Pyxel 実装はゲーム挙動の正解にしない。

Rogue2.Official は日本語表現と用語の準拠元であり、確率やターン処理などのゲームロジックの正解ではない。既存 Pyxel 実装が Rogue 5.4.4 と食い違う場合は、既存挙動ではなく Rogue 5.4.4 を優先する。

Pyxel 向けの差分は、表示、入力、移植UI、非ブロッキング演出など、ゲーム状態を変えない範囲に留める。ゲーム状態が原作と異なる差分をどうしても入れる場合は、原作との差、理由、影響範囲をこの文書へ記録してから実装する。

忠実度に関わる変更は、実装前に Rogue 5.4.4 の期待値テストを追加する。baseline テストは「壊れてほしくない現状」の保護に使い、原作と違う既知バグの正当化には使わない。実装コメントまたはテスト名から、参照した原作ファイル名・関数名・定数名を追えるようにする。

補助参照としてローカルの `vendor/rogue545p/` に Rogue 5.4.5p のコードを置く。出典は http://yozvox.web.fc2.com/526F677565.html 。原則の準拠先は引き続き `vendor/rogue544/` だが、Rogue 5.4.4 の identify scroll は `extern.c:scr_info[]` で `identify potion` / `identify scroll` / `identify weapon` / `identify armor` / `identify ring, wand or staff` の5種類に分かれており、プレイ感の劣化として扱う。これを1種類へ戻す場合は、5.4.5p の `options.c:idscrl`、`extern.c:scr_info2[]`、`extern.c:set_scroll_2()` を比較参照し、Rogue 5.4.4 からの意図的差分としてこの文書へ記録してから実装する。
## RNG とコア分離の進め方

Rogue 5.4.4 準拠作業の土台として、乱数入口は `rogue_rng.py` の `RogueRng` に集約する。`RogueRng.rnd(n)` は原作 `main.c:rnd(range)` 相当、`RogueRng.roll(number, sides)` は原作 `main.c:roll(number, sides)` 相当として扱う。Pyxel 版では現時点で C の `rand()` と seed 完全一致までは目標にしないが、ゲーム状態に影響する乱数呼び出しは `RNG` 経由にし、忠実度テストで差し替えや監査ができる形にする。

既存の `random.choice` / `random.shuffle` 相当の処理は、初回整理では Python 標準の挙動を維持する薄いラッパーとして残す。乱数消費順そのものを Rogue 5.4.4 の `rnd()` ベースへ寄せる必要がある箇所は、該当する原作関数を確認したうえで、その機能の忠実度修正として個別に扱う。

今後の大きな分割は一気に `core/` 化しない。未実装でしがらみが少ない指輪・杖を、最初の Pyxel 非依存ロジックの実例として追加する。指輪では `rings.c` と `things.c`、杖では `sticks.c` と方向指定 zap 周辺を参照し、効果処理、生成テーブル、識別、チャージ、装備/使用結果を Pyxel 入力・描画から切り離しやすい helper として作る。既存機能は触るタイミングで `swing`, `roll_em`, `do_passages`, `pick_one` など C 関数名に対応する小さな境界へ寄せ、`Game` から純ロジックが自然に抜ける形を優先する。
## モンスターAI

モンスターAIは Rogue 5.4.4 の `monsters.c`, `chase.c`, `fight.c`, `move.c` を基準にする。単純な「視界内ならマンハッタン距離で近づく」処理は原作と大きく異なり、扉上のプレイヤーへ近づけない、Rattlesnake / Ice monster の特殊攻撃が弱すぎる、非起床モンスターまで常時接近する、といったズレを生むため採用しない。`chase.c:runners()` の `ISHELD` / `ISRUN` ゲート、`ISTARGET` 移動後解除、`move_monst() == -1` 時の飛行追加移動抑止、飛行モンスターの追加移動、`chase.c:move_monst()` の速度ステップ実行と held gate 分離、`chase.c:runto()` の追跡開始、`chase.c:diag_ok()` の斜め移動可否、`chase.c:dist()` / `dist_cp()` の二乗距離、`chase.c:roomin()` の部屋矩形判定、`chase.c:see_monst()` / `cansee()` の盲目/不可視、lamp距離、斜め遮蔽、同室照明ゲート、`chase.c:do_chase()` の Dragon flame gate / 最寄り出口 / greedy 目的地補正 / chasee room 選択、`chase.c:chase()` の confused / Phantom / Bat ランダム移動ゲート、混乱解除、候補ゲート、距離/tie選択、戻り値条件は `rogue_chase.py` の小 helper とし、`move.c:rndmove()` の1回だけのランダム移動試行は `rogue_move.py` の小 helper とする。`Game` 側はモンスター1体のターン処理、ヒーロー距離判定、追跡1ステップ処理、地形判定を渡して委譲する。通常 room door は `passages.c:numpass()` で passage 番号は付くが `F_PASS` ではないため、`chase.c:do_chase()` の `proom` 判定では hero がドア上にいても部屋所属として扱う。

コマンド前の起床は `command.c:command()` が呼ぶ `misc.c:look(TRUE)` に合わせ、Pyxel の `visible` 全体ではなく hero 周囲3x3の `look()` scan だけで行う。明るい部屋の部屋全体起床は `move.c:door_open()` / `rooms.c:enter_room()` 側の責務として扱う。

現行実装では `runto()` 相当で `Monster.running` を立て、running でないモンスターは基本的に移動しない。プレイヤーがモンスターを攻撃した場合や、視界に入った mean monster が `wake_monster()` 相当で起きた場合、`scroll of aggravate monsters` を読んだ場合に追跡を開始する。`chase.c:find_dest()` 相当では、carry 確率を持つモンスターがプレイヤーと別室かつ見えていない場合、同室アイテムを目的地候補にし、`scroll of scare monster` と `mlist` 内の既存 `t_dest` が指すアイテムを除外する。この `mlist` 走査は呼び出し元自身も含むため、`find_dest()` は自分の古い `t_dest` を保持せず、重複済み目的地として扱う。`chase.c:do_chase()` は既存 `t_dest` を床上 `lvl_obj` と照合してから追跡し直す処理を持たないため、目的地 item が床から消えた場合でもその座標へ到着するまで追跡し、到着後に `lvl_obj` が無ければ pack 移動せず停止する。ただし `ISGREED` monster は `do_chase()` 冒頭の `rer->r_goldval == 0` 分岐に合わせ、room gold が消えたら stale gold destination より hero を優先する。部屋所属は通常表示用の `room_at()` とは別にAI用所属を持ち、部屋床、部屋外周、扉、通路を区別する。`chase.c:roomin()` は `r_pos <= coord <= r_pos + r_max` の右下包含境界に合わせる。扉は通路側の所属も保持しつつ、`chase.c:roomin()` / `do_chase()` の同室分岐が必要な場面では部屋側所属も参照する。door 上の chaser が別室の目的地へ向かう場合は、`do_chase()` と同じく部屋側 `r_exit` を先に比較し、その `mindist` を保ったまま passage 側 exit を比較する。

追跡は `chase()` 相当として、周囲8マスから `diag_ok()`、通行可、他モンスター占有、床上 `scroll of scare monster` を避ける条件を満たす候補を選び、Rogue 5.4.4 の `dist()` と同じ二乗距離で目的地に近づく。`PLAYER` は `io.c:step_ok()` で通行可能文字なので、item 目的地追跡中でも候補評価に含め、選ばれた場合は `do_chase()` 側の `ce(this, hero)` 分岐として攻撃する。hero の足元に scare scroll がある場合も `winat()` は `PLAYER` を先に返すため、scare scroll 除外は適用しない。別部屋にいる場合は、まず所属部屋の出口へ向かう。通路所属は `passages.c:numpass()` / `chase.c:roomin()` に寄せ、連結した `T_CORR` / `T_DOOR` 成分を passage identity として扱う。passage exit は `passnum()` が rooms[].r_exit 順に最初の未番号 exit から `numpass()` する root と、down/up/right/left 再帰で記録される順を保持し、`chase.c:do_chase()` の strict `<` による同距離出口 tie へ反映する。`chase.c:do_chase()` が maze passage 上の `lvl_obj` を monster pack へ移すと `chat(obj->o_pos)` は `FLOOR` へ戻るが `F_PASS` / passage number は残るため、Pyxel 版でも maze room 内の回収後 floor は AI 用 passage identity に含める。Bat、Phantom、confused monster は原作同様にランダム移動を混ぜ、`move.c:rndmove()` の `winat()` / `step_ok()` 判定に合わせて item 擬態 Xeroc もランダム移動先としては通過可能にする。hero の足元に scare scroll がある場合も `winat()` は `PLAYER` を返すため、monster のランダム移動では攻撃可能にする。player の混乱ランダム移動も同じ `move.c:rndmove()` なので、通常 monster glyph と `S_SCARE` scroll はランダム移動先として不可にする。flying monster は距離がある場合に追加移動する。

特殊攻撃は `fight.c` の命中後分岐へ寄せる。Ice monster は命中時に `no_command += rnd(2)+2` 相当でプレイヤーを凍結させ、Rattlesnake は `save(VS_POISON)` 失敗時に Strength を下げる。Aquator、Leprechaun、Nymph、Medusa、Troll、Vampire、Wraith、Venus Flytrap も、既存の簡略フラグを維持しつつ原作の発動タイミングへ寄せる。`fight.c:swing()` の d20 命中判定、`fight.c:roll_em()` の weapon/hurl profile、ダメージ式ロール、部位ごとの命中/ダメージ加算、defender `!ISRUN` 命中補正、`str_plus[]` / `add_dam[]` の Strength 補正、Ice monster の freeze 加算、Rattlesnake poison の Strength 低下判定、Wraith/Vampire drain 発動率、Wraith level drain、Vampire max HP drain、Venus Flytrap の `vf_hit` 加算・miss 時ダメージ・hold 解除、Nymph の `rnd(++nobj)==0` 盗み対象選択、Leprechaun の金額減算回数、`rogue.h:GOLDCALC` の金額ロールは `rogue_fight.py` の小 helper とし、`ISCANC` 相当の `cancel` は命中後特殊攻撃、Medusa の `wake_monster()` 視線、再生、Dragon breath などの特殊能力入口で必ず確認する。プレイヤーの行動不能は、sleep/freeze/faint 系の `no_command`、bear trap の `no_move`、Venus Flytrap の `held_by` に分ける。

モンスター状態フラグは `rogue_monsters.py` を Pyxel 非依存の対応表・小 helper とし、Rogue 5.4.4 `rogue.h` の `ISHASTE` / `ISSLOW` / `ISCANC` / `ISINVIS` / `CANHUH` に対応する既存フラグ文字列を集中させる。`chase.c:move_monst()` に合わせ、`ISSLOW` は `t_turn` が真の手だけ通常追跡し、`ISHASTE` は追加追跡を行い、処理後に `t_turn` を反転する。`sticks.c:do_zap()` の `WS_HASTE_M` / `WS_SLOW_M` はこの helper 経由で、遅い相手を速めると `ISSLOW` 解除、速い相手を遅くすると `ISHASTE` 解除、そうでなければ該当フラグ付与とし、slow monster は `t_turn = TRUE` に戻す。

player/monster の saving throw は `monsters.c:save_throw()` / `save()` に合わせ、`rogue_monsters.save_throw()` へ集約する。magic save は protection ring の enchantment を `VS_MAGIC` から差し引き、poison save は `VS_POISON=0` として同じ helper を使う。

モンスターの戦闘値は Rogue 5.4.4 `extern.c:monsters[]` の `s_lvl`, `s_arm`, `s_dmg`, `s_exp` を名前付き `MonsterSpec` として持つ。tuple の位置引数で `level` と `armor` を取り違えると、プレイヤー命中率や plate mail の防御力が大きく壊れるため、代表モンスターと `fight.c:swing` の境界値をテストで固定する。Hobgoblin は `level=1`, `armor=5`, `damage="1x8"`, `exp=3`、Ice monster は `level=1`, `armor=9`, `damage="0x0"`, `exp=5` を監査対象にする。生成時は `rogue_monsters.py` の `new_monster_stats()` を通し、`monsters.c:new_monster()` に合わせて `level - AMULETLEVEL` が正なら `s_lvl` / HP roll / `s_arm` / `s_exp` に反映し、EXPは `exp_add()` の HP/level 補正も加える。30階以深では `ISHASTE` を付与する。

通路番号付き passages、Dragon breath、指輪・杖・cancellation とAIの完全連携は、Rogue 5.4.4 `chase.c:do_chase()` の `DRAGONSHOT` 分岐と `sticks.c:fire_bolt()` の `hit_hero` 状態機械に合わせて監査済み。Dragon breath の最小接続は Rogue 5.4.4 `chase.c:do_chase()` の `DRAGONSHOT` 分岐と `sticks.c:fire_bolt()` に合わせ、同じ部屋内で直線・射程内・非 `ISCANC` なら `rnd(5)==0` で Dragon の位置から flame bolt を撃つ。monster 起点 bolt は hero に届くまでは他 monster を無視し、hero save 後は背後の monster に当たり得る。breath 後は `running/count/quiet` を止め、`to_death && !ISTARGET` に合わせて対象外 fight-to-death を解除する。`daemons.c:stomach()` の `hungry_state` 変化も `running/count/to_death` を止めるため、Pyxel 側では空腹状態変化時に dash と fight-to-death を同時に解除する。wandering monster は Rogue 5.4.4 の `main.c:fuse(swander, 0, WANDERTIME, AFTER)`, `daemons.c:swander()` / `rollwand()`, `monsters.c:wanderer()` を基準にし、初回 `swander` は AFTER fuse、以後の `rollwand` daemon と再予約 `swander` は BEFORE として扱う。`WANDERTIME` は `rogue.h` の `spread(70)` とする。配置位置は `rooms.c:find_floor(NULL, ..., monst=TRUE)` と同じく `rnd_room()` / `rnd_pos()` を成功まで繰り返し、部屋内の `step_ok()` セルで stairs / traps も許可し、通常通路だけのセルは除外する。`new_level.c:rnd_room()` は `ISGONE` を引いた間だけ再抽選し、固定回数後に先頭usableへfallbackする処理は持たない。wandering monster はさらに `roomin(cp) != proom` まで固定上限なしで繰り返し、teleport away は hero と同座標なら再試行する。部屋モンスター配置は `find_floor(rp, ..., monst=TRUE)` 後に `randmonster(FALSE)` する原作順を保つ。暗い部屋、迷路部屋、gone room は生成と視界への接続を先行実装済みで、今後も原作関数を確認しながらアイテム・モンスター配置やAI所属を詰める。階層生成は `new_level.c:new_level()` と同じく `do_rooms()` 後に `do_passages()` だけで通路を掘り、原作にない生成後の接続補修通路は追加しない。`passages.c:conn()` の通常部屋 door 座標と通路の曲がり位置は `rnd()` ベースで選び、隣接扉回避や Python `shuffle` / `randint` による独自選択は使わない。迷路部屋本体は `rooms.c:do_maze()` / `dig()` に合わせ、部屋原点からの偶数 offset を `rnd()` で開始点にし、進行方向は `rnd(++cnt)==0` で選ぶ。迷路部屋の接続点も `passages.c:conn()` と同じく side wall 座標を `rnd(room size - 2) + 1` で選び、`F_PASS` でない間は再試行する。maze room では `passages.c:door()` が表示を変えなくても `r_exit` へ記録するため、Pyxel 版でも `Room.exits` を AI 用出口として保持する。

`chase.c:runners()` と `daemons.c:stomach()` は `to_death` だけを落とし、Dragon breath / monster attack / remove_mon の対象外分岐だけが `kamikaze` も落とすため、Pyxel 側でも解除 helper を分ける。
## 武器メカニクス

武器は Rogue 5.4.4 の `weapons.c:init_dam`, `fight.c:roll_em`, `things.c:inv_name/new_thing`, `scrolls.c:S_ENCH` を基準にする。武器は命中補正 `hit_plus` とダメージ補正 `dam_plus` を別々に持ち、表示も `+1,+1 mace (weapon in hand)` のように2値で出す。近接・投擲とも Strength の命中/ダメージ補正を通し、arrow + bow のような launcher 補正も原作に合わせて合算する。`weapons.c:fall()` / `fallpos()` / `init_weapon()` の投擲落下候補、`rnd(++cnt)==0` 選択、落下失敗時分岐、初期個数は `rogue_weapons.py` の小 helper とする。`fight.c:remove_mon()` の monster pack 落下も `fall(FALSE)` と同じく `fallpos()` に通し、`fallpos()` 失敗時は impact 座標へ直置きせず破棄する。`things.c:new_thing()` の weapon curse/enchant と初期個数乱数、`fallpos()` の候補選択乱数は `RogueRng.rnd()` 経由に統一する。

防具は当面既存の `ench` 表現を維持する。ring of dexterity / increase damage は `fight.c:roll_em` 相当に合わせ、`weap == cur_weapon` のときに加算し、投げた武器が current weapon の場合も `hurl` 判定前に補正する。

装備変更は Rogue 5.4.4 の `armor.c:wear()` と `weapons.c:wield()` を分けて扱う。armor は `cur_armor != NULL` の場合に wear を拒否し、先に take off する必要がある。wield は `pack.c:get_item("wield", WEAPON)` 後に `weapons.c:wield()` 側で armor だけ拒否するため、Pyxel 版の Wield 選択リストも pack 全体を対象にし、potion / scroll / food / stick などを current weapon にできる。weapon は `weapons.c:wield()` が `dropcheck(cur_weapon)` を通るため、現在武器が cursed でなければ持ち替え可能であり、Pyxel 版でも自動置換自体は差分として扱わない。

呪い生成確率は `things.c:new_thing()` を基準にする。weapon は `rnd(100) < 10` で cursed、armor は `rnd(100) < 20` で cursed、一部 ring は `rnd(3)==0` で `o_arm=-1` かつ cursed、ring of aggravate monster と ring of teleportation は常時 cursed とする。food は ration/slime-mold を `rnd(10)!=0` の90/10にし、カテゴリ重みは `extern.c:things[]` の 26/36/16/7/7/4/4 を基準にする。`things.c:pick_one()` 相当の減算式重み選択は `rogue_things.py` に分離し、カテゴリ、potion、scroll、weapon、armor、ring、stick の種類選択は `rnd(100)` 経由で行う。`new_level.c:new_level()` の `no_food++` と `things.c:new_thing()` の food 生成時 `no_food=0` も `rogue_things.py` で扱い、4階層超で food を強制する。`new_level.c:put_things()` は `MAXOBJ` 各試行の 36% 判定に成功した時点で `new_thing()` と `find_floor()` へ進むため、Pyxel版も成功数を先に数えず、試行ごとに生成と配置を挟む。生成時の weapon / armor の curse / enchant は原則未鑑定情報であり、Pyxel 版では `Item.known` を Rogue 5.4.4 の `ISKNOW` 相当として扱う。armor は `armor.c:wear()` に合わせ、装備した時点で `known=True` にして enchant / protection を表示する。ring の `ring_num()` と stick の `charge_str()` は種類識別後に表示する。

拾得処理は Rogue 5.4.4 の `pack.c:add_pack()` / `pack_room()` を基準にする。scare monster scroll は未発見なら `ISFOUND` 相当を立て、発見済みを拾うと dust で消滅する。床からの拾得では同種スタック可能な food / missile でも `pack_room()` 相当の上限確認を先に通し、満杯ならスタックせず床に残す。

食料使用は Rogue 5.4.4 `misc.c:eat()` に合わせる。FOOD 以外を選んだ場合は `ugh, you would get ill if you ate that` を出し、`leave_pack()` へ進まず pack と food を変えない。FOOD の場合だけ `food_left = max(food_left, 0) + HUNGERTIME - 200 + rnd(400)`、STOMACHSIZE cap、hungry_state reset、slime-mold / ration 分岐を通す。

Potion / scroll 使用も `potions.c:quaff()` と `scrolls.c:read_scroll()` の型 gate を先に通す。POTION 以外の quaff は `yuk! Why would you want to drink that?`、SCROLL 以外の read は `there is nothing on it to read` を出し、識別状態・効果・`leave_pack()` へ進まない。

`scrolls.c:read_scroll()` は効果分岐より前に、読んだ scroll が `cur_weapon` なら `cur_weapon = NULL` にする。特に wielded `scroll of enchant weapon` は自分自身を current weapon として強化せず、`cur_weapon == NULL` の `you feel a strange sense of loss` 分岐へ進む。
## 指輪メカニクス

指輪は Rogue 5.4.4 の `rogue.h:R_*`, `extern.c:ring_info[]`, `init.c:stones[]/init_stones()`, `things.c:new_thing()/inv_name()/dropcheck()`, `rings.c:ring_on()/ring_off()/ring_eat()/ring_num()`, `fight.c:roll_em()`, `daemons.c:doctor()/stomach()`, `scrolls.c:S_REMOVE` を基準にする。`rogue_rings.py` を Pyxel 非依存の最初の指輪ロジック境界とし、14種テーブル、ランダム石名、補正付き指輪生成、左右スロット、装備/解除、呪い、食料消費をここへ寄せる。

初回実装では、ゲーム状態に直結する protection / add strength / dexterity / increase damage / slow digestion / regeneration を接続した。protection はプレイヤーAC、防具と同じ低いほど強い値へ反映し、dexterity / increase damage は装備中武器での近接攻撃にだけ加算する。slow digestion と searching などの確率型食料消費は `rings.c:ring_eat()` の負値テーブルに合わせ、slow digestion は消費を減らす。regeneration は `daemons.c:doctor()` と同じく自然回復判定後に追加回復し、回復した場合は quiet をリセットする。

残りの指輪効果は、Rogue 5.4.4 の `command.c`, `rings.c`, `monsters.c`, `move.c`, `fight.c`, `potions.c` を確認して接続した。searching はターン後処理で手ごとに `search()` 相当を呼び、ターンを追加消費せず失敗時メッセージも出さない。teleportation は同じターン後処理で手ごとに `rnd(50)==0` のときテレポートする。see invisible は invisible monster の表示条件へ反映し、aggravate monster は装備時と装備中の monster creation で追跡を開始させる。stealth は `wake_monster()` 相当の mean monster 起床判定を抑制する。sustain strength は Rattlesnake / dart trap / potion of poison の Strength 低下を防ぎ、maintain armor は Aquator / rust trap などの `rust_armor()` 相当で錆びを防ぐ。adornment は装備時効果を持たず、装備しただけでは識別済みにしない。

UI差分として、原作の `gethand()` による左右手プロンプトは、携帯機向けメニュー操作では最初の空きスロットへ装備し、解除時は装備中アイテムを選ぶ方式にしている。左右どちらに装備されているかはインベントリ表示の `(on left hand)` / `(on right hand)` で確認できる。今後、左右指定が攻略上必要になる場面が出た場合は、ゲーム状態の差分を出さずに方向入力で手を選ぶUIへ拡張する。

see invisible potion は Rogue 5.4.4 `potions.c:P_SEEINVIS` / `do_pot()`, `misc.c:spread()`, `rogue.h:CANSEE/SEEDURATION`, `daemons.c:unsee()` に合わせ、`spread(SEEDURATION)` の間だけ invisible monster の表示条件へ反映する。`P_SEEINVIS` 末尾の `sight()` 相当により blind も解除する。hallucination 中の invisible monster は `misc.c:look()` 相当により正体ではなくランダムな A-Z として表示する。hallucination potion 開始時は `potions.c:seen_stairs()` 相当で既知の階段を記録し、`misc.c:trip_ch()` / `daemons.c:visuals()` に合わせて既知の階段だけはランダムな物資文字へ変えない。monster detection potion は `potions.c:P_MFIND` の `SEEMONST` / `turn_see()` 相当として、現在フロアのモンスターを一時表示し、`HUHDURATION` 後の `turn_see(TRUE)` fuse で解除する。

Xeroc は Rogue 5.4.4 `monsters.c:new_monster()` の `t_disguise = rnd_thing()`、`misc.c:look()` の `t_disguise` 表示、`fight.c:attack()` の近接正体露出、`sticks.c:do_zap()` の `WS_CANCEL` による `t_disguise = t_type` を基準にする。Pyxel 版では `Monster.disguise` を `t_disguise` 相当として持ち、通常表示では擬態文字を描き、hallucination 中は既存 `rnd(26)+'A'` 表示を優先する。近接攻撃で未露出の Xeroc に触れた場合は正体を表示して攻撃をそこで止める。投擲時は正体露出後に攻撃判定を続ける。
## 杖メカニクス

杖は Rogue 5.4.4 の `rogue.h:WS_*`, `extern.c:ws_info[]`, `init.c:metal[]/wood[]/init_materials()`, `things.c:new_thing()/inv_name()/pick_one()`, `sticks.c:fix_stick()/do_zap()/charge_str()` を基準にする。初回実装では `rogue_sticks.py` を Pyxel 非依存の杖ロジック境界として追加し、14種テーブル、wand/staff と素材名のランダム割り当て、生成時チャージ、staff/wand の基礎ダメージ、識別時のチャージ表示を分離した。

アイテム生成では Rogue 5.4.4 `things[]` の最後の 4% を stick に戻し、未識別名は `copper wand` / `balsa staff` 型、識別済み名は `wand of light [12 charges](copper)` 型に寄せる。Pyxel 版の操作ではメニューの `Zap` から杖を選び、その後に方向を指定する。これは原作の `z` コマンドと同じく方向指定 zap として扱い、チャージが 0 の場合は `nothing happens` でチャージを減らさない。

今回接続した効果は `WS_LIGHT` の部屋照明と識別、チャージ消費、単体モンスター対象系の invisibility / polymorph / teleport away / teleport to / cancellation / haste monster / slow monster までとする。light は `sticks.c:WS_LIGHT` に合わせ、`rogue_sticks.light_uses_room_branch()` で gone room / 通路では `the corridor glows and then fades`、通常部屋では既に明るい場合も `the room is lit` とし、暗い部屋なら `ROOM_DARK` を外して視界を更新する。単体対象系は `sticks.c:do_zap()` に合わせ、`rogue.h:winat()` 相当で monster の `t_disguise` を先に見て、`io.c:step_ok()` 相当で停止位置を決める。アイテム文字に擬態中の Xeroc は `step_ok()` なので照準を通過し、既に `X` として見えている場合だけ対象になる。invisibility は `ISINVIS` 相当、polymorph は `new_monster(tp, rnd(26)+'A', pos)` 相当とし、`t_pack` は原作通り退避して復元し、`detach(mlist,tp)` 後の `monsters.c:new_monster()` `attach(mlist,tp)` に合わせて mlist head 相当に再接続する。polymorph wand の正式識別は `rogue_sticks.polymorph_identifies()` を通し、`see_monst(tp)` 相当で polymorph 後のモンスターが見えている時だけ行う。teleport away は `find_floor(NULL, ..., TRUE)` 相当の床へ転移、teleport to は `rogue_sticks.teleport_to_position()` でプレイヤー隣接の指定方向へ転移、cancellation は `ISCANC` 相当を立てて invisible / confuse 能力を外す。Flytrap に当たった対象系 zap は、保持者照合をせず `ISHELD` 相当を外す。cancellation では `fight.c:attack()` の miss damage に使う `vf_hit` 蓄積は消さない。cancellation 済みモンスターは `fight.c:attack()` と `monsters.c:wake_monster()` の `!ISCANC` 分岐に合わせ、既存の特殊攻撃、Medusa 視線、再生を抑止する。

lightning, fire, cold は Rogue 5.4.4 `sticks.c:do_zap()` / `fire_bolt()` に合わせ、`WS_ELECT` は bolt、`WS_FIRE` は flame、`WS_COLD` は ice として識別し、`BOLT_LENGTH=6`、壁・扉反射、`6x6` ダメージ、モンスター/プレイヤーの `VS_MAGIC` セーブ、Dragon に対する flame bounce を接続する。`fire_bolt()` の DOOR 分岐は `rogue_sticks.bolt_should_bounce()` を通し、hero がその door 上にいる場合だけ反射せず命中判定へ進む。モンスターがセーブして bolt が外れた時の `runto()` と miss 表示は、`rogue_sticks.saved_monster_miss_feedback()` を通して原作通り `ch != 'M' || t_disguise == 'M'` の場合だけ行い、追跡開始も hero 発射時かつ同ゲート内に限定する。miss 文言の対象名は `fight.c:set_mname()` 相当で、未視認なら `something`、monster detection 中なら実名を使う。Xeroc の item 擬態は `rogue.h:winat()` が `t_disguise` を返すため、`sticks.c:fire_bolt()` の `ch != 'M'` 分岐により saved miss 表示を抑止しない。hero 自身の反射 bolt で死亡した場合は `rogue_sticks.bolt_death_cause()` を通し、`death('b')` / `rip.c` に合わせて killer を `bolt` とする。treasure room、cancellation と Dragon breath などの細部連携は、それぞれの機能実装時に改めて原作関数を確認して詰める。

magic missile は `sticks.c:WS_MISSILE` の `o_hurldmg="1x4"`, `o_hplus=100`, `o_dplus=1`, `ISMISL`, `o_launch=cur_weapon->o_which` と `weapons.c:do_motion()` / `fight.c:roll_em()` を基準にし、`rogue_sticks.magic_missile_damage()` で現在武器がある場合の `o_dplus` も加える。`do_motion()` は `winat()` と `step_ok()` で弾道を進め、door で止まるため、アイテム擬態中の Xeroc は magic missile の弾道も通過する。

drain life は `sticks.c:drain()` の `pstats.s_hpt /= 2` 後に対象数で割る処理を `rogue_sticks.drain_life_split()` に分けて基準にする。部屋内では同じ部屋、通路内では `t_room == proom` / passage door 側の対象を集めるため、Pyxel 版の現行 passage 簡略表現では通路対象を隣接限定にしない。
## ダンジョン生成

元祖ローグの3×3セクターグリッドアルゴリズムを再現。現行では `rooms.c` と同じ `bsze.x = NUMCOLS / 3`, `bsze.y = NUMLINES / 3` により 80×24 マップを 26×8 セクター基準で扱い、Rogue 5.4.4 と同じ sector index 0..8 の固定順で9個の `Room` を作ったうえで、`rooms.c` 相当の `ISGONE` / 暗い部屋 / `ISMAZE` フラグを割り当てる。通路は全隣接セクターを無条件に接続せず、`passages.c` の `do_passages()` と同様に9部屋を結ぶ spanning tree 8本を作り、追加で `rnd(5)` 回だけ未接続の隣接エッジを掘る。通常部屋、迷路部屋、gone room はこの選ばれた通路グラフ上で接続し、flood fill は互換用の到達保証として残している。

地形・通路・階段・罠・アイテム・モンスター配置は原則 `y=1..22` に収める。Pyxel 側の HUD やログはこの論理座標に含めず、ゲーム状態に影響しない表示レイヤーとして扱う。

通路生成は Rogue 5.4.4 C ソースの `passages.c` を参照し、推測で似せない。特に `do_passages()` が部屋グラフを作り、`conn()` が接続方向に応じて壁上のドア位置を選び、`door()` が部屋の出口を記録し、`putpass()` が通路を掘る責務分担を基準にする。`conn()` は渡された edge が逆順でも小さい room index 側へ正規化し、横接続は左→右、縦接続は上→下の順で door RNG を消費する。階段配置は `new_level.c:new_level()` と同じく通路生成後に行い、固定 seed 群で階段が1個だけ生成され、プレイヤー初期位置から到達可能であることを監査する。

隠し扉・隠し通路は `passages.c:door()` / `putpass()` と同じく、通路生成中に `rnd(10)+1 < level` と `rnd(5)` / `rnd(40)` で判定する。生成後に地形を走査して隠す方式は、原作の RNG 消費順と `new_level.c:put_things()` 以降の床選択順をずらすため使わない。

階層生成の入口は Rogue 5.4.4 `new_level.c:new_level()` に合わせ、生成前に Venus Flytrap の hold 相当を解除する。teleport の hold 解除とは異なり、旧階層の monster は破棄されるため、Pyxel 側では古い `held_by` 参照を残さないことを目的にする。

部屋フラグは Rogue 5.4.4 `rooms.c` の `rnd(4)` 個の `ISGONE`、`rnd(10) < level - 1` による暗い部屋、同分岐内の `rnd(15)==0` による `ISMAZE` を基準にする。暗い部屋と迷路部屋は部屋全体を一括可視化せず、周囲視界のみで探索する。gone room は壁やドアを置かず、通路セルとして接続する。通路の曲がり点はドア直後の壁沿いセルを避け、部屋の水平壁に沿って長い通路が走らないようにする。

暗い部屋の床表示は Rogue 5.4.4 `misc.c:erase_lamp()`, `misc.c:show_floor()`, `rooms.c:leave_room()` の画面上の床消去に合わせる。Pyxel版は探索済みセルを再描画するが、暗い部屋の探索済み床 `.` は現在視界外では表示しない。壁、ドア、床上アイテムの扱いは既存の探索済み表示方針を維持し、床だけをランプ範囲外で消す。
## Phase 4 の完成基準

「Pyxel版をクリアしたら Rogue V5 をクリアしたと言える」ための短期的な山場は Phase 4 とする。26階で Amulet of Yendor が出現し、Amulet 所持後に階段を上って1階へ帰還し、勝利状態へ到達できることを最小のクリア条件にする。

`Cat and Amulet of Nyandor` は Rogue 5.4.4 本編仕様ではなく、5F Playable Beta 用の公開 variant として扱う。`PYXEL_ROGUE_VARIANT=nyandor` の時だけ、難易度は `Normal` 固定、目的階層は地下5階、`CAT_AMULET` 枠の特殊アイテム `The Cat (wearing the Amulet of Nyandor)` を `c` として置く。猫はインベントリ1枠を占有し、Drop不可。猫所持で地下1階から上ると勝利する。タイトルの `ENTER DUNGEON` 後は任務説明、簡単操作ガイドの順に表示し、ガイド承認後にゲームを開始する。Pages root はこの variant、`/rogue/` は本編デバッグ版とする。本編 `rogue` variant の Rogue 5.4.4 忠実度判断には混ぜない。

指輪、杖、罠、隠しドア、隠し通路、scroll of scare monster の床上効果は、単なるアイテム種類追加ではなく Rogue 5.4.4 の攻略判断を成立させる要素として扱う。特に search は、罠・隠しドア・隠し通路を発見するためのゲームロジック上の hook とし、A空押しの正面探索と Select+B / Action menu / `S` の周囲探索を区別する。

Trap Inspect は Rogue 5.4.4 の `^` + 方向に相当するターン非消費コマンドとして扱う。未発見罠は確認対象にせず、search または踏んだ時に露出した `^` だけが種類表示の対象になる。ゲームパッドでは Select+D-pad を高速入力、Action menu の Trap を発見しやすい入口にする。

罠と隠し要素の発生・発見は Rogue 5.4.4 の `new_level.c`, `passages.c`, `command.c`, `move.c` を基準にする。罠は `rnd(10) < level` の階層ゲートを通ったとき `rnd(level / 4) + 1` 個、最大 `MAXTRAPS` 個を部屋床へ隠して置き、種類は各 trap ごとに床選択後 `rnd(NTRAPS)` とする。trap 配置は候補一覧から選ばず、`find_floor(NULL, ..., monst=FALSE)` の `rnd_room()` / `rnd_pos()` 試行後に `chat()==FLOOR` を確認するだけなので、monster square は除外しない。hidden trap は `move.c:do_move()` と `command.c:search()` に合わせ、表示文字が `FLOOR` の時だけ発見・発動し、stairs / item など別文字に後置きされた場合は trap flags だけでは露出・発動しない。隠し扉は `rnd(10)+1 < level && rnd(5)==0`、隠し通路は `rnd(10)+1 < level && rnd(40)==0` に寄せ、1階では生成されない。search は隠し扉 `rnd(5+probinc)==0`、罠 `rnd(2+probinc)==0`、隠し通路 `rnd(3+probinc)==0` で露出する。`probinc` は `command.c:search()` と同じく hallucination で +3、blind で +2 とする。`new_level.c` / `passages.c` / `command.c:search()` の確率ゲートは `rogue_search.py` / `rogue_dungeon.py` の小 helper として追えるようにする。`io.c:step_ok()` の文字/地形判定は `rogue_io.py` に置き、`misc.c:look()` 系の斜め遮蔽、`sticks.c:do_zap()` の `winat()` 照準、`rooms.c:find_floor(..., monst=TRUE)` 系の候補条件で同じ基準を使う。`move.c:be_trapped()` は levitation でなければ trap 種類の処理前に `running=FALSE` / `count=FALSE` 相当をクリアし、bear trap は `no_move += BEARTIME`、sleeping gas は `no_command += SLEEPTIME`、dart trap poison は `save(VS_POISON)` 後に sustain strength と Strength floor を確認して処理する。`do_move()` は `hero = nh` より前に `be_trapped(&nh)` を呼ぶため、移動で踏んだ arrow trap miss の矢は移動前 hero 位置から `fall()` する。`move.c:rust_armor()` の錆び合法判定・保護分岐と、`T_MYST` の11択メッセージ表は `rogue_move.py` の小 helper とする。

次の忠実度スプリントでは、passages / monster AI 細部、daemon / fuse、鑑定・命名・発見リストの順で進める。各修正では Rogue 5.4.4 C ソースの関数・定数を先に確認し、必要なら期待値テストを追加してから実装を変える。

run 停止条件は Rogue 5.4.4 の `move.c:do_run()` / `do_move()` と `misc.c:look()` を基準にする。Pyxel 版の dash は `look()` 相当の3x3前方側チェックで床アイテム、近接モンスター、罠、階段、扉、通路分岐を停止対象にし、遠くに見えているだけのモンスターでは停止しない。浅い階の行き止まり通路は、現行方針では `passages.c` の spanning tree と `rnd(5)` 追加接続に寄せており、体感差が出てもまず固定 seed のグラフ監査で原作相当か確認する。
## Phase 4 実装記録：原作との種類数・部屋タイプ差分

Phase 4 では、Rogue 5.4.4 の以下の主要メカニクスを「Pyxel版をクリアしたら Rogue V5 をクリアしたと言える」状態の成立に必要な忠実度修正対象として扱った。Rogue 5.4.4 は、Rogue V5 体験を一つの検証可能な実装へ接続するための底本であり、Rogue V5 の意味を排他的に固定するものではない。達成単位は Rogue 全体ではなく Rogue V5 であり、実装検証の底本は Rogue 5.4.4 である。2026-05-05 時点で、主要攻略判断に効く機能面の実装は完了扱いとし、今後見つかった細部差分は Phase 4 後の監査 backlog として扱う。各実装は原作関数の期待値テストを先に追加してから接続する方針で進めた。

巻物は `rogue.h:S_CONFUSE..S_PROTECT` / `MAXSCROLLS=18` / `scrolls.c:read_scroll()` / `extern.c:scr_info[]` を基準にする。Pyxel 版の `SCROLLS` は原作 18 種の順序と確率へ更新し、identify は Rogue 5.4.4 では `S_ID_POTION` / `S_ID_SCROLL` / `S_ID_WEAPON` / `S_ID_ARMOR` / `S_ID_R_OR_S` の 5 種へ分離されている。今後はこの5種類仕様を劣化差分として扱い、5.4.5p の `idscrl` 実装をリファレンスに1種類化する方針を検討する。`S_ID_*` は `scrolls.c:read_scroll()` の `id_type[]` と `wizard.c:set_know()` 相当に合わせ、対象カテゴリだけを正式鑑定する。現時点では携帯機UI向けの暫定として該当カテゴリの未鑑定品から自動選択するため、原作 `whatis(TRUE, type)` の対象選択プロンプトは後続の「鑑定・命名・発見リスト忠実度」で実装する。`S_CONFUSE` は `fight.c:attack()` の `CANHUH` 付与、`S_FDET` は `scrolls.c:S_FDET` の全食料一時表示、`S_PROTECT` は `scrolls.c:S_PROTECT` の防具呪い・錆び防止として接続する。

`S_HOLD` は `scrolls.c:read_scroll()` と同じく周囲2マス内の `ISRUN` monster から `ISRUN` を外し、`ISHELD` を立てるだけにする。原作に duration roll はなく、解除は `chase.c:runto()` など `ISHELD` を外す入口に任せる。
`S_CREATE` は `scrolls.c:read_scroll()` と同じく周囲8マスを `winat()` / `io.c:step_ok()` で候補化する。通常 monster 文字は候補外だが、item 文字に擬態した Xeroc は `step_ok()` を通る。生成は `monsters.c:new_monster()` の `attach(mlist, tp)` に合わせ、同座標に既存 monster がある場合でも新 monster を mlist head 相当に置く。

scroll の未識別タイトルは `init.c:init_names()` を基準にし、`rnd(3)+2` 語、各語 `rnd(3)+1` 音節、各音節 `sylls[rnd(count)]` で組み立てる。`MAXNAME` 判定は単語ごとではなく `prbuf` 全体の書き込み位置に掛かるため、Pyxel 版の `rogue_init.scroll_title()` もタイトル全体の長さで判定し、`IdentTable.snam` 生成で使う。

ポーションは `rogue.h:P_CONFUSE..P_LEVIT` / `MAXPOTIONS=14` / `potions.c:quaff()` / `extern.c:pot_info[]` を基準にする。現行 Pyxel 版は原作 14 種を実装済み。`P_LSD` は `ISHALU` 相当として `potions.c:do_pot()` / `daemons.c:come_down()` に合わせ、`misc.c:rnd_thing()` / `misc.c:look()` 相当の視覚混乱、`command.c:search()` の `probinc` 増加、invisible monster のランダム表示へ接続する。`P_LSD` 使用時に `SEEMONST` が有効なら原作は `turn_see(FALSE)` を呼ぶが、これは `SEEMONST` 解除ではなく再表示なので、Pyxel 版も monster detection の残り期間と `turn_see` fuse を維持する。`P_LEVIT` は `ISLEVIT` 相当として罠・階段の発動条件と床上アイテム拾得を抑止し、`daemons.c:land()` 相当で解除する。

表示は `misc.c:look()` の `p_monst` 優先に合わせ、visible monster がいるセルでは床・通路・床上アイテムを重ねて描かず、monster glyph だけを描く。これは原作準拠であり、Pyxel 版の可読性改善でもある。床上アイテムや地形は monster が移動した後に通常の探索済み表示へ戻る。

`potions.c:do_pot()` の共通処理は、未識別なら `knowit` で `oi_know` を更新し、対応フラグが未発動なら `fuse()`、発動中なら `lengthen()` する。Pyxel 版ではこの識別更新と fuse/lengthen 分岐を `rogue_potions.do_pot_known()` / `do_pot_fuse_action()` へ寄せ、`P_CONFUSE`, `P_LSD`, `P_BLIND`, `P_LEVIT` の分岐で使う。

`potions.c:P_SEEINVIS` は `do_pot(P_SEEINVIS, FALSE)` のため正式識別せず、既に `CANSEE` の場合は `lengthen(unsee, t)` だけを試みる。Pyxel 版では see invisible ring による `CANSEE` と potion の残り期間を分け、ring-only 状態で quaff した場合は potion duration を増やさない分岐を `rogue_potions.see_invisible_duration()` で固定する。

`potions.c:P_TFIND` は `lvl_obj != NULL` のブロック内で床上アイテムと monster pack を走査するため、床上オブジェクトが無い階では monster pack の魔法アイテムも感知しない。Pyxel 版ではこの走査ゲートを `rogue_potions.magic_detection_can_scan()` で固定する。

`potions.c:quaff()` は効果処理後に `misc.c:call_it(&pot_info[obj->o_which])` を呼ぶ。`call_it()` は `oi_know` が立っていれば既存の `oi_guess` を消し、未判明かつ仮名ありならその仮名を維持する。Pyxel 版では potion 使用後の仮名更新を `rogue_potions.call_it_guess_after_use()` で固定する。`sticks.c:do_zap()` は非杖を選んだ場合に `after=FALSE` としてターンを消費しないため、Pyxel 版の方向確定後処理も `zap_stick()` の戻り値でターン消費を分ける。

treasure room（俗称モンスターハウス）は `new_level.c:138, 180-231` の `treas_room()` を基準にする。`put_things()` で 1/20 の階に発生し、通常物資は `MAXOBJ=9` 回の `rnd(100)<36` 試行で配置し、Amulet 所持後に上階へ戻る場合は `level < max_level` で新規物資を置かない。通常部屋の gold とモンスターは `rooms.c:do_rooms()` を基準にし、gold は各部屋 `rnd(2)==0` かつ Amulet 上昇中ではない場合に `GOLDCALC` 後 `find_floor()` で配置し、部屋モンスターは gold あり80%、なし25%で発生する。`rooms.c:find_floor()` は候補一覧から選ばず、`rnd_room()` と `rnd_pos()` を成功まで繰り返す。Pyxel版も room gold、通常物資、treasure room item / monster、Amulet、部屋モンスターの配置でこの乱数試行式を使い、`monst=FALSE` は通常部屋では `FLOOR`、`ISMAZE` では `PASSAGE` を待つ。`new_level.c:new_level()` は `put_things()` 後に traps、stairs、hero を置くため、Pyxel版も通常物資 / Amulet、trap、stair、hero の順で配置し、stairs と hero は `find_floor()` 相当で選ぶ。gone room は `rnd(4)` 回の重複あり選択、dark/maze は `rnd(10)<level-1` と `rnd(15)==0` を `rogue_rooms.py` へ分離する。treasure room は `MINTREAS=2` / `MAXTREAS=10` 個のアイテムを埋めたうえで、次階層相当のモンスターを `ISMEAN` 付きで多数配置する。部屋内モンスターは `give_pack()` で持ち物も持つ。Pyxel 版では `rogue_dungeon.py` に treasure room の発生ゲート、`MINTREAS` / `MAXTREAS` / `MAXTRIES`、通常物資試行、Amulet 上昇中ゲート、個数計算を分離し、`Game` 側は配置と既存 `make_item()` / `Monster` 生成の接続だけを担当する。

`give_pack` は Rogue 5.4.4 `monsters.c:give_pack()` と `extern.c:monsters[]` の `m_carry` を基準にする。Pyxel版では `MonsterSpec.carry` に A-Z の値を持たせ、通常モンスター生成時に `level >= max_level && rnd(100) < m_carry` 相当を `rogue_monsters.should_give_pack()` へ小分割し、`make_item()` を `Monster.pack` に保持し、`fight.c:remove_mon(..., TRUE)` 相当として倒した時に床へ落とす。Leprechaun は `fight.c:killed()` に合わせ、`level >= max_level` で死亡時に `GOLDCALC` gold を pack へ追加し、`save(VS_MAGIC)` 成功時はさらに4回分を足してから床へ落とす。wandering monster は原作 `monsters.c:wanderer()` と同じく `give_pack()` を呼ばない。treasure room 内モンスターは `treas_room()` の一時的な `level++` 相当により、次階層 depth で `give_pack()` を呼ぶ。`rooms.c:do_rooms()` は room gold も `lvl_obj` に `attach()` するため、`chase.c:find_dest()` の carry monster 目的地候補と `do_chase()` の到達時 pack 収集は scare scroll 以外の gold を含む。room gold と部屋モンスターは各部屋の `draw_room()` 直後に置き、`passages.c:do_passages()` と `new_level.c` の `no_food++` より前に処理する。gold item の名前は `things.c:inv_name()` の `GOLD` 分岐に合わせ、個数ではなく gold value として表示する。

ring の未識別 stone は `init.c:init_stones()` を基準にし、`rnd(NSTONES)` の重複回避で `r_stones[]` を選び、対応する `stones[].st_value` を `ring_info[].oi_worth` へ加算する。Pyxel 版では `IdentTable.rstones` と `IdentTable.rworth` を同時に初期化し、`rip.c:total_winner()` 相当の勝利 pack worth では加算後の `rworth` を使う。ring / stick の半額判定は type の `oi_know` ではなく個体の `obj->o_flags & ISKNOW` に合わせ、売却後の type 識別更新はスコア計算結果へ影響させない。

daemon / fuse 期間管理は `daemon.c`, `daemons.c`, `main.c:fuse()/lengthen()/extinguish()` を基準にする。現行は個別 `int` カウンタで近似しているが、`doctor / stomach / runners / swander / rollwand / sight / unsee / unconfuse / unblind / unhaste / unring / land / nohaste` を統一インフラで扱うことで、`potion of haste self` の重ね掛け、`ring of regeneration` の同時発動、wandering monster の `WANDERTIME=spread(70)` などを Rogue 5.4.4 と同じターン消費で再現できる。`doctor()` と `stomach()` の純ロジックは `rogue_daemons.py` の `doctor_tick()` / `stomach_tick()` に小分割し、`Player` はリング食料消費や再生回数など周辺値を渡して委譲する。`doctor()` は HP が最大でも `quiet++` を先に行い、レベル8以上の回復量は `rnd(level-7)+1`、回復判定後に `max_hp` へ丸め、HPが変わった場合は `quiet=0` に戻す。`stomach()` は `food_left -= ring_eat(LEFT) + ring_eat(RIGHT) + 1 - amulet` とし、`food_left <= 0` で既に `no_command` 中なら新たな faint 期間を加えず、faint 期間は `rnd(8)+4` とする。`command.c:command()` に合わせ、BEFORE daemon/fuse は `no_command` 減算より前に実行し、haste 中も `ntimes++` の2回行動ループへ入る前、Pyxel側では前半行動で1回だけ実行する。`no_command` が減算で0になった時は `you can move again` を出す。

`stomach()` の餓死判定は `if (food_left-- < -STARVETIME)` なので、餓死するターンでも `food_left` は先に1減る。`rogue_daemons.stomach_tick()` でもこの post-decrement を再現する。faint 判定は `rnd(5)`、faint 期間は `rnd(8)+4` として `RogueRng.rnd()` 経由に統一する。

初期移行として `rogue_daemons.py` に `DelayedActionTable` / `FuseList` / `DaemonList` を追加し、`daemon.c:fuse()`, `lengthen()`, `extinguish()`, `do_fuses(AFTER)`, `start_daemon()`, `kill_daemon()`, `do_daemons()` と比較できる境界を作る。daemon と fuse は原作同様に共通の `MAXDAEMONS=20` スロットを使い、同名の重複登録を許し、`kill_daemon()` / `extinguish()` は先頭1件だけ消す。まず `potions.c:P_HASTE` / `misc.c:add_haste(TRUE)` / `daemons.c:nohaste()` を接続し、haste 中は `command.c:command()` の `ntimes++` 相当として、2回のプレイヤー行動につき1回だけ AFTER fuse、空腹、モンスター行動を進める。haste self の二重使用は `rnd(8)` の `no_command` を加え、`nohaste` fuse を消して失神メッセージを出す。`potions.c:P_CONFUSE`, `P_SEEINVIS`, `P_LSD`, `P_BLIND`, `P_LEVIT`, `P_MFIND` は `do_pot()` / `turn_see()` 相当として未発動時に `fuse()`、発動中の再使用で `lengthen()` する。`swander` / `rollwand` は `rogue_daemons.py` の `swander()` / `rollwand()` へ小分割し、`main.c` の初回 `fuse(AFTER)` と `daemons.c` の `start_daemon(BEFORE)` / 再予約 `fuse(BEFORE)` に合わせる。doctor、stomach、runners など daemon 系は、後続タスクで同じ delayed action 境界へ段階移行する。

`main.c` の初期 delayed action 登録順は `start_daemon(runners)`, `start_daemon(doctor)`, `fuse(swander, WANDERTIME, AFTER)`, `start_daemon(stomach)` とする。Pyxel 版でも共通スロット順をこれに合わせ、後続の `d_slot()` 相当の再利用順を原作と比較できるようにする。`potions.c:P_LSD` は初回 hallucination で `start_daemon(visuals, BEFORE)` し、`daemons.c:come_down()` で `kill_daemon(visuals)` する。`daemons.c:visuals()` は visible item、未記録 stairs、visible/detected monster の順に `rnd_thing()` / `rnd(26)` を消費するため、Pyxel 版でも draw 時に乱数を引かず、BEFORE daemon で hallucination 表示キャッシュを更新する。盲目中は `cansee()`/`see_monst()` 対象を更新しないが、`SEEMONST` による detected monster は原作通り `rnd(26)+'A'` で更新する。

`daemons.c:sight()` は blind を解除するときに `extinguish(sight)` も行う。Pyxel 版でも `potions.c:P_HEALING`, `P_XHEAL`, `P_SEEINVIS` から `sight()` を通し、blind 解除後に古い `sight` fuse が残らないようにする。

`daemons.c:unsee()` は invisible monster の画面復元後に `CANSEE` を解除する。Pyxel 版では描画を次フレームの視界更新へ委ね、ゲーム状態としての see invisible potion 期間だけを `rogue_daemons.unsee_state()` で解除する。see invisible ring は別条件として扱うため、potion fuse 終了後も ring 装備中なら不可視視認は残る。

`daemons.c:land()` は levitation 解除時に hallucination 中かどうかで `choose_str()` の文言を分ける。Pyxel 版でも `rogue_daemons.land_state()` に分け、通常時は `you float gently to the ground`、hallucination 中は `bummer!  You've hit the ground` を出す。

`potions.c:turn_see()` は `turn_off` で `SEEMONST` を解除し、それ以外では付与する。Pyxel 版では一時表示の残り期間を `see_monsters` に保持し、ON/OFF の状態変更は `rogue_potions.turn_see_state()` へ寄せる。`turn_see(FALSE)` の戻り値は、`see_monst()` でまだ見えていなかった monster を一時表示したかどうかなので、`P_MFIND` の感知メッセージは `rogue_potions.turn_see_adds_new()` で判定する。`P_MFIND` は `do_pot()` 経由ではなく、使用ごとに `fuse(turn_see, TRUE, HUHDURATION, AFTER)` を追加する。再使用時も `lengthen()` せず、原作の delayed action スロット重複を保つ。

Wizard モード（`wizard.c` / `command.c` の `+` トグル、CTRL-D/A/F/T/E/C/X/~/I 系）は、忠実度監査に必要な周辺機能として `../TODO.md` Phase 7 に記録する。ゲーム中セーブは Settings の `Save and quit` とキーボード `S` から同じ確認画面を開き、タイトルの `CONTINUE` で再開する。原作の起動時引数そのものではなく、中断セーブの意味論を優先する。
## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

探索済みだが現在視界外のセルでは、地形と床上アイテムは表示し続け、モンスターは表示しない。これは元祖ローグの「見えた地図上のもの」と「現在見えている動くもの」を分ける表示に寄せるためで、ミニマップや敵一覧のような追加情報UIは使わない。

投擲は Rogue 5.4.4 のゲームロジック準拠を優先し、命中・落下・ターン経過は投げた時点で即確定する。一方で Pyxel Rogue の表示補助として、投げたアイテムが通過セルを数フレーム移動して見える非ブロッキングのアニメーションだけを重ねる。Pyxel Web 互換のため、sleep や待機ループでゲーム更新を止めない。
## 鑑定・命名・発見リスト

Rogue 5.4.4 の鑑定状態は、種類単位の `obj_info.oi_know`、種類単位の仮名 `obj_info.oi_guess`、個体単位の `ISKNOW`、武器/防具の個体ラベル `o_label` を分ける。参照元は `rogue.h:obj_info/ISKNOW`、`things.c:inv_name()/nameit()/print_disc()`、`wizard.c:whatis()/set_know()`、`command.c:call()`、`misc.c:call_it()`。

現行 Pyxel 版は `IdentTable.pk/sk/rk/wk`、`Item.known`、`oi_guess` 相当、`c` call、`D` discovered list、weapon / armor 個体ラベル `o_label` まで実装済み。ring / stick は、種類判明後も個体 `ISKNOW` 相当の `Item.known` が立つまで補正値・チャージを隠す。

実装時は `potions.c:quaff()/do_pot()`、`scrolls.c:read_scroll()` の各分岐で「判明する/しない」を期待値テスト化してから直す。Pyxel 都合で文字入力を簡略化しても、正式鑑定と仮名は別状態として保存する。詳細な監査メモは TODO とテスト名へ寄せる。
## 元祖ローグのソース参照先

Rogue 5.4.4 C ソースの参照元は https://github.com/Davidslv/rogue とする。

ローカル作業では `vendor/` 配下を参照元置き場にする。`vendor/` は `.gitignore` で除外し、Pyxel Rogue 本体のリポジトリには含めない。Rogue 5.4.4 は `vendor/rogue544/` を標準参照先にする。セットアップは次のどちらかで行う。

```bash
mkdir -p vendor
git clone https://github.com/Davidslv/rogue.git vendor/rogue544
```

または、既に隣接ディレクトリなどに clone 済みの場合はコピーしてよい。

```bash
mkdir -p vendor
cp -R ../260416_rogue544 vendor/rogue544
```

忠実度に関わる変更では、`vendor/rogue544/` の該当ファイルを `rg` / `sed` で必要箇所だけ確認し、参照したファイル名・関数名・定数名をテスト名、コメント、またはこの文書から追えるようにする。原作ソース本文の長い引用は避け、根拠としては短い関数名・テーブル名・行動仕様を記録する。
