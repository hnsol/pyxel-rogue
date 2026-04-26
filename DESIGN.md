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

補助参照として `vendor/rogue545p/` に Rogue 5.4.5p のコードを保持する。出典は http://yozvox.web.fc2.com/526F677565.html 。原則の準拠先は引き続き `vendor/rogue544/` だが、Rogue 5.4.4 の identify scroll は `extern.c:scr_info[]` で `identify potion` / `identify scroll` / `identify weapon` / `identify armor` / `identify ring, wand or staff` の5種類に分かれており、プレイ感の劣化として扱う。これを1種類へ戻す場合は、5.4.5p の `options.c:idscrl`、`extern.c:scr_info2[]`、`extern.c:set_scroll_2()` を比較参照し、Rogue 5.4.4 からの意図的差分としてこの文書へ記録してから実装する。

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

テストプレイ中に実行中の改訂を識別しやすくするため、右HUDタイトルは `Rogue V5 YYMMDD_HHMM` 形式の手動更新ビルド表記を含める。体感差の有無に関係なく、コード・テスト・設計文書などを変更した場合は同じ変更で `UI_BUILD` を更新する。これはゲームメカニクスではなく開発・テスト用の表示補助として扱う。

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

キーボードは「Pad style」と「Rogue commands」を分ける。Pad style はゲームパッドの A/B/Start/Select に対応する移植UIで、`Enter` / `Esc` / `Space` / `Tab` / `Shift+方向` を使う。英字キーは Rogue V5 の直打ちコマンドに優先配分するため、旧 A 相当の `z` と旧 B 相当の `c` は Pad style から外す。これにより `z` は zap、`c` は将来の call 用として自然に残せる。

Rogue commands はプレイ中だけ発火し、専用UIや別ロジックは作らず既存のメニュー項目へのショートカットとして扱う。現行では `t` quick throw、`q` quaff、`r` read、`e` eat、`w` wear、`W` wield、`T` take off、`z` zap、`i` inventory、`?` help、`s` 周囲 search、`^` trap inspect を実装する。`^` は Rogue 5.4.4 風に方向待ちへ入り、Select+D-pad / Tab+方向 は携帯機向けの即時 Trap Inspect として同じ確認処理へ接続する。メニュー/アイテム選択/方向指定オーバーレイ中は文字コマンドを発火させない。将来的にアイテム選択中の `a-z` は、表示されている inventory letter の直接選択として別レイヤーで扱う。

A+B は足踏み専用にする。search を兼ねると足踏みが search の上位互換になり、Rogue 5.4.4 の `.` と `s` の意味が薄くなるため、周囲 search は Select+A または補助メニュー/キーボード `S` に分ける。A の空押しは、何もない場所での正面1マス search として扱い、探索の手触りを増やしつつ周囲 search とは区別する。

自動ピックアップは Rogue 5.4.4 の `pickup` オプション相当として扱い、デフォルトONにする。Select(Back) 補助メニューから ON/OFF を切り替え、OFF時は床上アイテムに乗ったことだけを通知し、Aで手動拾得する。拾得処理は手動/自動で共通化し、金は所持金へ直接加算、満杯時は `pack too full`、一度拾った `scroll of scare monster` は再拾得時に灰になる挙動を Rogue 5.4.4 の `pick_up()` に寄せる。

斜め入力は携帯機D-padで横→横+縦の順に入力イベントが分かれやすい。通常移動では単独方向の `btnp` を1フレームだけ保留し、次フレームに直交方向が押されたら斜め1回として確定する。斜め補助モード中は従来通り同時押し斜めだけを受け付け、上下左右単体では移動しない。メニュー系のカーソル操作は `dir_press()` とは別の上下入力として扱い、`diag_assist` と `dir_pending` の影響を受けない。

ダッシュ/走行は Rogue 5.4.4 の `command.c` / `move.c` / `misc.c` を参照し、`do_run()`, `do_move()`, `turn_ok()`, `look()` の挙動へ寄せる。通路のL字角では、前方が壁で左右どちらか一方だけに曲がれる場合、`turn_ok()` 相当の判定で方向転換して走り続ける。部屋内では Rogue 5.4.4 の `door_stop` 相当を常時ONとして扱い、壁沿いに走っているとき前方側の周囲に扉や分岐が見えたら停止する。

斜め移動・斜め近接攻撃・モンスターの斜め接触攻撃は Rogue 5.4.4 の `diag_ok()` 相当で判定する。斜め先そのものに加え、直交する2マスがどちらも通行可能なときだけ成立する。これにより、扉上や壁角から直交片側が壁になっている斜め先へは移動できず、そこにいるモンスターへの近接攻撃も発生しない。モンスター側も同じ制約を受ける。

HP自然回復と空腹は Rogue 5.4.4 の `daemons.c` にある `doctor()` / `stomach()` を基準にする。HPはターン経過で `quiet` が進み、低レベルではゆっくり、高レベルでは速く回復する。空腹は `HUNGERTIME`, `MORETIME`, `STOMACHSIZE`, `STARVETIME` の閾値を使い、食料切れ直後から毎ターンHPを削る挙動にはしない。

## モンスターAI

モンスターAIは Rogue 5.4.4 の `monsters.c`, `chase.c`, `fight.c`, `move.c` を基準にする。単純な「視界内ならマンハッタン距離で近づく」処理は原作と大きく異なり、扉上のプレイヤーへ近づけない、Rattlesnake / Ice monster の特殊攻撃が弱すぎる、非起床モンスターまで常時接近する、といったズレを生むため採用しない。`chase.c:runners()` の `ISHELD` / `ISRUN` ゲートと飛行モンスターの追加移動、`chase.c:move_monst()` の速度ステップ実行、`chase.c:runto()` の追跡開始、`chase.c:diag_ok()` の斜め移動可否、`chase.c:dist()` / `dist_cp()` の二乗距離、`chase.c:roomin()` の部屋矩形判定、`chase.c:see_monst()` / `cansee()` の盲目/不可視、lamp距離、斜め遮蔽、同室照明ゲート、`chase.c:do_chase()` の Dragon flame gate / 最寄り出口 / greedy 目的地補正 / chasee room 選択、`chase.c:chase()` の confused / Phantom / Bat ランダム移動ゲート、混乱解除、候補ゲート、距離/tie選択、戻り値条件は `rogue_chase.py` の小 helper とし、`move.c:rndmove()` の1回だけのランダム移動試行は `rogue_move.py` の小 helper とする。`Game` 側はモンスター1体のターン処理、ヒーロー距離判定、追跡1ステップ処理、地形判定を渡して委譲する。

現行実装では `runto()` 相当で `Monster.running` を立て、running でないモンスターは基本的に移動しない。プレイヤーがモンスターを攻撃した場合や、視界に入った mean monster が `wake_monster()` 相当で起きた場合、`scroll of aggravate monsters` を読んだ場合に追跡を開始する。`chase.c:find_dest()` 相当では、carry 確率を持つモンスターがプレイヤーと別室かつ見えていない場合、同室アイテムを目的地候補にし、`scroll of scare monster` と他モンスターが既に目的地にしているアイテムを除外する。部屋所属は通常表示用の `room_at()` とは別にAI用所属を持ち、部屋床、部屋外周、扉、通路を区別する。扉上の actor は通路側として扱い、扉そのものを部屋出口としても扱えるようにして、扉上のプレイヤーやモンスターが追跡処理から孤立しないようにする。

追跡は `chase()` 相当として、周囲8マスから `diag_ok()`、通行可、他モンスター占有、床上 `scroll of scare monster` を避ける条件を満たす候補を選び、Rogue 5.4.4 の `dist()` と同じ二乗距離で目的地に近づく。別部屋にいる場合は、まず所属部屋の出口へ向かう。現時点では通路番号は完全再現せず、通路は単一の corridor 所属として扱う。Bat、Phantom、confused monster は原作同様にランダム移動を混ぜ、flying monster は距離がある場合に追加移動する。

特殊攻撃は `fight.c` の命中後分岐へ寄せる。Ice monster は命中時に `no_command += rnd(2)+2` 相当でプレイヤーを凍結させ、Rattlesnake は `save(VS_POISON)` 失敗時に Strength を下げる。Aquator、Leprechaun、Nymph、Medusa、Troll、Vampire、Wraith、Venus Flytrap も、既存の簡略フラグを維持しつつ原作の発動タイミングへ寄せる。`fight.c:swing()` の d20 命中判定、`fight.c:roll_em()` の weapon/hurl profile、ダメージ式ロール、部位ごとの命中/ダメージ加算、defender `!ISRUN` 命中補正、`str_plus[]` / `add_dam[]` の Strength 補正、Ice monster の freeze 加算、Rattlesnake poison の Strength 低下判定、Wraith/Vampire drain 発動率、Wraith level drain、Vampire max HP drain、Venus Flytrap の `vf_hit` 加算・miss 時ダメージ・hold 解除、Nymph の `rnd(++nobj)==0` 盗み対象選択、Leprechaun の金額減算回数、`rogue.h:GOLDCALC` の金額ロールは `rogue_fight.py` の小 helper とし、`ISCANC` 相当の `cancel` は命中後特殊攻撃、Medusa の `wake_monster()` 視線、再生、Dragon breath などの特殊能力入口で必ず確認する。プレイヤーの行動不能は、sleep/freeze/faint 系の `no_command`、bear trap の `no_move`、Venus Flytrap の `held_by` に分ける。

モンスター状態フラグは `rogue_monsters.py` を Pyxel 非依存の対応表・小 helper とし、Rogue 5.4.4 `rogue.h` の `ISHASTE` / `ISSLOW` / `ISCANC` / `ISINVIS` / `CANHUH` に対応する既存フラグ文字列を集中させる。`chase.c:move_monst()` に合わせ、`ISSLOW` は `t_turn` が真の手だけ通常追跡し、`ISHASTE` は追加追跡を行い、処理後に `t_turn` を反転する。`sticks.c:do_zap()` の `WS_HASTE_M` / `WS_SLOW_M` はこの helper 経由で、遅い相手を速めると `ISSLOW` 解除、速い相手を遅くすると `ISHASTE` 解除、そうでなければ該当フラグ付与とし、slow monster は `t_turn = TRUE` に戻す。

モンスターの戦闘値は Rogue 5.4.4 `extern.c:monsters[]` の `s_lvl`, `s_arm`, `s_dmg`, `s_exp` を名前付き `MonsterSpec` として持つ。tuple の位置引数で `level` と `armor` を取り違えると、プレイヤー命中率や plate mail の防御力が大きく壊れるため、代表モンスターと `fight.c:swing` の境界値をテストで固定する。Hobgoblin は `level=1`, `armor=5`, `damage="1x8"`, `exp=3`、Ice monster は `level=1`, `armor=9`, `damage="0x0"`, `exp=5` を監査対象にする。

残差分として、通路番号付き passages、Dragon breath、指輪・杖・cancellation とAIの完全連携は未完了。Dragon breath の最小接続は Rogue 5.4.4 `chase.c:do_chase()` の `DRAGONSHOT` 分岐と `sticks.c:fire_bolt()` に合わせ、同じ部屋内で直線・射程内・非 `ISCANC` なら `rnd(5)==0` で Dragon の位置から flame bolt を撃つ。wandering monster は Rogue 5.4.4 の `main.c:fuse(swander, 0, WANDERTIME, AFTER)`, `daemons.c:swander()` / `rollwand()`, `monsters.c:wanderer()` を基準にし、初回 `swander` は AFTER fuse、以後の `rollwand` daemon と再予約 `swander` は BEFORE として扱う。`WANDERTIME` は `rogue.h` の `spread(70)` とする。暗い部屋、迷路部屋、gone room は生成と視界への接続を先行実装済みで、今後も原作関数を確認しながらアイテム・モンスター配置やAI所属を詰める。

## 武器メカニクス

武器は Rogue 5.4.4 の `weapons.c:init_dam`, `fight.c:roll_em`, `things.c:inv_name/new_thing`, `scrolls.c:S_ENCH` を基準にする。武器は命中補正 `hit_plus` とダメージ補正 `dam_plus` を別々に持ち、表示も `+1,+1 mace (weapon in hand)` のように2値で出す。近接・投擲とも Strength の命中/ダメージ補正を通し、arrow + bow のような launcher 補正も原作に合わせて合算する。`weapons.c:fall()` / `fallpos()` / `init_weapon()` の投擲落下候補、`rnd(++cnt)==0` 選択、落下失敗時分岐、初期個数は `rogue_weapons.py` の小 helper とする。

防具は当面既存の `ench` 表現を維持する。ring of dexterity / increase damage は `fight.c:roll_em` 相当に合わせ、装備中武器での近接攻撃に限って加算する。

装備変更は Rogue 5.4.4 の `armor.c:wear()` と `weapons.c:wield()` を分けて扱う。armor は `cur_armor != NULL` の場合に wear を拒否し、先に take off する必要がある。weapon は `weapons.c:wield()` が `dropcheck(cur_weapon)` を通るため、現在武器が cursed でなければ持ち替え可能であり、Pyxel 版でも自動置換自体は差分として扱わない。

呪い生成確率は `things.c:new_thing()` を基準にする。weapon は `rnd(100) < 10` で cursed、armor は `rnd(100) < 20` で cursed、一部 ring は `rnd(3)==0` で `o_arm=-1` かつ cursed、ring of aggravate monster と ring of teleportation は常時 cursed とする。food は ration/slime-mold を `rnd(10)!=0` の90/10にし、カテゴリ重みは `extern.c:things[]` の 26/36/16/7/7/4/4 を基準にする。`things.c:pick_one()` 相当の減算式重み選択は `rogue_things.py` に分離し、カテゴリ、potion、scroll、weapon、armor、ring、stick の種類選択は `rnd(100)` 経由で行う。`new_level.c:new_level()` の `no_food++` と `things.c:new_thing()` の food 生成時 `no_food=0` も `rogue_things.py` で扱い、4階層超で food を強制する。生成時の weapon / armor の curse / enchant は原則未鑑定情報であり、Pyxel 版では `Item.known` を Rogue 5.4.4 の `ISKNOW` 相当として扱う。armor は `armor.c:wear()` に合わせ、装備した時点で `known=True` にして enchant / protection を表示する。ring の `ring_num()` と stick の `charge_str()` は種類識別後に表示する。

拾得処理は Rogue 5.4.4 の `pack.c:add_pack()` / `pack_room()` を基準にする。scare monster scroll は未発見なら `ISFOUND` 相当を立て、発見済みを拾うと dust で消滅する。床からの拾得では同種スタック可能な food / missile でも `pack_room()` 相当の上限確認を先に通し、満杯ならスタックせず床に残す。

## 指輪メカニクス

指輪は Rogue 5.4.4 の `rogue.h:R_*`, `extern.c:ring_info[]`, `init.c:stones[]/init_stones()`, `things.c:new_thing()/inv_name()/dropcheck()`, `rings.c:ring_on()/ring_off()/ring_eat()/ring_num()`, `fight.c:roll_em()`, `daemons.c:doctor()/stomach()`, `scrolls.c:S_REMOVE` を基準にする。`rogue_rings.py` を Pyxel 非依存の最初の指輪ロジック境界とし、14種テーブル、ランダム石名、補正付き指輪生成、左右スロット、装備/解除、呪い、食料消費をここへ寄せる。

初回実装では、ゲーム状態に直結する protection / add strength / dexterity / increase damage / slow digestion / regeneration を接続した。protection はプレイヤーAC、防具と同じ低いほど強い値へ反映し、dexterity / increase damage は装備中武器での近接攻撃にだけ加算する。slow digestion と searching などの確率型食料消費は `rings.c:ring_eat()` の負値テーブルに合わせ、slow digestion は消費を減らす。regeneration は `daemons.c:doctor()` と同じく自然回復判定後に追加回復し、回復した場合は quiet をリセットする。

残りの指輪効果は、Rogue 5.4.4 の `command.c`, `rings.c`, `monsters.c`, `move.c`, `fight.c`, `potions.c` を確認して接続した。searching はターン後処理で手ごとに `search()` 相当を呼び、ターンを追加消費せず失敗時メッセージも出さない。teleportation は同じターン後処理で手ごとに `rnd(50)==0` のときテレポートする。see invisible は invisible monster の表示条件へ反映し、aggravate monster は装備時と装備中の monster creation で追跡を開始させる。stealth は `wake_monster()` 相当の mean monster 起床判定を抑制する。sustain strength は Rattlesnake / dart trap / potion of poison の Strength 低下を防ぎ、maintain armor は Aquator / rust trap などの `rust_armor()` 相当で錆びを防ぐ。adornment は装備時効果を持たず、装備しただけでは識別済みにしない。

UI差分として、原作の `gethand()` による左右手プロンプトは、携帯機向けメニュー操作では最初の空きスロットへ装備し、解除時は装備中アイテムを選ぶ方式にしている。左右どちらに装備されているかはインベントリ表示の `(on left hand)` / `(on right hand)` で確認できる。今後、左右指定が攻略上必要になる場面が出た場合は、ゲーム状態の差分を出さずに方向入力で手を選ぶUIへ拡張する。

see invisible potion は Rogue 5.4.4 `potions.c:P_SEEINVIS` / `do_pot()`, `misc.c:spread()`, `rogue.h:CANSEE/SEEDURATION`, `daemons.c:unsee()` に合わせ、`spread(SEEDURATION)` の間だけ invisible monster の表示条件へ反映する。`P_SEEINVIS` 末尾の `sight()` 相当により blind も解除する。hallucination 中の invisible monster は `misc.c:look()` 相当により正体ではなくランダムな A-Z として表示する。monster detection potion は `potions.c:P_MFIND` の `SEEMONST` / `turn_see()` 相当として、現在フロアのモンスターを一時表示し、`HUHDURATION` 後の `turn_see(TRUE)` fuse で解除する。

Xeroc は Rogue 5.4.4 `monsters.c:new_monster()` の `t_disguise = rnd_thing()`、`misc.c:look()` の `t_disguise` 表示、`fight.c:attack()` の近接正体露出、`sticks.c:do_zap()` の `WS_CANCEL` による `t_disguise = t_type` を基準にする。Pyxel 版では `Monster.disguise` を `t_disguise` 相当として持ち、通常表示では擬態文字を描き、hallucination 中は既存 `rnd(26)+'A'` 表示を優先する。近接攻撃で未露出の Xeroc に触れた場合は正体を表示して攻撃をそこで止める。投擲時は正体露出後に攻撃判定を続ける。

## 杖メカニクス

杖は Rogue 5.4.4 の `rogue.h:WS_*`, `extern.c:ws_info[]`, `init.c:metal[]/wood[]/init_materials()`, `things.c:new_thing()/inv_name()/pick_one()`, `sticks.c:fix_stick()/do_zap()/charge_str()` を基準にする。初回実装では `rogue_sticks.py` を Pyxel 非依存の杖ロジック境界として追加し、14種テーブル、wand/staff と素材名のランダム割り当て、生成時チャージ、staff/wand の基礎ダメージ、識別時のチャージ表示を分離した。

アイテム生成では Rogue 5.4.4 `things[]` の最後の 4% を stick に戻し、未識別名は `copper wand` / `balsa staff` 型、識別済み名は `wand of light [12 charges](copper)` 型に寄せる。Pyxel 版の操作ではメニューの `Zap` から杖を選び、その後に方向を指定する。これは原作の `z` コマンドと同じく方向指定 zap として扱い、チャージが 0 の場合は `nothing happens` でチャージを減らさない。

今回接続した効果は `WS_LIGHT` の部屋照明と識別、チャージ消費、単体モンスター対象系の invisibility / polymorph / teleport away / teleport to / cancellation / haste monster / slow monster までとする。light は暗い部屋なら `ROOM_DARK` を外して視界を更新し、部屋外では `the corridor glows and then fades` とする。単体対象系は `sticks.c:do_zap()` に合わせ、方向先の最初のモンスターへ効果を適用する。invisibility は `ISINVIS` 相当、polymorph は `new_monster(tp, rnd(26)+'A', pos)` 相当、teleport away は `find_floor(NULL, ..., TRUE)` 相当の床へ転移、teleport to はプレイヤー隣接の指定方向へ転移、cancellation は `ISCANC` 相当を立てて invisible / confuse 能力を外す。cancellation 済みモンスターは `fight.c:attack()` と `monsters.c:wake_monster()` の `!ISCANC` 分岐に合わせ、既存の特殊攻撃、Medusa 視線、再生を抑止する。

lightning, fire, cold は Rogue 5.4.4 `sticks.c:do_zap()` / `fire_bolt()` に合わせ、`WS_ELECT` は bolt、`WS_FIRE` は flame、`WS_COLD` は ice として識別し、`BOLT_LENGTH=6`、壁・扉反射、`6x6` ダメージ、モンスター/プレイヤーの `VS_MAGIC` セーブ、Dragon に対する flame bounce を接続する。treasure room、cancellation と Dragon breath などの細部連携は、それぞれの機能実装時に改めて原作関数を確認して詰める。

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

罠と隠し要素の発生・発見は Rogue 5.4.4 の `new_level.c`, `passages.c`, `command.c`, `move.c` を基準にする。罠は `rnd(10) < level` の階層ゲートを通ったとき `rnd(level / 4) + 1` 個、最大 `MAXTRAPS` 個を部屋床へ隠して置き、種類は `rnd(NTRAPS)` とする。隠し扉は `rnd(10)+1 < level && rnd(5)==0`、隠し通路は `rnd(10)+1 < level && rnd(40)==0` に寄せ、1階では生成されない。search は隠し扉 `rnd(5+probinc)==0`、罠 `rnd(2+probinc)==0`、隠し通路 `rnd(3+probinc)==0` で露出する。`probinc` は `command.c:search()` と同じく hallucination で +3、blind で +2 とする。`new_level.c` / `passages.c` / `command.c:search()` の確率ゲートは `rogue_search.py` / `rogue_dungeon.py` の小 helper として追えるようにする。`move.c:be_trapped()` の bear trap は `no_move += BEARTIME`、sleeping gas は `no_command += SLEEPTIME`、dart trap poison は `save(VS_POISON)` 後に sustain strength と Strength floor を確認して処理する。`move.c:rust_armor()` の錆び合法判定・保護分岐と、`T_MYST` の11択メッセージ表は `rogue_move.py` の小 helper とする。

次の忠実度スプリントでは、passages / monster AI 細部、daemon / fuse、鑑定・命名・発見リストの順で進める。各修正では Rogue 5.4.4 C ソースの関数・定数を先に確認し、必要なら期待値テストを追加してから実装を変える。

run 停止条件は Rogue 5.4.4 の `move.c:do_run()` / `do_move()` と `misc.c:look()` を基準にする。Pyxel 版の dash は `look()` 相当の3x3前方側チェックで床アイテム、近接モンスター、罠、階段、扉、通路分岐を停止対象にし、遠くに見えているだけのモンスターでは停止しない。浅い階の行き止まり通路は、現行方針では `passages.c` の spanning tree と `rnd(5)` 追加接続に寄せており、体感差が出てもまず固定 seed のグラフ監査で原作相当か確認する。

## 死亡画面とスコア

死亡画面はブラウザ・携帯機でのテストプレイを続けやすくする移植UIとして追加する。Depth、Level、Gold、Exp、Turn、死因を表示し、A または Start で新規ゲームへ戻れるようにする。

スコア保存はゲームメカニクスの外側に置く。`vendor/rogue544/rip.c:score()` と `main.c:quit()` を基準に、順位は Gold のみ、死亡は 90%、quit と勝利は 100% を採用する。v1 は同一端末内保存の JSON / localStorage とし、死亡 / 勝利 / quit の結果画面から Top 10 を見られる状態を最小要件にする。全履歴画面は別タスクとして分ける。

## Phase 4 残課題：原作との種類数・部屋タイプ差分

現行 Pyxel 版は、Rogue 5.4.4 の以下の主要メカニクスを未実装または別設計のまま残している。いずれも「Pyxel版をクリアしたら Rogue 5.4.4 をクリアしたと言える」状態の成立に必要であり、忠実度修正の対象とする。実装時は各原作関数の期待値テストを先に追加してから接続する。

巻物は `rogue.h:S_CONFUSE..S_PROTECT` / `MAXSCROLLS=18` / `scrolls.c:read_scroll()` / `extern.c:scr_info[]` を基準にする。Pyxel 版の `SCROLLS` は原作 18 種の順序と確率へ更新し、identify は Rogue 5.4.4 では `S_ID_POTION` / `S_ID_SCROLL` / `S_ID_WEAPON` / `S_ID_ARMOR` / `S_ID_R_OR_S` の 5 種へ分離されている。今後はこの5種類仕様を劣化差分として扱い、5.4.5p の `idscrl` 実装をリファレンスに1種類化する方針を検討する。`S_ID_*` は `scrolls.c:read_scroll()` の `id_type[]` と `wizard.c:set_know()` 相当に合わせ、対象カテゴリだけを正式鑑定する。現時点では携帯機UI向けの暫定として該当カテゴリの未鑑定品から自動選択するため、原作 `whatis(TRUE, type)` の対象選択プロンプトは後続の「鑑定・命名・発見リスト忠実度」で実装する。`S_CONFUSE` は `fight.c:attack()` の `CANHUH` 付与、`S_FDET` は `scrolls.c:S_FDET` の全食料一時表示、`S_PROTECT` は `scrolls.c:S_PROTECT` の防具呪い・錆び防止として接続する。

ポーションは `rogue.h:P_CONFUSE..P_LEVIT` / `MAXPOTIONS=14` / `potions.c:quaff()` / `extern.c:pot_info[]` を基準にする。現行 Pyxel 版は原作 14 種を実装済み。`P_LSD` は `ISHALU` 相当として `potions.c:do_pot()` / `daemons.c:come_down()` に合わせ、`misc.c:rnd_thing()` / `misc.c:look()` 相当の視覚混乱、`command.c:search()` の `probinc` 増加、invisible monster のランダム表示へ接続する。`P_LEVIT` は `ISLEVIT` 相当として罠・階段の発動条件と床上アイテム拾得を抑止し、`daemons.c:land()` 相当で解除する。

treasure room（俗称モンスターハウス）は `new_level.c:138, 180-231` の `treas_room()` を基準にする。`put_things()` で 1/20 の階に発生し、通常物資は `MAXOBJ=9` 回の `rnd(100)<36` 試行で配置し、Amulet 所持後に上階へ戻る場合は `level < max_level` で新規物資を置かない。通常部屋の gold とモンスターは `rooms.c:do_rooms()` を基準にし、gold は各部屋 `rnd(2)==0` かつ Amulet 上昇中ではない場合に `GOLDCALC` で配置し、部屋モンスターは gold あり80%、なし25%で発生する。gone room は `rnd(4)` 回の重複あり選択、dark/maze は `rnd(10)<level-1` と `rnd(15)==0` を `rogue_rooms.py` へ分離する。treasure room は `MINTREAS=2` / `MAXTREAS=10` 個のアイテムを埋めたうえで、次階層相当のモンスターを `ISMEAN` 付きで多数配置する。部屋内モンスターは `give_pack()` で持ち物も持つ。Pyxel 版では `rogue_dungeon.py` に treasure room の発生ゲート、`MINTREAS` / `MAXTREAS` / `MAXTRIES`、通常物資試行、Amulet 上昇中ゲート、個数計算を分離し、`Game` 側は配置と既存 `make_item()` / `Monster` 生成の接続だけを担当する。

`give_pack` は Rogue 5.4.4 `monsters.c:give_pack()` と `extern.c:monsters[]` の `m_carry` を基準にする。Pyxel版では `MonsterSpec.carry` に A-Z の値を持たせ、通常モンスター生成時に `level >= max_level && rnd(100) < m_carry` 相当を `rogue_monsters.should_give_pack()` へ小分割し、`make_item()` を `Monster.pack` に保持し、`fight.c:remove_mon(..., TRUE)` 相当として倒した時に床へ落とす。Leprechaun は `fight.c:killed()` に合わせ、`level >= max_level` で死亡時に `GOLDCALC` gold を pack へ追加し、`save(VS_MAGIC)` 成功時はさらに4回分を足してから床へ落とす。wandering monster は原作 `monsters.c:wanderer()` と同じく `give_pack()` を呼ばない。treasure room 内モンスターは `treas_room()` の一時的な `level++` 相当により、次階層 depth で `give_pack()` を呼ぶ。

daemon / fuse 期間管理は `daemon.c`, `daemons.c`, `main.c:fuse()/lengthen()/extinguish()` を基準にする。現行は個別 `int` カウンタで近似しているが、`doctor / stomach / runners / swander / rollwand / sight / unsee / unconfuse / unblind / unhaste / unring / land / nohaste` を統一インフラで扱うことで、`potion of haste self` の重ね掛け、`ring of regeneration` の同時発動、wandering monster の `WANDERTIME=spread(70)` などを Rogue 5.4.4 と同じターン消費で再現できる。`doctor()` と `stomach()` の純ロジックは `rogue_daemons.py` の `doctor_tick()` / `stomach_tick()` に小分割し、`Player` はリング食料消費や再生回数など周辺値を渡して委譲する。`doctor()` は HP が最大でも `quiet++` を先に行い、レベル8以上の回復量は `rnd(level-7)+1`、回復判定後に `max_hp` へ丸め、HPが変わった場合は `quiet=0` に戻す。`stomach()` は `food_left -= ring_eat(LEFT) + ring_eat(RIGHT) + 1 - amulet` とし、`food_left <= 0` で既に `no_command` 中なら新たな faint 期間を加えず、faint 期間は `rnd(8)+4` とする。`command.c:command()` に合わせ、BEFORE daemon/fuse は `no_command` 減算より前に実行し、`no_command` が減算で0になった時は `you can move again` を出す。

初期移行として `rogue_daemons.py` に `DelayedActionTable` / `FuseList` / `DaemonList` を追加し、`daemon.c:fuse()`, `lengthen()`, `extinguish()`, `do_fuses(AFTER)`, `start_daemon()`, `kill_daemon()`, `do_daemons()` と比較できる境界を作る。daemon と fuse は原作同様に共通の `MAXDAEMONS=20` スロットを使い、同名の重複登録を許し、`kill_daemon()` / `extinguish()` は先頭1件だけ消す。まず `potions.c:P_HASTE` / `misc.c:add_haste(TRUE)` / `daemons.c:nohaste()` を接続し、haste 中は `command.c:command()` の `ntimes++` 相当として、2回のプレイヤー行動につき1回だけ AFTER fuse、空腹、モンスター行動を進める。haste self の二重使用は `rnd(8)` の `no_command` を加え、`nohaste` fuse を消して失神メッセージを出す。`potions.c:P_CONFUSE`, `P_SEEINVIS`, `P_LSD`, `P_BLIND`, `P_LEVIT`, `P_MFIND` は `do_pot()` / `turn_see()` 相当として未発動時に `fuse()`、発動中の再使用で `lengthen()` する。`swander` / `rollwand` は `rogue_daemons.py` の `swander()` / `rollwand()` へ小分割し、`main.c` の初回 `fuse(AFTER)` と `daemons.c` の `start_daemon(BEFORE)` / 再予約 `fuse(BEFORE)` に合わせる。doctor、stomach、runners など daemon 系は、後続タスクで同じ delayed action 境界へ段階移行する。

`daemons.c:sight()` は blind を解除するときに `extinguish(sight)` も行う。Pyxel 版でも `potions.c:P_HEALING`, `P_XHEAL`, `P_SEEINVIS` から `sight()` を通し、blind 解除後に古い `sight` fuse が残らないようにする。

Wizard モード（`wizard.c` / `command.c` の `+` トグル、CTRL-D/A/F/T/E/C/X/~/I 系）とゲーム中セーブ（`save.c:save_game()/restore()`、`command.c` の `S`）は、忠実度監査・長時間プレイの成立に必要な周辺機能として `TODO.md` Phase 7 に記録する。Pyxel Web での永続化方式は実装時に決める。

## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

探索済みだが現在視界外のセルでは、地形と床上アイテムは表示し続け、モンスターは表示しない。これは元祖ローグの「見えた地図上のもの」と「現在見えている動くもの」を分ける表示に寄せるためで、ミニマップや敵一覧のような追加情報UIは使わない。

投擲は Rogue 5.4.4 のゲームロジック準拠を優先し、命中・落下・ターン経過は投げた時点で即確定する。一方で Pyxel Rogue の表示補助として、投げたアイテムが通過セルを数フレーム移動して見える非ブロッキングのアニメーションだけを重ねる。Pyxel Web 互換のため、sleep や待機ループでゲーム更新を止めない。

## ファイル構成

現行実装は `rogue.py` 中心だが、単一ファイルは前提にしない。見通しがよく、Rogue 5.4.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。

分割する場合は、ゲームロジック、データテーブル、入力、描画、設定、保存、通信、プラットフォーム差分の境界を意識する。

現時点では大規模分割よりも、依存方向を整える小さな整理を優先する。分割の目的は、このプロジェクトとしてのコードの見通し・テストしやすさを上げることと、Rogue 5.4.4 C ソースとの比較を効果的にすることに置く。`Game` 内にはまだロジック、入力、描画、文言が同居しているため、まず `TextCatalog` とロジックテストで境界を作り、以後の機能追加時に必要な範囲から分離する。今後も Phase 4 タスクを進めるたびに、原作関数・定数・テーブルに対応するまとまりを見つけたら、小さな `rogue_*.py` helper へ切り出す機会を必ず確認する。

Phase 4 の間は Rogue 5.4.4 忠実度を最優先にし、`core/`, `ui/`, `backend/` のような全面分割は先行しない。新規または修正対象の機能では、ゲーム状態を変える処理を Pyxel 描画・入力・保存/通信から切り離しやすい形に寄せる。設定値は将来の `Settings` 相当へ集約できるよう、言語、自動拾い、パレット、run 表示、レイアウト候補などを散在させない。

`rogue.py` の大きめ分割は、daemon/fuse、monster AI、戦闘計算など Phase 4 の主要忠実度テストがもう一段固定され、対象関数の期待値が十分に赤緑で守られた後に行う。現時点で適した分割は、今回の `rogue_daemons.py` のように原作ファイルや関数群に対応する小さな helper 抽出までとする。全面分割へ進む目安は、Phase 4 の未完了リストが戦闘計算の精密化と照合用テスト拡充中心になり、`Game` から副作用なしに呼べる純ロジック境界が複数揃った時点とする。

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

## 鑑定・命名・発見リスト

Rogue 5.4.4 の鑑定状態は、種類単位の `obj_info.oi_know`、種類単位の仮名 `obj_info.oi_guess`、個体単位の `ISKNOW`、武器/防具の個体ラベル `o_label` を分ける。参照元は `rogue.h:obj_info/ISKNOW`、`things.c:inv_name()/nameit()/print_disc()`、`wizard.c:whatis()/set_know()`、`command.c:call()`、`misc.c:call_it()`。

現行 Pyxel 版は `IdentTable.pk/sk/rk/wk` と `Item.known` に加え、`oi_guess` 相当の `pg/sg/rg/wg`、`misc.c:call_it()` 相当の `c` call、`things.c:print_disc()` 相当の `D` discovered list、`command.c:call()` 相当の weapon / armor 個体ラベル `o_label` まで実装済み。`use_pot()` / `use_scr()` の正式鑑定タイミングも `potions.c:quaff()/do_pot()` と `scrolls.c:read_scroll()` に合わせて監査済み。ring / stick は Rogue 5.4.4 `things.c:nameit()`、`rings.c:ring_num()`、`sticks.c:charge_str()` に合わせ、種類判明後も個体 `ISKNOW` 相当の `Item.known` が立つまで補正値・チャージを隠す。

修正は `TODO.md` の「鑑定・命名・発見リスト忠実度」を優先順に進める。実装時は `potions.c:quaff()/do_pot()`、`scrolls.c:read_scroll()` の各分岐で「判明する/しない」を期待値テスト化してから直す。Pyxel 都合で文字入力を簡略化しても、正式鑑定と仮名は別状態として保存する。

Potion の正式鑑定は Rogue 5.4.4 `potions.c:quaff()` の分岐ごとに扱う。`do_pot()` は `oi_know` が未設定のときだけ `knowit` を反映し、既に知っている種類を未鑑定へ戻さない。`P_SEEINVIS` は `do_pot(P_SEEINVIS, FALSE)` のため飲んでも `oi_know` を立てない。`P_MFIND` は `SEEMONST` / `turn_see()` を開始するが `pot_info[P_MFIND].oi_know` を直接立てない。`P_TFIND` は `potions.c:is_magic()` 相当で床上アイテムとモンスター所持品 `t_pack` を調べ、魔法アイテムを実際に検出した場合だけ `pot_info[P_TFIND].oi_know` を立てる。一方で healing / poison / gain strength / haste self / levitation など、原作で明示的に `oi_know` を立てるものは使用時に正式鑑定する。Strength 変化、healing / extra healing の HP 上限処理は `rogue_potions.py` に分離し、`P_HEALING` は `roll(level, 4)`、`P_XHEAL` は `roll(level, 8)` を使う。raise level は `potions.c:raise_level()` と `misc.c:check_level()` に合わせ、`e_levels[level-1]+1` 相当の経験値へ進め、上がったレベル数ぶん `roll(delta, 10)` で HP / max HP を増やし、`welcome to level %d` を出す。

命名機能と思い出し機能は、potion / scroll / ring / stick の `oi_guess`、weapon / armor 個体単位 `o_label`、discovered list まで実装済み。`things.c:print_disc()` は `oi_know` または `oi_guess` がある potion / scroll / ring / stick を一覧化する。

Scroll の正式鑑定も Rogue 5.4.4 `scrolls.c:read_scroll()` の各分岐に合わせる。`S_CONFUSE` / `S_SCARE` / `S_REMOVE` / `S_AGGR` は効果を出すが `scr_info[] .oi_know` を直接立てない。`S_MAP` は `scr_info[S_MAP].oi_know` を立て、隠しドア / 通路 / 罠を実地形として表示対象に戻す。`S_SLEEP` は `no_command` を設定し、`player.t_flags &= ~ISRUN` 相当として Pyxel 側の dash を止める。`S_HOLD` は周囲2マス以内の running monster を実際に `ISHELD` 相当へしたときだけ `scr_info[S_HOLD].oi_know` を立て、対象がいない場合は strange sense of loss で未鑑定のままにする。`S_TELEP` は `teleport()` 後に `cur_room != proom` になった場合だけ識別する。`S_CREATE` は周囲8マスの `step_ok()` 候補から生成し、正式識別は立てない。`S_ARMOR` / `S_ENCH` / `S_PROTECT` は装備中の防具 / 武器へ効果が出ても `scr_info[] .oi_know` を直接立てず、対象装備がない場合は strange sense of loss にする。

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
          'KEY_Q','KEY_W','KEY_E','KEY_T',
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
