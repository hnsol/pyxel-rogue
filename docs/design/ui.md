# UI Design

表示、入力、パレット、フォント、言語、移植UIの詳細仕様。ゲーム状態を変えない表示補助の判断を置く。

## 架空レトロコンソールとパレット方針

`Rogue V5 on Pyxel` は、1989年頃に NEC ホームエレクトロニクスが PC Engine と PC-98 の間を埋める大人向け文字表示ゲーム機として作った、架空の `PC-Engine Hi-Resolution` へ移植された Rogue というIF設定を採る。解像度は 512×320、ASCII 6×12px / CJK 10×12px / 行高12px の文字表示を重視し、内部マスターパレットは512色または4096色、同時表示は16色とする。

この16色制約は、Pyxelらしさと架空ハードのVRAM/帯域/コスト感を両立させるための作品上の制約である。Pyxel実装上は拡張色を使えるが、通常プレイ画面のテーマは16色CLUTとして扱う。タイトル背景など画像アセット専用パレットは、画像インデックス維持のため例外的に追加色を持ってよい。

Flexoki は公式の思想と配色名を参照するが、色表を丸ごと転載せず、Rogue V5 の可読性に合わせた16色移植パレットとして再構成する。参照元は https://stephango.com/flexoki とし、`Flexoki Dark` / `Flexoki Light` / `Flexoki Syntax Dark` / `Flexoki Syntax Light` を内蔵テーマとして持つ。

パレット定義は単なる色配列ではなく、地形、記憶地形、UI本文、補助情報、強調、金、罠などの意味役割を持つ。モンスター分類はゲーム側で定義し、パレット側は `beast` / `undead` / `magic` / `thief` / `deadly` / `mimic` などの分類色を提供する。個別に読みにくい敵だけ、テーマ側の上書きを許す。

`Flexoki Dark` は低彩度で暗い探索画面を基準にする。記憶地形は `base-850` とし、見えている壁・通路・床との差を残す。`I` ice monster は低層で頻出し、名前どおり氷の敵として読めることを優先して青系のままにする。一方で `P` phantom、`U` black unicorn、`X` xeroc は特殊・不可思議・擬態の敵として、情報表示や potion と同じ青系から分離する。Dark は空きスロットが1つだけなので、`purple-700` を追加し、`P/U/X` を同じ特殊敵色へまとめる。

`Flexoki Syntax Dark` は `Flexoki Dark` の探索画面の骨格を保ちながら、公式Syntax Highlight向けの400系アクセントを使う派生テーマとする。地形、記憶地形、本文、UI枠はDarkに近い階層を維持し、アイテム、危険、強調、特殊敵など意味のある記号をsyntax色へ寄せる。`I` は青系を維持し、`P/U` は `purple-700`、`X` は擬態・違和感を強めるため `magenta-400` に分ける。Darkでは特殊敵を1色に圧縮し、Syntax Darkでは追加スロットを使ってmimicだけ分離する。通常HUDの難度名、`Hp`、`Str`、`Arm`、`Exp`、`D:`、`G:`、装備ラベルと装備補正値は補助情報であり、本文より暗い `base-600` 相当のサブテキスト色を使う。

テーマ調整では、色だけを変えるつもりで表示仕様を変えてはならない。メッセージtoastの寿命、フェード段階数、各age範囲、表示行数、HUDの情報階層、記憶地形と現在視界の意味差は、テーマ共通の表示契約として扱う。テーマごとの分岐は、同じ契約を別の色で表現するためのものに限定する。たとえばtoastは `age 0` / `age 1` / `age 2-3` / `age 4-5` / 消滅という構造を維持し、Lightテーマで黒方向へ沈む逆転を避ける場合も、段階数や寿命を減らさず各段階の色だけを置き換える。

パレット作業では、変更前に「今回変えるもの」と「変えない表示契約」を明文化してから実装する。見た目の問題を直す場合でも、既存の時間変化、入力、ゲーム状態、ログ履歴、表示密度を勝手に単純化しない。テストはこの契約破壊を検知する補助であり、主対策は契約を設計文書上の制約として扱うことである。
## 対象環境

当面の主対象は PC / SteamDeck とし、Python/Pyxel 本体に加えて Pyxel Web でも遊べることを前提にする。中華ゲーム機、スマートフォン、タブレットなどの狭い画面向け最適化は将来候補へ下げる。

Pyxel Web Launcher で GitHub branch を指定して起動確認する場合、branch 名には `/` を使わない。Launcher の `run=owner/repo/branch/path` 形式では、`codex/foo` のような slash 付き branch 名が path と誤解されることがあるため、Webで確認する開発branchは最初から slash なしで作る。

Rogue 5.4.4 準拠のため、内部ダンジョン座標は `rogue.h` の `NUMCOLS=80`, `NUMLINES=24`, `STATLINE=NUMLINES-1` を基準にする。`move.c:do_move()` の境界条件と同じく、地形・通路・部屋・プレイヤー移動の主領域は `x=0..79`, `y=1..22` とし、`y=0` はメッセージ行相当、`y=23` はステータス行相当としてゲーム地形を置かない。

表示は Pyxel 向け UI として分離する。現在は 80桁の Rogue 5.4.4 ダンジョン領域を優先し、512×320 の架空レトロコンソール風画面で `80×22` のプレイ領域、四隅HUD、toast型メッセージを表示する。ゲームメカニクスは変更せず、表示レイヤーだけで状態確認を補助する。移植性のため、レイアウト定数は将来的に画面サイズから再計算できるようにする。


目標レイアウトは、Rogue 5.4.4 と同じ `80×24` 論理座標のうち、地形・移動領域である `80×22` をメインASCIIダンジョン表示として扱う。現在はセル 6×12px で描画領域 480×264px とし、512×320 画面の `x=16`, `y=24` へ収める。左右余白は16px、上は2行、下は約2.6行をHUD用に使い、サイドHUDと下部固定ログは置かない。

通常画面のHUDは、左上に現在難度 `Easy` / `Normal` / `Classic` / `Strict` を選択画面と同じ英字表記で表示し、右上に `D:26 G:1240`、左下にHPバーと `W +1,+1 mace A +2 plate`、右下に `Str 16(16) Arm 3 Exp 7/120` を置く。空腹・状態異常は該当時だけ右下2行目へ `Hungry Weak Faint Blind Confuse` のように表示する。装備名は通常画面では短縮名だけを表示し、正式名と詳細は Inventory 側で確認する。

四隅HUDの文字色は「ラベルを沈め、値を読ませる」方針にする。`D:` / `G:` / `Hp` / `W` / `A` / `Str` / `Arm` / `Exp` は暗めの補助色、値は通常文字色、Gold値だけはgold強調色にする。HPバーは文字ではなくバーだけを目立たせ、枠は暗めの白系、通常バーは階段と同系の金色、被ダメージ残像は明るい赤橙、危険時は赤にする。これは「架空レトロ機の上で動くモダンゲームUI」として、6×12フォント制約の中で情報階層を作るためのルールとする。

低HP時のHPバー枠は、赤や黄色の警告点滅ではなく、黒〜灰色だけでゆっくり脈打つ不気味な明滅にする。明滅は `dim -> shadow -> mid -> glow -> glow -> mid -> shadow -> dim` の役割列を5フレーム刻みで循環させ、各テーマはその役割を既存16色の中から選ぶ。枠は一瞬見えにくくなってよいが、特殊敵、アイテム、本文の目立つ色を直接使わない。HPバー本体の赤とは役割を分け、死亡後の墓画面で残って見えても「生命維持ランプがまだ脈打っている」ような余韻として許容する。

UIの構造検討は疑似Markdownで行い、実装時も同じ語彙へ寄せる。`[frame:panel]` は枠付きオーバーレイの `-- Title --`、`[frame:screen]` は結果・名前入力・スコアなど全画面級の `=== Title ===`、`[frame:prompt]` は方向入力などの小プロンプト、`[frame:inline-section]` はHUD内の `-- Equip --` / `-- Cond --` のような枠なし小見出しを表す。`[role:section]` は見出し構造色、`[role:text]` は通常本文、`[role:hilite]` は選択中・重要・特殊状態、`[role:restore]` は前回選択復元、`[role:subtext]` は操作ヒントに使う。新しいUI要素を追加するときはこの frame / role に分類し、合わない場合は先にこの体系を更新する。

UI変更では、機能が動くことだけでなく、画面がプレイヤーへ約束する概念が一貫しているかを確認する。表示名は難易度なら `DifficultyProfile.label`、識別状態なら `IdentTable` のように単一ソースから出し、HUDや日本語表示だけ別の固定文言へ逃がさない。テストは正しい表示だけでなく、`通常` 固定や未発見アイテム掲載のような「出てはいけない表示」も検査する。

名前入力は `## === Name Entry === [frame:screen]` として扱い、入力欄のラベルは `[role:section]`、文字カーソルと `END` は `[role:hilite]`、操作説明は `[role:subtext]` に置く。オンライン同期中の一時表示はスコア画面内の `### -- Sync -- [frame:panel]` として扱い、通信中メッセージは重要な進行状態として `[role:hilite]` にする。

### UI疑似Markdown一覧

この一覧は実装同期対象とする。UIを追加・変更したら、この一覧と実装のどちらが正かを確認し、ズレたままにしない。

```md
# Play [frame:screen]
## Rogue V5 YYMMDD_HHMM [role:section]
## Food Normal [role:text]
## Ctl 8w Auto [role:text]
## -- Equip -- [frame:inline-section] [role:section]
- +1,+1 mace [role:text]
- +2 plate [role:text]
## -- Cond -- [frame:inline-section] [role:section]
- Blind [role:hilite]

## -- Action -- [frame:panel]
- **z)** Zap [role:restore?]
- **t)** Throw [role:restore?]
- **P)** Put on [role:text]
- **r)** Read [role:restore?]
- **e)** Eat [role:restore?]
- **q)** Quaff [role:restore?]
- **w)** Wield [role:text]
- **W)** Wear [role:text]
- **T)** Take off [role:text]
- **R)** Remove ring [role:text]
- **c)** Call [role:text]
- **D)** Discoveries [role:text]
- **d)** Drop [role:text]

## Which Direction? [frame:prompt]
- 8方向入力 [role:hilite]
- 操作ヒント [role:subtext]

## === Language / 言語 === [frame:screen]
- Choose display language. / 表示言語を選んでください。 [role:text]
> English [role:hilite]
- 日本語 [role:text]
- 操作ガイド [role:subtext]

## -- Choose Your Rogue -- / -- 難易度を選ぶ -- [frame:panel]
> Normal [role:hilite]
- Easy [role:text]
- Classic [role:text|restore]
- selected description [role:subtext]
- 操作ガイド [role:subtext]

## -- Item Action -- [frame:panel]
> **a)** selected item [role:hilite|restore]
- **b)** item [role:text]

## === Info === / === 情報 === [frame:screen]
### -- Inventory | Log | Settings | Help -- / -- 持ちもの | ログ | 設定 | ヘルプ -- [frame:panel]
> Inventory [role:hilite]
- Log [role:text]
- Settings [role:text]
- Help [role:text]
- guide: Left/Right tabs, Select/B close [role:subtext]

## -- Save game -- / -- ゲームを保存 -- [frame:panel]
- Save this game and quit? / この冒険を保存して終了しますか？ [role:text]
- A/Enter: Save / B/Esc: Cancel [role:subtext]

## === Scoreboard === / === スコアボード === [frame:screen]
### -- Local | Weekly | Season -- / -- ローカル | 週間 | シーズン -- [frame:panel]
### Weekly Rivals 2026-W18 / シーズンレジェンド 2026-Spring [role:section + subtext]
- 1  1234 player: result [role:text|hilite]
- period / sync / guide [role:subtext]
#### -- Sync -- [frame:panel]
- Syncing scores... [role:hilite]

## === Online Sync === / === オンライン同期 === [frame:screen]
- prompt [role:text]
- name cursor / END [role:hilite]
- 操作ガイド [role:subtext]
- Select/L Change Language（言語切替） [role:hilite]

## === Name Entry === [frame:screen]
### Name [role:section]
> cursor / END [role:hilite]
- 操作ヒント [role:subtext]

## === R.I.P. === [frame:screen]
## === Victory === [frame:screen]
## -- Quit -- [frame:panel]
## === Top 10 === [frame:screen]
```

四隅HUDは、基礎ステータスと攻略判断に必要な装備補正だけを出す。通常の食料状態は表示せず、Rogue準拠で `Hungry` / `Weak` / `Faint` になった時だけ状態異常ラインへ出す。斜め補助や自動拾いなどの入力モードは、HPバー上の短い状態チップで常時表示する。

ミニマップと全体マップUIは廃止する。元祖ローグでは、見えているASCIIダンジョン表示そのものが地図であり、別レイヤーの地図UIを足すと探索体験が現代ローグライク寄りになりすぎるため。探索情報はメインASCII表示に集約する。

現代的UIは探索情報を増やすためではなく、状態確認を読みやすくするために使う。四隅HUDには HP、Str、Arm、Exp、Depth、Gold、武器/防具補正、状態異常をまとめる。常時インベントリ全表示、敵一覧、周辺警告レーダーのような便利すぎる情報は通常画面には置かない。詳細な履歴表示はメッセージ履歴画面で扱う。これは攻略情報を新しく増やすUIではなく、流れたログを読み返すための可読性補助とする。

Info画面は `## === Info === [frame:screen]` / `## === 情報 === [frame:screen]` の下に `### -- Inventory | Log | Settings | Help -- [frame:panel]` / `### -- 持ちもの | ログ | 設定 | ヘルプ -- [frame:panel]` 相当のタブ行を置く2段階見出しにする。Select または Tab で Inventory タブを開き、左右で Log / Settings / Help へ切り替える。Info中の Select/Tab は Info を閉じる。`?` はどのInfoタブからでも Help へ移る。Log は直近100件を上下スクロールで確認でき、開いた直後は最新メッセージ側を表示する。A/B/Esc/i でプレイへ戻る。ターンは消費しない。フィルタ、検索、敵一覧、危険警告などは持たせず、近接メッセージログと操作参照を補完する小さな保険に留める。

テストプレイ中に実行中の改訂を識別しやすくするため、コード・テスト・設計文書などを変更した場合は同じ変更で `UI_BUILD` を更新する。通常画面左上はタイトルではなく現在難度を表示するため、ビルド表記は通常プレイHUDへ常時表示しない。これはゲームメカニクスではなく開発・テスト用の表示補助として扱う。

HPバーの被ダメージ色はフレーム数ではなく、HP低下を検出したターン中だけ残す。次のターンへ進んだら通常表示に戻すことで、Pyxel の描画フレームレートや環境差で消える速さが変わりすぎないようにする。

Full Map / 拡大全体マップは現方針では復活させない。Rogue 5.4.4 の地形・移動領域をメインASCII表示へ集約することで、地図確認の役割は本体表示へ統合済みとみなす。将来マップ寸法や画面サイズを調整する場合も、まずメインASCII表示の可読性と探索済みセルの扱いを調整し、別レイヤーのマップUIを安易に追加しない。

### SteamDeck向けUI再設計候補

SteamDeck の Chrome / Pyxel Web で遊ぶことを主戦場にする場合、1280×800 の全域を使えるとは限らない。ブラウザ上部のタブやアドレスバー、Pyxel Web 側の表示余白を考慮し、画面サイズは整数倍の綺麗さだけで決めない。優先順位は、`80×22` ダンジョンを横欠けなく、老眼でも読みやすい大きさで表示することを最上位に置く。HUD とログの余裕より、メインASCIIの可読性を優先する。

通常プレイ画面は、`80×22` ダンジョンを512×320内の中央領域へ置き、Hades風に生命線を左下、身体・成長情報を右下、階層・Goldを右上へ分散する。下固定ログは置かず、メッセージは近接toastで扱う。

メッセージは下ログではなく、`message toast` としてダンジョン上に最大7行だけ一時表示する。表示はフレーム数ではなくターン数基準にし、0ターンを明色、1〜2ターンをやや暗く、3〜4ターンをさらに暗く、5ターンを最暗、6ターン目で非表示にする。ラッチ高さを持ち、行追加では高さを広げるが、古い行が age-out しても表示行を上へ詰めない。全行が消えたときだけラッチ高さと位置をリセットする。

toast の位置は `80×22` ダンジョンを3×3ブロックに分割して選ぶ。プレイヤー `@` のいるブロックは避ける。進行方向は直近4歩の有効移動ベクトル累計で決め、足踏み、戦闘、メニュー操作、無効移動は含めない。左右移動では前方隣接ブロック、下、上の順で選び、上下移動では前方隣接ブロック、左、右の順で選ぶ。前方隣接ブロックが画面外なら側方候補へ落とす。後方ブロックは原則使わない。進行方向がない場合は下、上、左、右の順で選ぶ。新着メッセージ発生時、またはプレイヤーがtoastブロック外側2マスの余白へ入ったときだけ位置を再評価する。戦闘や足踏みなど移動しないターンでは、基本的に位置を変えない。

toast は枠と半透明フィルを持たず、テキストと1px shadowだけで描く。幅は23 ASCII文字相当を基準にし、英語は単語途中で切らないようスペース直前で折り返す。CJKを含む文はスペースではなく pixel幅で折り返し、行頭 `、。！？` を避ける。メッセージ本文はログ保存時に正規化し、英語の文頭 `You` は `you` へ寄せ、日本語文末の `。` と英語文末の単独ピリオドは省く。意味を持つ `！` / `？` / `...` は残す。toast とメッセージ履歴は同じ正規化済み本文を表示する。新しいメッセージは下へ追加し、古いメッセージが上、新しいメッセージが下に来る時間順ログとして読む。0ターンの各メッセージ先頭には `>` を置き、wrap継続行にはマーカーを付けない。ack必須メッセージは未承認中だけ先頭行の `!` をブリンクさせ、wrap継続行も含めて本文色を強調色にする。承認後は通常の `>` 表示へ戻す。流れたログはメッセージ履歴画面で確認できるようにし、toast 自体に検索やフィルタは持たせない。

toast の age-out は、ゲーム状態を変えない「気持ちいい消え方」の追究として扱う。1メッセージが複数行に折り返された場合や1ターンで複数行出た場合でも、期限切れ行を同時に消さず、上の行から20フレームごとに1行ずつ退場させる。これによりログが一気に欠ける印象を避ける。ただし、退場アニメーション中にさらにターンが進んだ場合はテンポを優先し、残り行を待たずに即消す。ログ履歴 `msgs` 自体は削らず、toast 表示だけの演出差分に留める。

方向指定、アイテム選択、確認は toast ではなく `command window` として扱う。これらは結果ログではなく入力中の状態なので、入力完了またはキャンセルまで消えない。Inventory、Help、Score、Discoveries、Log history などは full screen UI とし、ダンジョン表示を一時的に消してよい。

UI見出しの装飾は画面階層を表す。`=== Title ===` は画面全体を占有する full screen UI、`-- Title --` は一時的な command window / panel、`--- Title ---` は Help や一覧本文内の section heading として使う。見出し色は構造ラベル用の `UI_SECTION_COL` に統一する。選択中のタブ、メニュー項目、カーソル、重要な実行対象は `UI_SELECTED_COL` / `UI_HILITE_COL`、本文は `UI_TEXT_COL`、操作ガイドや補助情報は `UI_SUBTEXT_COL` を使う。タイトル画面の専用パレットでも同じ意味づけを保ち、専用色番号は「選択中」「通常」「枠」の役割として扱う。

色指定は直接の Pyxel 色番号ではなく、意味を持つ color role を第一入口にする。画面側は「赤が欲しい」ではなく「危険」「警告」「補助設定ON」「補助設定OFF」「精神系状態」「有利状態」などの意味を要求し、`rogue_palettes.py` の `PaletteTheme.roles` が現在パレットでの色番号へ解決する。既存の地形・モンスター・HP低下フレーム role と同じ契約をHUDやInfoにも広げる。新しいUI色を追加するときは、まず role 名、用途、ON/OFFや危険度の意味を定義し、全パレットに割り当てる。表示コードに新しい固定色番号を増やさない。

HUDのHPバー上には、常時確認したい小さい状態チップ列を置く。`PICK ON/OFF` は自動拾い、`DIAG ON/OFF` はStart/Space押下中だけ有効な斜め補助を表す。ON は `flag_on`、OFF は `flag_off` role を使う。状態異常も同じ列に載せるが、全部を危険色にしない。空腹は `status_warn`、盲目・混乱・幻覚は `status_mind`、加速・浮遊・探知など有利/特殊状態は `status_buff`、HP低下や致命的な悪状態だけ `status_bad` を使う。これによりパレットごとに色味を変えても、意味の優先順位は保てる。

Info 画面は `Inventory / Log / Settings / Help` のタブ構成にする。Settings は上下で項目を選び、項目選択中の左右は他タブと同じくタブ切替に使う。A/Enterで値選択へ入り、値選択中だけ左右で値を変え、A/Enterで項目選択へ戻る。対象は `Auto pickup`, `Language`, `Palette`, `Save and quit` とし、現在値を常に文字で表示する。値の表示位置は固定列に置き、言語切替でラベル幅が変わっても `ON/OFF` やパレット名の開始位置は動かさない。`Save and quit` は `## -- Save game -- [frame:panel]` の確認を経て中断セーブを行う。確認系UIの操作ヒントはゲームパッド/キーボードを併記し、決定は `A/Enter`、キャンセルは `B/Esc` とする。`Auto pickup` は Rogue2.Official には直接対応語がない移植UIなので、日本語は操作文脈で「自動拾い」とする。足元を拾う即時コマンドは現時点では追加しない。`Language` / `Palette` は表示設定、`Auto pickup` は入力補助設定として扱い、ゲームメカニクスの確率やターン処理は変えない。設定変更は画面内の現在値で確認できるため、ゲームログには流さない。

セーブは Rogue 5.4.4 `save.c:save_game()`, `save_file()`, `restore()`, `encwrite()`, `encread()` と `state.c:rs_save_file()`, `rs_restore_file()` の意味論に寄せる。Pyxel版では原作バイナリ互換ではなく JSON を XOR 難読化して保存するが、保存対象は再開に必要なゲーム状態一式とし、設定、オンラインプロフィール、スコアキャッシュ、将来の統計/QRエクスポートは混ぜない。スロットは1つだけで、保存は中断として扱う。タイトル画面は保存済みのときだけ `CONTINUE` / `つづきから` を出し、ロード成功後は原作同様にセーブを消費する。破損などでロードに失敗した場合はセーブを消さない。

ゲームパッドとキーボードで別UIを作らない。`t` と `Select+A` は同じ quick throw インタフェースに入り、入口だけが異なる。方向待ち、アイテム選択、キャンセル、ログ、ターン消費は共通処理にする。他の Rogue command キーも、可能な限りゲームパッド向け command window と同じ状態へ接続する。

Item picker と Inventory は同じ pack grid 表示に寄せる。pack は現行通り `p.inv` の順番を pack letter `a-z` とし、Rogue 5.4.4 `pack.c:add_pack()` に近いカテゴリ寄せ挿入を保つ。表示だけを2〜3列グリッドに折り返し、カテゴリ選択の2段階UIは作らない。Inventory は操作ガイド領域を予約し、19件前後で2列化する。キーボードでは `a-z` の直選択を維持し、ゲームパッドでは上下左右で移動できるようにする。

Item picker の初期カーソルはコマンドごとに前回使用した `Item` object identity を記憶する。前回 object がまだ pack 内にあれば、その現在位置へカーソルを置く。消費や drop で object が pack から消えていれば `a` に戻す。letter や表示名では判定しない。鑑定や命名で表示名が変わっても同じ object なら継続し、別アイテムへ勝手に近寄せないことで誤爆を避ける。

Action menu は `Read` / `Eat` / `Quaff` を同じ行に並べ、ゲームパッドで左右移動したときの消耗品コマンドのまとまりを優先する。補助メニューは廃止し、ターンやコマンド実行に近い `Search`、`Trap`、`Quit` は Action menu へ移す。繰り返しやすく誤爆リスクが低い `Quaff` / `Read` / `Eat` / `Zap` / `Throw` だけ前回Actionを復元する。復元カーソルはシアン系の `UI_RESTORED_CURSOR_COL` で表示し、ユーザーが上下左右へ動かした時点で通常の選択色へ戻す。装備変更、drop、call、discoveries、search、trap、quit などは初期選択 `Eat` に戻す。
## オプション方針

オプションは表示、入力補助、保存先、通信、テスト用挙動に限定する。確率、ターン消費、モンスターAI、アイテム効果、罠、スコアなど、Rogue 5.4.4 の攻略判断に影響するゲームメカニクスはオプションで変えない。

`Settings` は言語、自動ピックアップ、パレット名、run 中間表示フラグなどを保持する。標準パレットは `flexoki_dark` とし、Palette 切替はゲーム状態に影響しない表示設定として扱う。
## 操作体系

現方針では A/B/Start/Select + D-pad を基本操作にする。詳細なキー割当と入力注意は `../../AGENTS.md` と `../TODO.md` を優先して読む。

```
D-pad                 通常は8方向移動。斜め狙いの2軸入力が遅れて1軸だけ確定した場合は、その軸を離すまで後追いの追加軸を次の斜め移動として扱わない
Start押下中           斜め補助モード
A                     決定 / 拾う / 階段。空押し時は search せず、足元に何もないことだけを伝える
B短押し               キャンセル / メニュー
B長押し + D-pad       ダッシュ
Select(Back)          Info（持ちもの / Log / Settings / Help）。Info中にもう一度押すと閉じる
Select+A              quick throw（方向を選んでからアイテム選択）
Select+B              周囲8マス search
Select+D-pad          発見済み罠の種類確認（^ + 方向相当）
A+B                   足踏み
,                     Rogue 5.4.4 command.c:',' 準拠の拾得
```

Rogue commands はプレイ中だけ発火し、既存メニュー項目へのショートカットとして扱う。アイテム選択中の `a-z` は `pack.c:get_item()` の letter 選択相当であり、プレイ中コマンドとは別レイヤーにする。
## フォント

Pyxel 標準フォント 4×6px は小さく、ASCII ローグの可読性に不安があった。`pyxel.Font(path)` で BDF 読込可能と判明し、現行では Pyxel 同梱の `umplus_j10r.bdf` を標準にしている。ASCII 6px / CJK 10px / 7187文字で日本語にも対応する。

```python
import os
font = pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__),
                                "examples", "assets", "umplus_j10r.bdf"))
```

フォント選択機構は持たず、当面は `umplus_j10r.bdf` に固定する。
## 日本語 / 英語切替

ゲーム挙動は Rogue 5.4.4 準拠、日本語表現は Rogue2.Official 準拠として扱う。Rogue2.Official は日本語メッセージ、アイテム名、モンスター名、ヘルプ文言などの表現ソースであり、ゲームロジックや確率・ターン処理の正解としては使わない。

参照元:

- https://github.com/suzukiiichiro/Rogue2.Official
- `mesg_J`: 日本語メッセージ・用語
- `mesg_E`: 英語メッセージとの対応確認

Rogue2.Official の `mesg_E` / `mesg_J` / `COPYING` はローカルの `vendor/rogue2_official_messages/` に UTF-8 参照データとして置く。このデータは文言・用語・メッセージ分離形式の確認専用であり、Pyxel Rogue の実行時には直接読み込まない。取り込み元、commit、ライセンス条件は取得元リポジトリで確認する。

現行実装では `assets/messages/en.json` / `ja.json` / `manifest.json` を実行時メッセージ辞書とし、`TextCatalog` が起動時に一度だけ読み込む。英語カタログは Rogue 5.4.4 C ソースの `msg()` / `addmsg()` 文字列と、Pyxel版固有の UI/ログ文言を持つ。日本語カタログは Rogue2.Official の `mesg_J` に寄せ、対応がない文言は `manual` として補完している。アイテム名、モンスター名、水薬色、HUD短縮名は `assets/terms/en.json` / `ja.json` に分離し、同じ nested key を持つことをテストで保証する。Pyxel Web launcher が JSON 資産を同梱しない場合は、同内容を Python module 化した `rogue_message_catalogs.py` / `rogue_terms.py` へフォールバックする。欠損キーは日本語から英語へフォールバックし、英語にもない場合は `[missing:key]` または元キーを返すが、通常開発では日本語 terms 欠損をテスト失敗として扱う。

`PYXEL_ROGUE_LANG=ja pyxel run rogue.py` で日本語表示を選べ、ゲーム中も Info の Settings タブにある Language から日英をトグルできる。初回オンライン同期導線では操作ヒント行の下に `Select/L Change Language（言語切替）` を表示し、ゲームパッドSelectまたはキーボードLで日英を切り替えられる。言語切り替えはターンを消費せず、過去ログは再翻訳しない。切り替え後の新規ログ、メニュー項目、アイテム名、オンラインスコアボード表示などが現在言語に従う。

ゲームログ、Settings、罠名表示、主要 terms、Info / Inventory タブ見出しとガイド文、Inventory の装備注記と防具 protection 表記は JSON 駆動の `TextCatalog` へ移行した。HUD の一部、Help、Death などの固定表示文言は後続タスクで用途別 API に寄せる。

HUD の短縮名は表示制約が強いため、通常のアイテム名とは別に `TextCatalog.hud_item_kind()` を入口にする。実データは `assets/terms` の `hud` namespace に置き、呼び出し側は通常名、HUD短縮名、メッセージ、メニュー文言を混ぜず、用途別の catalog API を通す。

日本語の指輪・杖名は Rogue2.Official の `mesg_J` を基準にする。英語では Rogue 5.4.4 と同じく `wand` / `staff` を区別するが、日本語表示ではどちらも `杖` に丸める。未鑑定品は材質名から `めのうの指輪` / `銅の杖` のように組み立て、鑑定済み品は種類名から `強さが増す指輪` / `魔法のミサイルの杖` のように組み立てる。

メッセージ分離は段階的に進める。Phase 4 以降で追加する新規ログ・UI文言は直書きせず `TextCatalog` 経由にし、既存文言は関連機能を触るタイミングで移行する。新規キーを追加するときは `assets/messages/README.md` の key / placeholder 規約に従い、`manifest.json` の source と `ja_status` から追えるようにする。

翻訳層はゲーム状態を変えない表示レイヤーとして扱う。同じ seed と同じ操作なら、英語 / 日本語の違いでプレイヤー位置、所持品、ターン、HP、モンスター配置などのゲーム状態が変わってはいけない。
## カメラ

現行の `80×22` 地形・移動領域は横幅を常時全表示するため、通常プレイ中の横カメラスクロールは不要になる。カメラ処理は、将来マップサイズや表示タイル数を変更した場合にも破綻しない互換処理として残す。縦方向は Rogue 5.4.4 の `y=1..22` を表示開始 `y=1` で扱い、メッセージ行相当の `y=0` とステータス行相当の `y=23` を地形表示から外す。
