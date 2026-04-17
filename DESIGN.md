# DESIGN.md — 設計判断の記録

## プロジェクトの発端

黎明期の名作を Pyxel で再現する企画から、ローグをコントローラ操作対応で作る方向に決定。その後「過剰にオーバースペックな Pyxel 版・元祖ローグ」にコンセプトが発展した。

最終目標は、Pyxel 版をクリアしたら本物の Rogue 5.4.4 をクリアしたと言える状態にすること。Rogue 5.4.4 準拠を主軸にし、将来的にはフォント切替 / 日英切替 / BGM / バージョン選択（3.6 / 5.2 / 5.4.4）を検討する。

実装は、原作と同じロジックか検証できる構造を優先する。表示・入力・移植性の都合で Pyxel 向けの実装差分が必要な場合も、ゲームロジックは原作と照合しやすく保つ。

短期的にはバージョン選択機能の優先度を下げ、Rogue 5.4.4 を単一ターゲットとして忠実度を上げる。将来の Rogue V5 系を含むバージョン切替に備えて、ゲームロジック、文言、入力・描画の依存方向は分離しやすく保つが、今はバージョン別分岐を先行追加しない。

## Rogue表記方針

詳細なバージョンを書く場合は `Rogue 5.4.4` とし、メジャーバージョンや系統を強調する場合は `Rogue V5` とする。詳細バージョンを途中で止めた短縮表記は新規に使わない。

## ゲームメカニクス準拠の運用

ゲームメカニクスは Rogue 5.4.4 C ソースを一次情報にする。確率、生成数、ターン消費、状態異常、攻撃判定、アイテム効果、罠、隠し要素、モンスターAIなど、ゲーム状態に影響する挙動は、実装前に該当する原作の関数・定数・テーブルを確認する。推測、現代ローグライクの慣習、Rogue2.Official、既存 Pyxel 実装はゲーム挙動の正解にしない。

Rogue2.Official は日本語表現と用語の準拠元であり、確率やターン処理などのゲームロジックの正解ではない。既存 Pyxel 実装が Rogue 5.4.4 と食い違う場合は、既存挙動ではなく Rogue 5.4.4 を優先する。

Pyxel 向けの差分は、表示、入力、移植UI、非ブロッキング演出など、ゲーム状態を変えない範囲に留める。ゲーム状態が原作と異なる差分をどうしても入れる場合は、原作との差、理由、影響範囲をこの文書へ記録してから実装する。

忠実度に関わる変更は、実装前に Rogue 5.4.4 の期待値テストを追加する。baseline テストは「壊れてほしくない現状」の保護に使い、原作と違う既知バグの正当化には使わない。実装コメントまたはテスト名から、参照した原作ファイル名・関数名・定数名を追えるようにする。

## README運用

README は外向け仕様、遊び方、公開リンク、実装概要の入口として扱う。仕様、操作、実装状況、実行方法、Web公開URL、ライセンスが変わる変更では、`README.md` と `README.en.md` の更新要否を確認し、必要なら同じ変更で同期する。

詳細な作業一覧は `TODO.md`、設計判断の経緯は `DESIGN.md` に置き、README には初めて見る人が遊び始めるための情報と概要だけを載せる。

## 対象環境

対象をデスクトップに限定せず、Python/Pyxel 本体に加えて Pyxel Web でも遊べることを前提にしたい。ブラウザ、SteamDeck、中華ゲーム機などでも破綻しない入力・画面構成を重視する。

512×320 画面を新しい基準にし、48×24 マップ、3×3セクターグリッドを常時全表示する方針にする。移植性のため、レイアウト定数は将来的に画面サイズから再計算できるようにする。

## 画面レイアウト

目標レイアウトは、48×24 のメインASCIIダンジョン表示を常時すべて見せる。現行セル 7×12px なら描画領域は 336×288px になり、512×320 画面の左側に収める。右側にはサイドHUD、下部には短いメッセージログを置く。

ミニマップと全体マップUIは廃止する。元祖ローグでは、見えているASCIIダンジョン表示そのものが地図であり、別レイヤーの地図UIを足すと探索体験が現代ローグライク寄りになりすぎるため。探索情報はメインASCII表示に集約する。

現代的UIは探索情報を増やすためではなく、状態確認を読みやすくするために使う。右サイドHUDには HP、Str、AC、Food、装備、状態異常、Depth、Turn、Gold、入力モードなどをまとめる。常時インベントリ全表示、敵一覧、周辺警告レーダーのような便利すぎる情報は通常画面には置かない。詳細な履歴表示は後続のメッセージ履歴スクロールで扱う。

Full Map / 拡大全体マップは現方針では復活させない。48×24 メインASCIIを常時全表示することで、地図確認の役割は本体表示へ統合済みとみなす。将来マップ寸法を変更する場合も、まずメインASCII表示の可読性と探索済みセルの扱いを調整し、別レイヤーのマップUIを安易に追加しない。

## 操作体系

当初は GB 版「風来のシレン」の D-pad + 少数ボタン操作を参考にした。現方針では、より携帯機・ブラウザ・Pyxel Web 向けに、A/B/Start/Select + D-pad を基本操作にする。

```
D-pad                 通常は8方向移動
Start短押し          斜め補助モード / 8方向移動モード（通常モード）のトグル
斜め補助モード中      左上/右上/右下/左下の同時押しだけを NW/NE/SE/SW として扱う
A                     決定 / 拾う / 階段 / 空押し時は正面1マス search
B短押し               キャンセル / メニュー
B長押し + D-pad       ダッシュ
Select(Back)          補助メニュー（Inventory / Help / Search / Trap / Pickup / Language）
Select+A              周囲8マス search
Select+B              quick throw（方向を選んでからアイテム選択）
Select+D-pad          発見済み罠の種類確認（^ + 方向相当）
A+B                   足踏み
X/Y/L/R               当面は必須操作にしない。将来のショートカット予約
```

Start長押しは携帯機側の電源OFF等に割り当てられることがあるため、ゲーム操作として依存しない。斜め補助モードは、SteamDeck、ブラウザ、携帯機で斜め入力を安定させるための移植UIとして扱う。通常時の8方向移動とは別扱いにし、斜め補助モード中は上下左右単体入力では移動しない。ただしこれはプレイ中の移動・ダッシュ・方向指定に限る。メニュー、アイテム選択、補助メニューのカーソル上下は UI 操作として扱い、斜め補助モード中でも上下単体入力を受け付ける。

B はダッシュ（ホールド）とキャンセル/メニュー（単押し）を兼務する。ダッシュ開始は `btnp()` ではなく現在ホールド中の方向で判定し、D-pad を先に押してから B、または B を先に押してから D-pad のどちらでも走り始められるようにする。`btn()` と `btnp()` の扱い、離した瞬間の誤発火には注意する。斜め補助モード ON/OFF はステータス欄に表示し、現在の入力モードが常に分かるようにする。

Select(Back) は補助メニューにしつつ、ゲームパッド向け chord レイヤーとしても扱う。Select+A は周囲8マス search を実行し、A空押しの正面1マス search と同じ A 系操作にまとめる。Select+B は Rogue 5.4.4 の `t` コマンドに寄せ、方向を選んでから投げるアイテムを選択する quick throw とする。Select+D-pad は Rogue 5.4.4 の `^` + 方向に相当する Trap Inspect とし、発見済み罠の種類を方向指定で確認する。ステータス、ヘルプ、search、Trap Inspect、自動拾い切替の入口は補助メニューにも残し、A/B/Start/Select + D-pad だけで主要操作を完結させる。マップは常時48×24で全表示するため、補助メニューには置かない。

A+B は足踏み専用にする。search を兼ねると足踏みが search の上位互換になり、Rogue 5.4.4 の `.` と `s` の意味が薄くなるため、周囲 search は Select+A または補助メニュー/キーボード `S` に分ける。A の空押しは、何もない場所での正面1マス search として扱い、探索の手触りを増やしつつ周囲 search とは区別する。

自動ピックアップは Rogue 5.4.4 の `pickup` オプション相当として扱い、デフォルトONにする。Select(Back) 補助メニューから ON/OFF を切り替え、OFF時は床上アイテムに乗ったことだけを通知し、Aで手動拾得する。拾得処理は手動/自動で共通化し、金は所持金へ直接加算、満杯時は `pack too full`、一度拾った `scroll of scare monster` は再拾得時に灰になる挙動を Rogue 5.4.4 の `pick_up()` に寄せる。

斜め入力は携帯機D-padで横→横+縦の順に入力イベントが分かれやすい。通常移動では単独方向の `btnp` を1フレームだけ保留し、次フレームに直交方向が押されたら斜め1回として確定する。斜め補助モード中は従来通り同時押し斜めだけを受け付け、上下左右単体では移動しない。メニュー系のカーソル操作は `dir_press()` とは別の上下入力として扱い、`diag_assist` と `dir_pending` の影響を受けない。

ダッシュ/走行は Rogue 5.4.4 の `command.c` / `move.c` / `misc.c` を参照し、`do_run()`, `do_move()`, `turn_ok()`, `look()` の挙動へ寄せる。通路のL字角では、前方が壁で左右どちらか一方だけに曲がれる場合、`turn_ok()` 相当の判定で方向転換して走り続ける。部屋内では Rogue 5.4.4 の `door_stop` 相当を常時ONとして扱い、壁沿いに走っているとき前方側の周囲に扉や分岐が見えたら停止する。

斜め移動・斜め近接攻撃・モンスターの斜め接触攻撃は Rogue 5.4.4 の `diag_ok()` 相当で判定する。斜め先そのものに加え、直交する2マスがどちらも通行可能なときだけ成立する。これにより、扉上や壁角から直交片側が壁になっている斜め先へは移動できず、そこにいるモンスターへの近接攻撃も発生しない。モンスター側も同じ制約を受ける。

HP自然回復と空腹は Rogue 5.4.4 の `daemons.c` にある `doctor()` / `stomach()` を基準にする。HPはターン経過で `quiet` が進み、低レベルではゆっくり、高レベルでは速く回復する。空腹は `HUNGERTIME`, `MORETIME`, `STOMACHSIZE`, `STARVETIME` の閾値を使い、食料切れ直後から毎ターンHPを削る挙動にはしない。

## モンスターAI

モンスターAIは Rogue 5.4.4 の `monsters.c`, `chase.c`, `fight.c`, `move.c` を基準にする。単純な「視界内ならマンハッタン距離で近づく」処理は原作と大きく異なり、扉上のプレイヤーへ近づけない、Rattlesnake / Ice monster の特殊攻撃が弱すぎる、非起床モンスターまで常時接近する、といったズレを生むため採用しない。

現行実装では `runto()` 相当で `Monster.running` を立て、running でないモンスターは基本的に移動しない。プレイヤーがモンスターを攻撃した場合や、視界に入った mean monster が `wake_monster()` 相当で起きた場合、`scroll of aggravate monsters` を読んだ場合に追跡を開始する。部屋所属は通常表示用の `room_at()` とは別にAI用所属を持ち、部屋床、部屋外周、扉、通路を区別する。扉上の actor は通路側として扱い、扉そのものを部屋出口としても扱えるようにして、扉上のプレイヤーやモンスターが追跡処理から孤立しないようにする。

追跡は `chase()` 相当として、周囲8マスから `diag_ok()`、通行可、他モンスター占有、床上 `scroll of scare monster` を避ける条件を満たす候補を選び、Rogue 5.4.4 の `dist()` と同じ二乗距離で目的地に近づく。別部屋にいる場合は、まず所属部屋の出口へ向かう。現時点では通路番号は完全再現せず、通路は単一の corridor 所属として扱う。Bat、Phantom、confused monster は原作同様にランダム移動を混ぜ、flying monster は距離がある場合に追加移動する。

特殊攻撃は `fight.c` の命中後分岐へ寄せる。Ice monster は命中時に `no_command += rnd(2)+2` 相当でプレイヤーを凍結させ、Rattlesnake は `save(VS_POISON)` 失敗時に Strength を下げる。Aquator、Leprechaun、Nymph、Medusa、Troll、Vampire、Wraith、Venus Flytrap も、既存の簡略フラグを維持しつつ原作の発動タイミングへ寄せる。プレイヤーの行動不能は、sleep/freeze/faint 系の `no_command`、bear trap の `no_move`、Venus Flytrap の `held_by` に分ける。

モンスターの戦闘値は Rogue 5.4.4 `extern.c:monsters[]` の `s_lvl`, `s_arm`, `s_dmg`, `s_exp` を名前付き `MonsterSpec` として持つ。tuple の位置引数で `level` と `armor` を取り違えると、プレイヤー命中率や plate mail の防御力が大きく壊れるため、代表モンスターと `fight.c:swing` の境界値をテストで固定する。Hobgoblin は `level=1`, `armor=5`, `damage="1x8"`, `exp=3`、Ice monster は `level=1`, `armor=9`, `damage="0x0"`, `exp=5` を監査対象にする。

残差分として、通路番号付き passages、Xeroc のアイテム擬態、指輪・杖・cancellation とAIの完全連携は未完了。暗い部屋、迷路部屋、gone room は生成と視界への接続を先行実装済みで、今後も原作関数を確認しながらアイテム・モンスター配置やAI所属を詰める。

## 武器メカニクス

武器は Rogue 5.4.4 の `weapons.c:init_dam`, `fight.c:roll_em`, `things.c:inv_name/new_thing`, `scrolls.c:S_ENCH` を基準にする。武器は命中補正 `hit_plus` とダメージ補正 `dam_plus` を別々に持ち、表示も `+1,+1 mace (weapon in hand)` のように2値で出す。近接・投擲とも Strength の命中/ダメージ補正を通し、arrow + bow のような launcher 補正も原作に合わせて合算する。

防具は当面既存の `ench` 表現を維持する。ring of dexterity / increase damage は未実装だが、後で `fight.c:roll_em` 相当に加算できるよう、武器計算は小さな helper に分けている。

## フォント

Pyxel 標準フォント 4×6px は小さく、ASCII ローグの可読性に不安があった。`pyxel.Font(path)` で BDF 読込可能と判明し、現行では Pyxel 同梱の `umplus_j10r.bdf` を標準にしている。ASCII 6px / CJK 10px / 7187文字で日本語にも対応する。

```python
import os
font = pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__),
                                "examples", "assets", "umplus_j10r.bdf"))
```

当面は `umplus_j10r.bdf` を使うが、将来的なフォント選択は許容する。ただしローグの画面表示に向く可読性を必須条件にする。

## 日本語 / 英語切替

ゲーム挙動は Rogue 5.4.4 準拠、日本語表現は Rogue2.Official 準拠として扱う。Rogue2.Official は日本語メッセージ、アイテム名、モンスター名、ヘルプ文言などの表現ソースであり、ゲームロジックや確率・ターン処理の正解としては使わない。

参照元:

- https://github.com/suzukiiichiro/Rogue2.Official
- `mesg_J`: 日本語メッセージ・用語
- `mesg_E`: 英語メッセージとの対応確認

現行実装では `TextCatalog` と `LANG_EN` / `LANG_JA` を導入し、`PYXEL_ROGUE_LANG=ja pyxel run rogue.py` で日本語表示を選べる入口を用意した。Phase 1 として、ゲーム中も Select(Back) 補助メニューの Language から日英をトグルできる。言語切り替えはターンを消費せず、過去ログは再翻訳しない。切り替え後の新規ログ、メニュー項目、アイテム名などの表示だけが現在言語に従う。

まだ全メッセージ辞書化は完了していない。歓迎文、空腹、探索、戦闘、拾得、メニュー項目、アイテム名・モンスター名の代表範囲から段階的に `TextCatalog` 経由へ移行している。HUD、Inventory、Help、Death などの直書き英語は後続タスクで辞書化する。

メッセージ分離は段階的に進める。Phase 4 以降で追加する新規ログ・UI文言は直書きせず `TextCatalog` 経由にし、既存文言は関連機能を触るタイミングで移行する。先に巨大な翻訳リファクタを行うより、指輪、杖、罠、Amulet、勝利、search結果など新規要素の文言を増やす時点で辞書化することを優先する。

翻訳層はゲーム状態を変えない表示レイヤーとして扱う。同じ seed と同じ操作なら、英語 / 日本語の違いでプレイヤー位置、所持品、ターン、HP、モンスター配置などのゲーム状態が変わってはいけない。

## カメラ

現行48×24マップを常時全表示する目標レイアウトでは、通常プレイ中のカメラスクロールは不要になる。カメラ処理は、将来マップサイズを変更した場合や表示タイル数がマップより小さい場合にも破綻しない互換処理として残す。

## ダンジョン生成

元祖ローグの3×3セクターグリッドアルゴリズムを再現。現行では48×24マップを16×8セクターに分割し、Rogue 5.4.4 と同じ sector index 0..8 の固定順で9個の `Room` を作ったうえで、`rooms.c` 相当の `ISGONE` / 暗い部屋 / `ISMAZE` フラグを割り当てる。通路は全隣接セクターを無条件に接続せず、`passages.c` の `do_passages()` と同様に9部屋を結ぶ spanning tree 8本を作り、追加で `rnd(5)` 回だけ未接続の隣接エッジを掘る。通常部屋、迷路部屋、gone room はこの選ばれた通路グラフ上で接続し、flood fill は互換用の到達保証として残している。

マップ寸法は現行値であり固定仕様ではないが、原作ロジックとの比較可能性を崩さないことを優先する。

通路生成は Rogue 5.4.4 C ソースの `passages.c` を参照し、推測で似せない。特に `do_passages()` が部屋グラフを作り、`conn()` が接続方向に応じて壁上のドア位置を選び、`door()` が部屋の出口を記録し、`putpass()` が通路を掘る責務分担を基準にする。

部屋フラグは Rogue 5.4.4 `rooms.c` の `rnd(4)` 個の `ISGONE`、`rnd(10) < level - 1` による暗い部屋、同分岐内の `rnd(15)==0` による `ISMAZE` を基準にする。暗い部屋と迷路部屋は部屋全体を一括可視化せず、周囲視界のみで探索する。gone room は壁やドアを置かず、通路セルとして接続する。通路の曲がり点はドア直後の壁沿いセルを避け、部屋の水平壁に沿って長い通路が走らないようにする。

## Phase 4 の完成基準

「Pyxel版をクリアしたら Rogue 5.4.4 をクリアしたと言える」ための短期的な山場は Phase 4 とする。26階で Amulet of Yendor が出現し、Amulet 所持後に階段を上って1階へ帰還し、勝利状態へ到達できることを最小のクリア条件にする。

指輪、杖、罠、隠しドア、隠し通路、scroll of scare monster の床上効果は、単なるアイテム種類追加ではなく Rogue 5.4.4 の攻略判断を成立させる要素として扱う。特に search は、罠・隠しドア・隠し通路を発見するためのゲームロジック上の hook とし、A空押しの正面探索と Select+A / 補助メニュー / `S` の周囲探索を区別する。

Trap Inspect は Rogue 5.4.4 の `^` + 方向に相当するターン非消費コマンドとして扱う。未発見罠は確認対象にせず、search または踏んだ時に露出した `^` だけが種類表示の対象になる。ゲームパッドでは Select+D-pad を高速入力、補助メニューの Trap を発見しやすい入口にする。

罠と隠し要素の発生・発見は Rogue 5.4.4 の `new_level.c`, `passages.c`, `command.c`, `move.c` を基準にする。罠は `rnd(10) < level` の階層ゲートを通ったとき `rnd(level / 4) + 1` 個、最大 `MAXTRAPS` 個を部屋床へ隠して置く。隠し扉は `rnd(10)+1 < level && rnd(5)==0`、隠し通路は `rnd(10)+1 < level && rnd(40)==0` に寄せ、1階では生成されない。search は隠し扉 `rnd(5+probinc)==0`、罠 `rnd(2+probinc)==0`、隠し通路 `rnd(3+probinc)==0` で露出する。Pyxel版では hallucination が未実装のため、その `probinc` だけは状態実装時に追加する。

実装順は、search / 隠し要素 / 罠、指輪、杖と方向指定 zap、Amulet / 帰還勝利、既知の忠実度バグ修正を基本にする。各修正では Rogue 5.4.4 C ソースの関数・定数を先に確認し、必要なら期待値テストを追加してから実装を変える。

## 死亡画面とスコア

死亡画面はブラウザ・携帯機でのテストプレイを続けやすくする移植UIとして追加する。Depth、Level、Gold、Exp、Turn、死因を表示し、A または Start で新規ゲームへ戻れるようにする。

スコア履歴保存は死亡画面とは分ける。JSONによるハイスコア保存と履歴画面は Phase 7 の仕上げタスクとして扱う。

## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

探索済みだが現在視界外のセルでは、地形と床上アイテムは表示し続け、モンスターは表示しない。これは元祖ローグの「見えた地図上のもの」と「現在見えている動くもの」を分ける表示に寄せるためで、ミニマップや敵一覧のような追加情報UIは使わない。

投擲は Rogue 5.4.4 のゲームロジック準拠を優先し、命中・落下・ターン経過は投げた時点で即確定する。一方で Pyxel Rogue の表示補助として、投げたアイテムが通過セルを数フレーム移動して見える非ブロッキングのアニメーションだけを重ねる。Pyxel Web 互換のため、sleep や待機ループでゲーム更新を止めない。

## ファイル構成

現行実装は `rogue.py` 中心だが、単一ファイルは前提にしない。見通しがよく、Rogue 5.4.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。

分割する場合は、ゲームロジック、データテーブル、入力、描画、プラットフォーム差分の境界を意識する。

現時点では大規模分割よりも、依存方向を整える小さな整理を優先する。`Game` 内にはまだロジック、入力、描画、文言が同居しているため、まず `TextCatalog` とロジックテストで境界を作り、以後の機能追加時に必要な範囲から分離する。

## テスト方針

最初の一手は「最小テスト → 最小翻訳層 → baseline 拡充」とする。翻訳層はリファクタリングなので、最低限のテストで import / 初期化 / ダンジョン到達性 / 初期装備を守り、その後に翻訳層込みの baseline を増やす。

テストは標準ライブラリの `unittest` で実行できる。

```bash
python3 -m unittest
PYXEL_ROGUE_LANG=ja python3 -m unittest
```

baseline テストは「壊れてほしくない現状」を固定するためのもの。Rogue 5.4.4 と違う既知バグを正当化するためには使わない。忠実度修正では、Rogue 5.4.4 C ソースの該当関数・定数に基づく期待値テストを先に追加し、失敗を確認してから実装を直す。定数テーブルを触る変更では、代表値の監査テストを同じ変更に含め、参照した原作のファイル名・関数名・テーブル名をテスト名、コメント、または本文から追えるようにする。

## コミット方針

コミットメッセージは、直前に編集した最後の変更だけで決めない。前回コミットからの staged diff 全体を確認し、コード、テスト、設計文書を含む変更全体を表す件名にする。

コミット前には `git diff --cached --stat` を確認し、必要に応じて `git diff --cached` で内容を見る。複数の独立した変更が混ざっている場合はコミットを分ける。分けない場合でも、件名は実装された成果のまとまりを表し、断片的な作業名にしない。

## BGM（しろもふさん自動演奏ツール）

参照候補:

- しろもふさん自動演奏ツール: https://github.com/shiromofufactory/8bit-bgm-generator
- Pyxel組み込み例: https://github.com/hnsol/pyxel-hadegame の `pyxelhg/bgm/bgm_generator.py`

Pyxel サウンド / ミュージックへの組み込み方、Pyxel Web での鳴り方、モジュール化して import する方法を検討する。

## 元祖ローグのソース参照先

Rogue 5.4.4 C ソースの参照元は https://github.com/Davidslv/rogue とする。

ローカル作業では `vendor/rogue544/` を標準参照先にする。このディレクトリは `.gitignore` で除外し、Pyxel Rogue 本体のリポジトリには含めない。セットアップは次のどちらかで行う。

```bash
mkdir -p vendor
git clone https://github.com/Davidslv/rogue.git vendor/rogue544
```

または、既に隣接ディレクトリなどに clone 済みの場合はコピーしてよい。

```bash
mkdir -p vendor
cp -R ../260416_rogue544 vendor/rogue544
```

忠実度に関わる変更では、`vendor/rogue544/` の該当ファイルを `rg` / `sed` で必要箇所だけ確認し、参照したファイル名・関数名・定数名をテスト名、コメント、またはこの `DESIGN.md` から追えるようにする。原作ソース本文の長い引用は避け、根拠としては短い関数名・テーブル名・行動仕様を記録する。

## ロジックテスト用 mock 手順

現在は `tests/test_rogue_baseline.py` に Pyxel mock を置き、`python3 -m unittest` でロジックテストを実行できる。以下は REPL や単発検証で同じ考え方を使う場合の手順。

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
