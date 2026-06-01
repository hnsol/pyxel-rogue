# Online And Score Design

死亡・勝利・スコア・オンライン同期・名前入力に関する詳細仕様。

## 死亡画面とスコア

死亡画面はブラウザ・携帯機でのテストプレイを続けやすくする移植UIとして追加する。`## === R.I.P. === [frame:screen]` として扱い、墓石本文と Depth / Level / Exp / Turn は `[role:text]`、Gold と次画面へ進む操作は `[role:hilite]` にする。A または Start でスコア画面へ進める。Result 系の Victory / Top 10 は `[frame:screen]`、Quit は小さめの結果確認なので `[frame:panel]` とする。画面タイトルは日英ローカライズ、本文は `[role:text]`、勝利文・Gold・次画面へ進む操作だけ `[role:hilite]`、Top 10 の表本体は scoreboard の `[role:text]` に揃える。

スコア保存はゲームメカニクスの外側に置く。`vendor/rogue544/rip.c:score()`、`rip.c:death()`、`rip.c:killname()`、`rip.c:total_winner()`、`main.c:quit()` を基準に、死亡は Gold の 90% を墓石表示とスコアに使い、starvation / hypothermia / arrow / dart / bolt の死因名と冠詞も `killname()` に合わせる。quit は Gold 100%、勝利は Gold に所持品売却額を加えた値を採用する。ローカル保存は JSON / localStorage とし、旧スコア形式は開発中リセットとして v2 storage へ切り替える。スコアボードは `## === Scoreboard === [frame:screen]` / `## === スコアボード === [frame:screen]` の下に、通常Rogueでは `### -- Easy | Normal | Classic | Strict -- [frame:panel]` の難易度タブ、続けて `### -- Local | Weekly | Season -- [frame:panel]` / `### -- ローカル | 週間 | シーズン -- [frame:panel]` の期間タブを置く。その次の行に My Rogue Chronicle / Weekly Rivals / Seasonal Legends、期間ラベル、表示難度を並べる。スコアボードの表示難度はプレイ設定の難易度とは別に持ち、タイトルから開いた場合は上下で切り替えられる。ゲーム終了後に開く場合は、その冒険の難易度を初期表示にする。下部の期間終了、同期状態、操作ガイドは暗色の `[role:subtext]` とし、ランキング10行と重ならないように領域を予約する。My Rogue Chronicle はローカル履歴を即表示する。Daily は廃止し、Weekly / Season は同一期間・同一 player_name の最高点だけを表示する。Season は Spring 3-5月、Summer 6-8月、Fall 9-11月、Winter 12-2月の固定季節制とする。

オンラインスコア送信は移植UIの外側にある任意機能として扱う。公開repoには実デプロイ先URLや運用詳細を置かず、通信先は `PYXEL_ROGUE_SCORE_URL` で実行環境から渡す。実装雛形は公開してよいが、シークレット、実URL、実運用メモは公開文書へ書かない。ゲーム終了時はローカル保存を優先し、通信失敗時もゲーム進行を止めない。

Nyandor 5F Playable Beta は期間限定URLとして扱うが、将来ゲームモード化する可能性を残す。オンラインスコアボードのダミースコアは、実スコアのRogue 5.4.4準拠処理とは分離した表示補助とする。Nyandorから取得するWeekly / Seasonでは `variant=nyandor` を渡し、サーバ側の実スコアとダミーを専用シートで分ける。Nyandorは `Normal` 固定なので難易度タブを出さず、ダミーも地下1-5階・低めの点数に圧縮する。本編Rogueのダミーは従来通り深層を含む。

初回起動と未登録状態は Guest mode とし、名前は `guest` 固定にする。設定ファイル / localStorage がまだない初回だけ、タイトル前に `=== Language / 言語 ===` の言語選択を表示し、説明文も `Choose display language. / 表示言語を選んでください。` と日英併記にして保存する。Guest のローカルスコアは保存し、Weekly / Season はオンラインスコアボードから取得するが、ローカルスコアは送信しない。Guest の Weekly / Season 表示ではオンラインTop10へローカルスコアを合成せず、Top10の下に1行空けてローカルguest最高スコアだけを強調表示する。Guest の同期操作回数は `guest_metrics` に `timestamp` / `event` だけを記録し、失敗しても表示を止めない。タイトルは Guest 時に `ENTER DUNGEON / SCOREBOARD / ONLINE MODE`、登録済み Online 時に `ENTER DUNGEON / SCOREBOARD / GUEST MODE` を出し、日本語モードでは `運命の洞窟に入る / スコアボード / オンラインモード` または `ゲストモード` にする。状態行は暗色ではなく強調色で、`MODE: GUEST` または `MODE: ONLINE` と `USER: <id>` を表示する。Online ID は空欄名から開始し、`guest` は予約名として登録不可にする。Online 登録画面では、ローカルスコア履歴から `guest` と予約名を除いた直近3件を `Previous Names` / `以前の名前` として縦に出し、D-pad/矢印で `END` の先へ移動して候補を選べる。Select/L の言語切替は維持する。Online 登録後は登録ID固定で、登録後にそのIDで記録されたスコアだけを同期対象にする。Guest / Online の2モードに整理し、未認証を示す `*` 表記は使わない。

Death Review Stats は、死亡 / 勝利 / quit 後に次回の判断を改善するための攻略支援として扱う。プレイ中に情報を増やすものではなく、終了後に LLM へ貼れる Markdown 風プレーンテキストを表示またはコピーできるようにする。目的は「答えを見る」ことではなく、Rogue の失敗を自分で振り返るための材料を整えること。

Stats には内部真相を出さず、その時点でプレイヤーが知っていた情報だけを出す。死亡時 pack は画面上で見えていた名前で列挙し、鑑定済みアイテムは種類名を出す。未鑑定アイテムは `unknown potion x3` / `unknown scroll x2` のようにカテゴリと数だけを出し、正体は明かさない。面倒な集計、たとえば消耗品使用数、食料残数、最終装備、直近ログ、depth / turn / HP / Str / AC、難易度、seed、build はコンピュータがまとめる。

タイトル導線は移植UIとして `Logo -> Online registration prompt -> Title -> Play` にする。起動ロゴは Rogue 5.4.4 の著作権表示と Pyxel 版の HSL Laboratory 表記を表示し、任意キーでスキップできる。Title の Start は即 New Game に進み、Name 欄選択時はオンライン名の登録/切替導線に入る。ゲーム開始ログは `Hello <NAME>, welcome to the Dungeons of Doom!` / `やあ <NAME>、運命の洞窟へようこそ。` とし、local-onlyの場合は `<NAME>` に `*` 印を付ける。開始直後からマップ/HUD/ログを描画する。
