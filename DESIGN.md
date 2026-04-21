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

## RNG とコア分離の進め方

Rogue 5.4.4 準拠作業の土台として、乱数入口は `rogue_rng.py` の `RogueRng` に集約する。`RogueRng.rnd(n)` は原作 `main.c:rnd(range)` 相当、`RogueRng.roll(number, sides)` は原作 `main.c:roll(number, sides)` 相当として扱う。Pyxel 版では現時点で C の `rand()` と seed 完全一致までは目標にしないが、ゲーム状態に影響する乱数呼び出しは `RNG` 経由にし、忠実度テストで差し替えや監査ができる形にする。

既存の `random.choice` / `random.shuffle` 相当の処理は、初回整理では Python 標準の挙動を維持する薄いラッパーとして残す。乱数消費順そのものを Rogue 5.4.4 の `rnd()` ベースへ寄せる必要がある箇所は、該当する原作関数を確認したうえで、その機能の忠実度修正として個別に扱う。

今後の大きな分割は一気に `core/` 化しない。未実装でしがらみが少ない指輪・杖を、最初の Pyxel 非依存ロジックの実例として追加する。指輪では `rings.c` と `things.c`、杖では `sticks.c` と方向指定 zap 周辺を参照し、効果処理、生成テーブル、識別、チャージ、装備/使用結果を Pyxel 入力・描画から切り離しやすい helper として作る。既存機能は触るタイミングで `swing`, `roll_em`, `do_passages`, `pick_one` など C 関数名に対応する小さな境界へ寄せ、`Game` から純ロジックが自然に抜ける形を優先する。

## README運用

README は外向け仕様、遊び方、公開リンク、実装概要の入口として扱う。仕様、操作、実装状況、実行方法、Web公開URL、ライセンスが変わる変更では、`README.md` と `README.en.md` の更新要否を確認し、必要なら同じ変更で同期する。

詳細な作業一覧は `TODO.md`、設計判断の経緯は `DESIGN.md` に置き、README には初めて見る人が遊び始めるための情報と概要だけを載せる。

## 対象環境

対象をデスクトップに限定せず、Python/Pyxel 本体に加えて Pyxel Web でも遊べることを前提にしたい。ブラウザ、SteamDeck、中華ゲーム機などでも破綻しない入力・画面構成を重視する。

Pyxel Web Launcher で GitHub branch を指定して起動確認する場合、branch 名には `/` を使わない。Launcher の `run=owner/repo/branch/path` 形式では、`codex/foo` のような slash 付き branch 名が path と誤解されることがあるため、Webで確認する開発branchは最初から slash なしで作る。

Rogue 5.4.4 準拠のため、内部ダンジョン座標は `rogue.h` の `NUMCOLS=80`, `NUMLINES=24`, `STATLINE=NUMLINES-1` を基準にする。`move.c:do_move()` の境界条件と同じく、地形・通路・部屋・プレイヤー移動の主領域は `x=0..79`, `y=1..22` とし、`y=0` はメッセージ行相当、`y=23` はステータス行相当としてゲーム地形を置かない。

表示は Pyxel 向け UI として分離する。現在は 80桁の Rogue 5.4.4 ダンジョン領域を優先し、576×360 の 16:10 寄り画面で `80×22` のプレイ領域、右HUD、下ログを表示する。移植性のため、レイアウト定数は将来的に画面サイズから再計算できるようにする。

## 画面レイアウト

目標レイアウトは、Rogue 5.4.4 と同じ `80×24` 論理座標のうち、地形・移動領域である `80×22` をメインASCIIダンジョン表示として扱う。現在はセル 6×12px で描画領域 480×264px とし、576×360 画面の左側に収める。右側には細いサイドHUD、下部には7行のメッセージログを置く。

576×360 レイアウトでは右HUD幅が約80pxになるため、HUDは詳細表示ではなく状態サマリとして扱う。装備欄は `W +1,+1 2H sw` / `A +2 plate` のような短縮名を使い、日本語でも `W +1,+1 両手剣` / `A +2 鋼鉄` のように短く収める。正式な装備名と詳細は Inventory 側で確認する。

ミニマップと全体マップUIは廃止する。元祖ローグでは、見えているASCIIダンジョン表示そのものが地図であり、別レイヤーの地図UIを足すと探索体験が現代ローグライク寄りになりすぎるため。探索情報はメインASCII表示に集約する。

現代的UIは探索情報を増やすためではなく、状態確認を読みやすくするために使う。右サイドHUDには HP、Str、AC、Food、装備、状態異常、Depth、Turn、Gold、入力モードなどをまとめる。常時インベントリ全表示、敵一覧、周辺警告レーダーのような便利すぎる情報は通常画面には置かない。詳細な履歴表示は後続のメッセージ履歴スクロールで扱う。

テストプレイ中に実行中の改訂を識別しやすくするため、右HUDタイトルは `Rogue V5 YYMMDDHHMM` 形式の手動更新ビルド表記を含める。表示、入力、ゲームロジック、ダンジョン生成など、遊んで違いが分かる変更を入れた場合は同じ変更で `UI_BUILD` を更新する。これはゲームメカニクスではなく開発・テスト用の表示補助として扱う。

HPバーの被ダメージ色はフレーム数ではなく、HP低下を検出したターン中だけ残す。次のターンへ進んだら通常表示に戻すことで、Pyxel の描画フレームレートや環境差で消える速さが変わりすぎないようにする。

Full Map / 拡大全体マップは現方針では復活させない。Rogue 5.4.4 の地形・移動領域をメインASCII表示へ集約することで、地図確認の役割は本体表示へ統合済みとみなす。将来マップ寸法や画面サイズを調整する場合も、まずメインASCII表示の可読性と探索済みセルの扱いを調整し、別レイヤーのマップUIを安易に追加しない。

## 将来方針：GBC 美学寄せと 360x240 移行

この方針は Rogue 5.4.4 再現（Phase 4）が一段落した後に着手する将来計画として記録する。現時点ではゲームメカニクスの忠実度を最優先とし、本方針に基づく実装は行わない。Rogue 5.4.4 再現の過程でも、後続のインタフェース刷新を困難にする方向の設計判断（解像度依存のハードコード増加、入力処理の散在）は避ける。

Pyxel で作っているプロジェクトのアイデンティティを活かすため、携帯機 GBC を参照点としたインタフェースへ寄せる。参照するのは配色、情報密度、音の簡素さ。これは Rogue 5.4.4 の「情報を読ませる」性質と相性がよく、8bit BGM Generator のランダム生成音とも噛み合う。

情報デザインは Ghost Babel を参考にする。右側への情報寄せ、渋い配色、記号で読ませる画面構成は、本体ASCIIダンジョンを汚さずに状態確認を拡充するうえで有効。ただし Ghost Babel の音楽は再現しない。ミリタリー感、常時ミニマップ前提、派手な数字UIなどメタルギア文法そのものは持ち込まず、**Ghost Babel の整理のしかたを借りたローグ**を目指す。

解像度は現行の 576×360 から **360×240** へ移行する。Steam Deck（1280×800）で3倍整数スケールすれば 1080×720 となり左右の黒帯で収まる。ブラウザや PC でも整数倍スケールが綺麗に出る。移行時は 80×24 論理座標を維持したままタイル寸法、右HUD幅、下ログ行数を再計算する。可変画面/レイアウト再計算が完了してから本移行に着手する。

パレットは **32 色**（GBC の BG レイヤー最大 = 8パレット×4色 に対応）。`rogue.py` の `GBC_PALETTE` 定数で定義済み。基調は青灰（壁・廊下）と緑（部屋床）の寒色低彩度。警告・戦闘時のみ赤（22番）、UI強調にシアン（27番）、金・階段に琥珀（29番）を使い、常時高彩度にしない。純白（31番）はカーソル・点滅限定。`pyxel.colors` へ実行時に適用する（`Game.__init__` 内）。

ただし現行パレットは雰囲気を優先しており、テストプレイ時の可読性検証が必要。次段階では 3〜5 種のパレット候補をデータとして定義し、起動時オプションまたはゲーム中オプションから切り替えて比較できるようにする。候補には現行の GBC 寄りテーマ、より高コントラストなテーマ、terminal 風や light 風テーマを含める。最終的にはテストプレイで最も読みやすい設定へ絞り込み、ユーザーが常時多数の表示設定を選ぶ形にはしない。

マップUIの扱いは、既存の「ミニマップと Full Map / 拡大全体マップは復活させない」方針を維持する。ただし、明示的な操作時のみフロア全体マップを**全画面オーバーレイ**として一時表示することは例外として許容する方向で検討する。表示範囲は `self.vis` が示す探索済みセルに限定し、未探索は非表示を原則とする。ターンは消費しない。常時表示UIや画面端ミニマップは引き続き採用しない。

入力割当は既存方針と同じく A / B / Start / Select + D-pad のみを使う。Start 長押しは携帯機側の電源OFF等に割り当てられるため依存しない。B 長押し+D-pad はダッシュで使用中のため避ける。マップオーバーレイのキー割当は着手時に決定し、Select 長押し、新規 chord、トグルなどを候補として比較する。

BGM は 8bit BGM Generator のランダム生成を前提とするが、階層ごとの固定シード化（曲として安定）か毎回ランダム（探索感を重視）かはプレイ感で決める。GBC 美学と相性を取り、短い・緊張感あり・勇ましすぎない・ループ耐性のあるパラメータ帯を優先する。

## オプション方針

オプション切替は、まず開発中の比較検証とテストプレイ補助として導入する。パレット、run 中の移動過程表示、レイアウト候補、入力補助など、プレイ感や可読性を比較したい項目は設定化してよい。

一方で、最終的な体験はコンシューマゲーム機寄りにする。PCゲームのように細かい設定を大量に残すのではなく、十分に検証したうえでベストな値を標準仕様として固定し、ユーザーに見せるオプションは最小限にする。

オプションは原則として表示、入力補助、保存先、通信、テスト用挙動に限定する。確率、ターン消費、モンスターAI、アイテム効果、罠、スコアなど、Rogue 5.4.4 の攻略判断に影響するゲームメカニクスはオプションで変えない。ゲーム状態に影響しない run 表示の省略や非ブロッキング演出の切替は許容するが、同じ操作列で到達するゲーム状態が変わってはいけない。

初期の設定基盤として `Settings` を導入し、言語、自動ピックアップ、パレット名、run 中間表示フラグを保持する。既存コードとの互換性のため `Game.lang` と `Game.auto_pickup` はプロパティとして残し、内部では `Game.settings` に委譲する。設定項目は表示・入力補助に限定し、Phase 4 の忠実度作業で扱うゲームメカニクスへは接続しない。

パレット比較用に `gbc`、`gbc_high_contrast`、`flexoki_light` の3候補を定義し、Select(Back) 補助メニューの Palette から循環切替できるようにする。切替は `pyxel.colors` へ即時反映する表示設定であり、ターン消費、RNG、プレイヤー状態、マップ、所持品、モンスター配置には影響させない。

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

Select(Back) は補助メニューにしつつ、ゲームパッド向け chord レイヤーとしても扱う。Select+A は周囲8マス search を実行し、A空押しの正面1マス search と同じ A 系操作にまとめる。Select+B は Rogue 5.4.4 の `t` コマンドに寄せ、方向を選んでから投げるアイテムを選択する quick throw とする。Select+D-pad は Rogue 5.4.4 の `^` + 方向に相当する Trap Inspect とし、発見済み罠の種類を方向指定で確認する。ステータス、ヘルプ、search、Trap Inspect、自動拾い切替の入口は補助メニューにも残し、A/B/Start/Select + D-pad だけで主要操作を完結させる。地図確認はメインASCII表示に集約するため、補助メニューには置かない。

キーボードは A/B/Start/Select 相当の最低限操作を維持したうえで、Rogue V5 の直打ちコマンドも衝突しない範囲で正式対応する。候補は `t` quick throw、`q` quaff、`r` read、`e` eat、`w` wield、`W` wear armor、`T` take off、`P` put on ring、`i` inventory、`?` help、`S` 周囲 search、`^` trap inspect とする。大文字コマンドは Shift+letter で扱う。`z` zap は現行の A 相当キー `Z` と衝突するため、裸の `z` へは割り当てず、`Shift+Z` や別キー、またはメニュー Zap の継続を実装時に比較する。直打ちコマンドは、メニュー/アイテム選択/方向指定オーバーレイ中には通常UI入力を優先し、プレイ中だけ発火させる。

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

特殊攻撃は `fight.c` の命中後分岐へ寄せる。Ice monster は命中時に `no_command += rnd(2)+2` 相当でプレイヤーを凍結させ、Rattlesnake は `save(VS_POISON)` 失敗時に Strength を下げる。Aquator、Leprechaun、Nymph、Medusa、Troll、Vampire、Wraith、Venus Flytrap も、既存の簡略フラグを維持しつつ原作の発動タイミングへ寄せる。`ISCANC` 相当の `cancel` は命中後特殊攻撃、Medusa の `wake_monster()` 視線、再生、Dragon breath などの特殊能力入口で必ず確認する。プレイヤーの行動不能は、sleep/freeze/faint 系の `no_command`、bear trap の `no_move`、Venus Flytrap の `held_by` に分ける。

モンスター状態フラグは `rogue_monsters.py` を Pyxel 非依存の対応表・小 helper とし、Rogue 5.4.4 `rogue.h` の `ISHASTE` / `ISSLOW` / `ISCANC` / `ISINVIS` / `CANHUH` に対応する既存フラグ文字列を集中させる。`chase.c:move_monst()` に合わせ、`ISSLOW` は `t_turn` が真の手だけ通常追跡し、`ISHASTE` は追加追跡を行い、処理後に `t_turn` を反転する。`sticks.c:do_zap()` の `WS_HASTE_M` / `WS_SLOW_M` はこの helper 経由で、遅い相手を速めると `ISSLOW` 解除、速い相手を遅くすると `ISHASTE` 解除、そうでなければ該当フラグ付与とし、slow monster は `t_turn = TRUE` に戻す。

モンスターの戦闘値は Rogue 5.4.4 `extern.c:monsters[]` の `s_lvl`, `s_arm`, `s_dmg`, `s_exp` を名前付き `MonsterSpec` として持つ。tuple の位置引数で `level` と `armor` を取り違えると、プレイヤー命中率や plate mail の防御力が大きく壊れるため、代表モンスターと `fight.c:swing` の境界値をテストで固定する。Hobgoblin は `level=1`, `armor=5`, `damage="1x8"`, `exp=3`、Ice monster は `level=1`, `armor=9`, `damage="0x0"`, `exp=5` を監査対象にする。

残差分として、通路番号付き passages、Xeroc のアイテム擬態、Dragon breath、指輪・杖・cancellation とAIの完全連携は未完了。wandering monster は Rogue 5.4.4 の `main.c:fuse(swander, 0, WANDERTIME, AFTER)`, `daemons.c:swander()` / `rollwand()`, `monsters.c:wanderer()` を基準にし、`WANDERTIME` は `rogue.h` の `spread(70)` として扱う。暗い部屋、迷路部屋、gone room は生成と視界への接続を先行実装済みで、今後も原作関数を確認しながらアイテム・モンスター配置やAI所属を詰める。

## 武器メカニクス

武器は Rogue 5.4.4 の `weapons.c:init_dam`, `fight.c:roll_em`, `things.c:inv_name/new_thing`, `scrolls.c:S_ENCH` を基準にする。武器は命中補正 `hit_plus` とダメージ補正 `dam_plus` を別々に持ち、表示も `+1,+1 mace (weapon in hand)` のように2値で出す。近接・投擲とも Strength の命中/ダメージ補正を通し、arrow + bow のような launcher 補正も原作に合わせて合算する。

防具は当面既存の `ench` 表現を維持する。ring of dexterity / increase damage は `fight.c:roll_em` 相当に合わせ、装備中武器での近接攻撃に限って加算する。

装備変更は Rogue 5.4.4 の `armor.c:wear()` と `weapons.c:wield()` を分けて扱う。armor は `cur_armor != NULL` の場合に wear を拒否し、先に take off する必要がある。weapon は `weapons.c:wield()` が `dropcheck(cur_weapon)` を通るため、現在武器が cursed でなければ持ち替え可能であり、Pyxel 版でも自動置換自体は差分として扱わない。

呪い生成確率は `things.c:new_thing()` を基準にする。weapon は `rnd(100) < 10` で cursed、armor は `rnd(100) < 20` で cursed、一部 ring は `rnd(3)==0` で `o_arm=-1` かつ cursed、ring of aggravate monster と ring of teleportation は常時 cursed とする。生成時の weapon / armor の curse / enchant は原則未鑑定情報であり、Pyxel 版では `Item.known` を Rogue 5.4.4 の `ISKNOW` 相当として扱う。armor は `armor.c:wear()` に合わせ、装備した時点で `known=True` にして enchant / protection を表示する。ring の `ring_num()` と stick の `charge_str()` は種類識別後に表示する。

## 指輪メカニクス

指輪は Rogue 5.4.4 の `rogue.h:R_*`, `extern.c:ring_info[]`, `init.c:stones[]/init_stones()`, `things.c:new_thing()/inv_name()/dropcheck()`, `rings.c:ring_on()/ring_off()/ring_eat()/ring_num()`, `fight.c:roll_em()`, `daemons.c:doctor()/stomach()`, `scrolls.c:S_REMOVE` を基準にする。`rogue_rings.py` を Pyxel 非依存の最初の指輪ロジック境界とし、14種テーブル、ランダム石名、補正付き指輪生成、左右スロット、装備/解除、呪い、食料消費をここへ寄せる。

初回実装では、ゲーム状態に直結する protection / add strength / dexterity / increase damage / slow digestion / regeneration を接続した。protection はプレイヤーAC、防具と同じ低いほど強い値へ反映し、dexterity / increase damage は装備中武器での近接攻撃にだけ加算する。slow digestion と searching などの確率型食料消費は `rings.c:ring_eat()` の負値テーブルに合わせ、slow digestion は消費を減らす。regeneration は `daemons.c:doctor()` と同じく自然回復判定後に追加回復し、回復した場合は quiet をリセットする。

残りの指輪効果は、Rogue 5.4.4 の `command.c`, `rings.c`, `monsters.c`, `move.c`, `fight.c`, `potions.c` を確認して接続した。searching はターン後処理で手ごとに `search()` 相当を呼び、ターンを追加消費せず失敗時メッセージも出さない。teleportation は同じターン後処理で手ごとに `rnd(50)==0` のときテレポートする。see invisible は invisible monster の表示条件へ反映し、aggravate monster は装備時と装備中の monster creation で追跡を開始させる。stealth は `wake_monster()` 相当の mean monster 起床判定を抑制する。sustain strength は Rattlesnake / dart trap / potion of poison の Strength 低下を防ぎ、maintain armor は Aquator / rust trap などの `rust_armor()` 相当で錆びを防ぐ。adornment は装備時効果を持たず、装備しただけでは識別済みにしない。

UI差分として、原作の `gethand()` による左右手プロンプトは、携帯機向けメニュー操作では最初の空きスロットへ装備し、解除時は装備中アイテムを選ぶ方式にしている。左右どちらに装備されているかはインベントリ表示の `(on left hand)` / `(on right hand)` で確認できる。今後、左右指定が攻略上必要になる場面が出た場合は、ゲーム状態の差分を出さずに方向入力で手を選ぶUIへ拡張する。

see invisible potion は Rogue 5.4.4 `potions.c:P_SEEINVIS` / `do_pot()`, `misc.c:spread()`, `rogue.h:CANSEE/SEEDURATION`, `daemons.c:unsee()` に合わせ、`spread(SEEDURATION)` の間だけ invisible monster の表示条件へ反映する。`P_SEEINVIS` 末尾の `sight()` 相当により blind も解除する。残差分として、hallucination 中の invisible 表示、`turn_see()` 相当の全モンスター表示、Xeroc 擬態や wand cancellation との相互作用は、それぞれの機能実装時に改めて原作関数を確認して接続する。

## 杖メカニクス

杖は Rogue 5.4.4 の `rogue.h:WS_*`, `extern.c:ws_info[]`, `init.c:metal[]/wood[]/init_materials()`, `things.c:new_thing()/inv_name()/pick_one()`, `sticks.c:fix_stick()/do_zap()/charge_str()` を基準にする。初回実装では `rogue_sticks.py` を Pyxel 非依存の杖ロジック境界として追加し、14種テーブル、wand/staff と素材名のランダム割り当て、生成時チャージ、staff/wand の基礎ダメージ、識別時のチャージ表示を分離した。

アイテム生成では Rogue 5.4.4 `things[]` の最後の 4% を stick に戻し、未識別名は `copper wand` / `balsa staff` 型、識別済み名は `wand of light [12 charges](copper)` 型に寄せる。Pyxel 版の操作ではメニューの `Zap` から杖を選び、その後に方向を指定する。これは原作の `z` コマンドと同じく方向指定 zap として扱い、チャージが 0 の場合は `nothing happens` でチャージを減らさない。

今回接続した効果は `WS_LIGHT` の部屋照明と識別、チャージ消費、単体モンスター対象系の invisibility / polymorph / teleport away / teleport to / cancellation / haste monster / slow monster までとする。light は暗い部屋なら `ROOM_DARK` を外して視界を更新し、部屋外では `the corridor glows and then fades` とする。単体対象系は `sticks.c:do_zap()` に合わせ、方向先の最初のモンスターへ効果を適用する。invisibility は `ISINVIS` 相当、polymorph は `new_monster(tp, rnd(26)+'A', pos)` 相当、teleport away は `find_floor(NULL, ..., TRUE)` 相当の床へ転移、teleport to はプレイヤー隣接の指定方向へ転移、cancellation は `ISCANC` 相当を立てて invisible / confuse 能力を外す。cancellation 済みモンスターは `fight.c:attack()` と `monsters.c:wake_monster()` の `!ISCANC` 分岐に合わせ、既存の特殊攻撃、Medusa 視線、再生を抑止する。

残りの lightning, fire, cold, magic missile, drain life, nothing は、Rogue 5.4.4 `sticks.c` / `fight.c` / `monsters.c` / `chase.c` / `move.c` の該当処理を確認して、期待値テストを追加してから順に攻略上の効果へ接続する。Xeroc 擬態、treasure room、hallucination、cancellation と Dragon breath などの細部連携は、それぞれの機能実装時に改めて原作関数を確認して詰める。

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

Rogue2.Official の `mesg_E` / `mesg_J` / `COPYING` は `vendor/rogue2_official_messages/` に UTF-8 参照データとして保持する。このデータは文言・用語・メッセージ分離形式の確認専用であり、Pyxel Rogue の実行時には直接読み込まない。取り込み元、commit、ライセンス条件は同ディレクトリの `README.md` と `COPYING` を参照する。

現行実装では `assets/messages/en.json` / `ja.json` / `manifest.json` を実行時メッセージ辞書とし、`TextCatalog` が起動時に一度だけ読み込む。英語カタログは Rogue 5.4.4 C ソースの `msg()` / `addmsg()` 文字列と、Pyxel版固有の UI/ログ文言を持つ。日本語カタログは Rogue2.Official の `mesg_J` に寄せ、対応がない文言は `manual` として補完している。Pyxel Web launcher が JSON 資産を同梱しない場合は、同内容を Python module 化した `rogue_message_catalogs.py` へフォールバックする。欠損キーは日本語から英語へフォールバックし、英語にもない場合は `[missing:key]` を返して stderr に一度だけ警告する。

`PYXEL_ROGUE_LANG=ja pyxel run rogue.py` で日本語表示を選べ、ゲーム中も Select(Back) 補助メニューの Language から日英をトグルできる。言語切り替えはターンを消費せず、過去ログは再翻訳しない。切り替え後の新規ログ、メニュー項目、アイテム名などの表示だけが現在言語に従う。

ゲームログ、補助メニュー、罠名表示は JSON 駆動の `TextCatalog` へ移行した。HUD の一部、Inventory、Help、Death などの固定表示文言は後続タスクで用途別 API に寄せる。

HUD の短縮名は表示制約が強いため、通常のアイテム名とは別に `TextCatalog.hud_item_kind()` を入口にする。実データは段階的に分離するが、呼び出し側は通常名、HUD短縮名、メッセージ、メニュー文言を混ぜず、用途別の catalog API を通す。

メッセージ分離は段階的に進める。Phase 4 以降で追加する新規ログ・UI文言は直書きせず `TextCatalog` 経由にし、既存文言は関連機能を触るタイミングで移行する。新規キーを追加するときは `assets/messages/README.md` の key / placeholder 規約に従い、`manifest.json` の source と `ja_status` から追えるようにする。

翻訳層はゲーム状態を変えない表示レイヤーとして扱う。同じ seed と同じ操作なら、英語 / 日本語の違いでプレイヤー位置、所持品、ターン、HP、モンスター配置などのゲーム状態が変わってはいけない。

## カメラ

現行の `80×22` 地形・移動領域は横幅を常時全表示するため、通常プレイ中の横カメラスクロールは不要になる。カメラ処理は、将来マップサイズや表示タイル数を変更した場合にも破綻しない互換処理として残す。縦方向は Rogue 5.4.4 の `y=1..22` を表示開始 `y=1` で扱い、メッセージ行相当の `y=0` とステータス行相当の `y=23` を地形表示から外す。

## ダンジョン生成

元祖ローグの3×3セクターグリッドアルゴリズムを再現。現行では `rooms.c` と同じ `bsze.x = NUMCOLS / 3`, `bsze.y = NUMLINES / 3` により 80×24 マップを 26×8 セクター基準で扱い、Rogue 5.4.4 と同じ sector index 0..8 の固定順で9個の `Room` を作ったうえで、`rooms.c` 相当の `ISGONE` / 暗い部屋 / `ISMAZE` フラグを割り当てる。通路は全隣接セクターを無条件に接続せず、`passages.c` の `do_passages()` と同様に9部屋を結ぶ spanning tree 8本を作り、追加で `rnd(5)` 回だけ未接続の隣接エッジを掘る。通常部屋、迷路部屋、gone room はこの選ばれた通路グラフ上で接続し、flood fill は互換用の到達保証として残している。

地形・通路・階段・罠・アイテム・モンスター配置は原則 `y=1..22` に収める。Pyxel 側の HUD やログはこの論理座標に含めず、ゲーム状態に影響しない表示レイヤーとして扱う。

通路生成は Rogue 5.4.4 C ソースの `passages.c` を参照し、推測で似せない。特に `do_passages()` が部屋グラフを作り、`conn()` が接続方向に応じて壁上のドア位置を選び、`door()` が部屋の出口を記録し、`putpass()` が通路を掘る責務分担を基準にする。

部屋フラグは Rogue 5.4.4 `rooms.c` の `rnd(4)` 個の `ISGONE`、`rnd(10) < level - 1` による暗い部屋、同分岐内の `rnd(15)==0` による `ISMAZE` を基準にする。暗い部屋と迷路部屋は部屋全体を一括可視化せず、周囲視界のみで探索する。gone room は壁やドアを置かず、通路セルとして接続する。通路の曲がり点はドア直後の壁沿いセルを避け、部屋の水平壁に沿って長い通路が走らないようにする。

暗い部屋の床表示は Rogue 5.4.4 `misc.c:erase_lamp()`, `misc.c:show_floor()`, `rooms.c:leave_room()` の画面上の床消去に合わせる。Pyxel版は探索済みセルを再描画するが、暗い部屋の探索済み床 `.` は現在視界外では表示しない。壁、ドア、床上アイテムの扱いは既存の探索済み表示方針を維持し、床だけをランプ範囲外で消す。

## Phase 4 の完成基準

「Pyxel版をクリアしたら Rogue 5.4.4 をクリアしたと言える」ための短期的な山場は Phase 4 とする。26階で Amulet of Yendor が出現し、Amulet 所持後に階段を上って1階へ帰還し、勝利状態へ到達できることを最小のクリア条件にする。

指輪、杖、罠、隠しドア、隠し通路、scroll of scare monster の床上効果は、単なるアイテム種類追加ではなく Rogue 5.4.4 の攻略判断を成立させる要素として扱う。特に search は、罠・隠しドア・隠し通路を発見するためのゲームロジック上の hook とし、A空押しの正面探索と Select+A / 補助メニュー / `S` の周囲探索を区別する。

Trap Inspect は Rogue 5.4.4 の `^` + 方向に相当するターン非消費コマンドとして扱う。未発見罠は確認対象にせず、search または踏んだ時に露出した `^` だけが種類表示の対象になる。ゲームパッドでは Select+D-pad を高速入力、補助メニューの Trap を発見しやすい入口にする。

罠と隠し要素の発生・発見は Rogue 5.4.4 の `new_level.c`, `passages.c`, `command.c`, `move.c` を基準にする。罠は `rnd(10) < level` の階層ゲートを通ったとき `rnd(level / 4) + 1` 個、最大 `MAXTRAPS` 個を部屋床へ隠して置く。隠し扉は `rnd(10)+1 < level && rnd(5)==0`、隠し通路は `rnd(10)+1 < level && rnd(40)==0` に寄せ、1階では生成されない。search は隠し扉 `rnd(5+probinc)==0`、罠 `rnd(2+probinc)==0`、隠し通路 `rnd(3+probinc)==0` で露出する。Pyxel版では hallucination が未実装のため、その `probinc` だけは状態実装時に追加する。

次の忠実度スプリントでは、杖 bolt 系、Xeroc、passages / monster AI 細部の順で進める。各修正では Rogue 5.4.4 C ソースの関数・定数を先に確認し、必要なら期待値テストを追加してから実装を変える。

run 停止条件は Rogue 5.4.4 の `move.c:do_run()` / `do_move()` と `misc.c:look()` を基準にする。Pyxel 版の dash は `look()` 相当の3x3前方側チェックで床アイテム、近接モンスター、罠、階段、扉、通路分岐を停止対象にし、遠くに見えているだけのモンスターでは停止しない。浅い階の行き止まり通路は、現行方針では `passages.c` の spanning tree と `rnd(5)` 追加接続に寄せており、体感差が出てもまず固定 seed のグラフ監査で原作相当か確認する。

## 死亡画面とスコア

死亡画面はブラウザ・携帯機でのテストプレイを続けやすくする移植UIとして追加する。Depth、Level、Gold、Exp、Turn、死因を表示し、A または Start で新規ゲームへ戻れるようにする。

スコア履歴保存は死亡画面とは分ける。JSONによるハイスコア保存と履歴画面は Phase 7 の仕上げタスクとして扱う。

## Phase 4 残課題：原作との種類数・部屋タイプ差分

現行 Pyxel 版は、Rogue 5.4.4 の以下の主要メカニクスを未実装または別設計のまま残している。いずれも「Pyxel版をクリアしたら Rogue 5.4.4 をクリアしたと言える」状態の成立に必要であり、忠実度修正の対象とする。実装時は各原作関数の期待値テストを先に追加してから接続する。

巻物は `rogue.h:S_CONFUSE..S_PROTECT` / `MAXSCROLLS=18` / `scrolls.c:read_scroll()` / `extern.c:scr_info[]` を基準にする。現行 12 種に対し、原作は 18 種で、特に `identify` が対象別に `S_ID_POTION` / `S_ID_SCROLL` / `S_ID_WEAPON` / `S_ID_ARMOR` / `S_ID_R_OR_S` の 5 種へ分離している点は確率テーブル全体に影響する。Pyxel 版で単一 identify を残す差分を選ぶ場合は、原作との差・理由・影響を本文書へ記録したうえで決定する。`S_CONFUSE` は `fight.c:attack()` の `CANHUH` 付与、`S_FDET` は `scrolls.c:S_FDET` の全食料一時表示、`S_PROTECT` は `scrolls.c:S_PROTECT` の防具呪い・錆び防止として接続する。

ポーションは `rogue.h:P_CONFUSE..P_LEVIT` / `MAXPOTIONS=14` / `potions.c:quaff()` / `extern.c:pot_info[]` を基準にする。現行 12 種に対し、原作は 14 種で、未実装は `P_LSD`（hallucination）と `P_LEVIT`（levitation）。`P_LSD` は視覚混乱に加え `command.c` / `chase.c` の `ISHALU` 表示差し替え、search の `probinc` 増加、invisible monster の誤表示まで接続する。`P_LEVIT` は `ISLEVIT` 相当として罠・階段の発動条件と床上アイテム拾得を抑止し、`daemons.c:land()` 相当で解除する。

treasure room（俗称モンスターハウス）は `new_level.c:138, 180-231` の `treas_room()` を基準にする。`put_things()` で 1/20 の階に発生し、`MINTREAS=2` / `MAXTREAS=10` 個のアイテムを埋めたうえで、次階層相当のモンスターを `ISMEAN` 付きで多数配置する。部屋内モンスターは `give_pack()` で持ち物も持つ。設計書および Pyxel 実装のいずれにも記述がないため、部屋タイプとしての生成、視界公開、AI（全員 `ISMEAN` で起きている扱い）を新規に設計する必要がある。

`give_pack` は Rogue 5.4.4 `monsters.c:give_pack()` と `extern.c:monsters[]` の `m_carry` を基準にする。Pyxel版では `MonsterSpec.carry` に A-Z の値を持たせ、通常モンスター生成時に `level >= max_level && rnd(100) < m_carry` 相当で `make_item()` を `Monster.pack` に保持し、`fight.c:remove_mon(..., TRUE)` 相当として倒した時に床へ落とす。wandering monster は原作 `monsters.c:wanderer()` と同じく `give_pack()` を呼ばない。残事項は `new_level.c:treas_room()` の部屋単位配置で、treasure room 内モンスターへ `give_pack()` を呼ぶ接続は treasure room 実装時に行う。

daemon / fuse 期間管理は `daemon.c`, `daemons.c`, `main.c:fuse()/lengthen()/extinguish()` を基準にする。現行は個別 `int` カウンタで近似しているが、`doctor / stomach / runners / swander / rollwand / sight / unsee / unconfuse / unblind / unhaste / unring / land / nohaste` を統一インフラで扱うことで、`potion of haste self` の重ね掛け、`ring of regeneration` の同時発動、wandering monster の `WANDERTIME=spread(70)` などを Rogue 5.4.4 と同じターン消費で再現できる。

Wizard モード（`wizard.c` / `command.c` の `+` トグル、CTRL-D/A/F/T/E/C/X/~/I 系）とゲーム中セーブ（`save.c:save_game()/restore()`、`command.c` の `S`）は、忠実度監査・長時間プレイの成立に必要な周辺機能として `TODO.md` Phase 7 に記録する。Pyxel Web での永続化方式は実装時に決める。

## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

探索済みだが現在視界外のセルでは、地形と床上アイテムは表示し続け、モンスターは表示しない。これは元祖ローグの「見えた地図上のもの」と「現在見えている動くもの」を分ける表示に寄せるためで、ミニマップや敵一覧のような追加情報UIは使わない。

投擲は Rogue 5.4.4 のゲームロジック準拠を優先し、命中・落下・ターン経過は投げた時点で即確定する。一方で Pyxel Rogue の表示補助として、投げたアイテムが通過セルを数フレーム移動して見える非ブロッキングのアニメーションだけを重ねる。Pyxel Web 互換のため、sleep や待機ループでゲーム更新を止めない。

## ファイル構成

現行実装は `rogue.py` 中心だが、単一ファイルは前提にしない。見通しがよく、Rogue 5.4.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。

分割する場合は、ゲームロジック、データテーブル、入力、描画、設定、保存、通信、プラットフォーム差分の境界を意識する。

現時点では大規模分割よりも、依存方向を整える小さな整理を優先する。`Game` 内にはまだロジック、入力、描画、文言が同居しているため、まず `TextCatalog` とロジックテストで境界を作り、以後の機能追加時に必要な範囲から分離する。

Phase 4 の間は Rogue 5.4.4 忠実度を最優先にし、`core/`, `ui/`, `backend/` のような全面分割は先行しない。新規または修正対象の機能では、ゲーム状態を変える処理を Pyxel 描画・入力・保存/通信から切り離しやすい形に寄せる。設定値は将来の `Settings` 相当へ集約できるよう、言語、自動拾い、パレット、run 表示、レイアウト候補などを散在させない。

保存、オンラインスコアボード、タイトル画面、複数UIレイアウトは、ゲームメカニクスの外側に置く将来レイヤーとして扱う。これらはコア状態の読み書きや表示選択を行ってよいが、Rogue 5.4.4 準拠のターン処理や判定ロジックへ依存を逆流させない。

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
