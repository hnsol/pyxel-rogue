# AGENTS.md — Pyxel Rogue

「過剰にオーバースペックな Pyxel 版・元祖ローグ」。ASCII ベースで Rogue 5.4.4 を検証可能な底本として扱う。Pyxel 版をクリアしたら、それは Rogue V5 をクリアしたと言える状態を最終目標にする。

- フレームワーク: Pyxel 2.9.0 / Python 3.10+
- 実行対象: Python/Pyxel 本体に加えて Pyxel Web も視野に入れる
- 想定環境: ブラウザ、デスクトップ、SteamDeck、中華ゲーム機など
- 現行本体: `rogue.py`
- タスク一覧は `docs/TODO.md`、設計判断の入口は `docs/DESIGN.md`、詳細仕様は `docs/design/*.md`、品質方針は `docs/dev/QUALITY_POLICY.md` を参照

## 品質方針

- Rogue 5.4.4 は挙動の底本であり、コード構造の模範ではない
- 実装・構造・検証・文書は、現代的な Python プロジェクトとして美しく保つ
- 目的は行数削減ではなく、40年後にも仕様・設計判断・検証方法を追えるリポジトリにすること
- 分割は責務境界を明確にするために行う。小さすぎる抽出や wrapper 比較テストの増殖は避ける
- 変更前に、目的が「美しい repo」にどう効くかを短く確認する
- 詳細は `docs/dev/QUALITY_POLICY.md` に従う

## 設計文書の読み分け

- UI、入力、表示名、パレット、フォント、言語: `docs/design/ui.md`
- Rogue 5.4.4 忠実度、ゲームメカニクス、生成、AI、アイテム、原作参照: `docs/design/rogue544.md`
- プロジェクト説明、Rogue表記、README運用: `docs/design/project.md`
- 難易度、将来バリアント、バージョン選択方針: `docs/design/variants.md`
- BGM/音まわり: `docs/design/bgm.md`
- スコア、死亡・勝利画面、オンライン同期、名前入力: `docs/design/online.md`
- ファイル分割、テスト、repo整理、mock、コミット運用: `docs/design/architecture.md`

## 最優先の原作参照ルール

- ゲーム状態に影響するバグは、まず Rogue 5.4.4 との忠実度差分が露出した可能性として扱い、原作確認前に症状回避の補修を足さない
- Rogue 5.4.4 の挙動確認は、必ず最初にローカルの `vendor/rogue544/` を読む
- 忠実度修正では、Web検索や記憶より先に `vendor/rogue544/` の該当 C ソースを `rg` / `sed` で確認する
- 参照した原作ファイル名・関数名・定数名は、テスト名、コメント、または `docs/design/rogue544.md` から追えるようにする
- `vendor/rogue544/` が見つからない場合だけ、`docs/design/rogue544.md` の「元祖ローグのソース参照先」に従って取得方法を確認する

## セットアップ

```bash
pip install pyxel
pyxel run rogue.py
```

## テスト

```bash
python3 -c "import ast; ast.parse(open('rogue.py').read()); print('OK')"
python3 tools/check_project_rules.py
uvx ruff check .
python3 -m unittest
```

ロジックテストは `tests/test_rogue_baseline.py` で Pyxel を mock して実行する。日本語切替込みの確認は次で行う。

```bash
PYXEL_ROGUE_LANG=ja python3 -m unittest
```

## コード構造

現行実装は root の `rogue.py` を入口にし、補助モジュールは `pyxel_rogue/` 配下に置く。

```
rogue.py
├── 定数・テーブル（POTIONS[12], SCROLLS[12], WEAPONS[9], ARMORS[8], BESTIARY[26]）
├── TextCatalog / LANG_EN / LANG_JA（日英切替・代表文言）
├── Room / Item / Monster / Player / IdentTable / DGen（ダンジョン生成）
└── Game（メイン: ステートマシン ST_PLAY/MENU/ITEM/DIR/STATUS/HELP/DEAD）
    ├── update: 入力 → upd_play / upd_menu / upd_item / upd_dir
    ├── draw:   80×22メインASCII + 右サイドHUD + 下ログ → オーバーレイ
    └── 各ステートに upd_xxx() と draw_xxx() が1対1で対応
```

単一ファイルは前提にしない。見通しがよく、Rogue 5.4.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。
新規の補助モジュールは root 直下の `rogue_*.py` ではなく、`pyxel_rogue/rogue_*.py` として追加する。

## 画面・マップ

- 現行マップ: Rogue 5.4.4 準拠の80×24論理座標、3×3セクターグリッド
- 地形・通路・部屋・プレイヤー移動領域: `x=0..79`, `y=1..22`
- 現行画面: 暫定640×320
- 現行レイアウト: 80×22メインASCII常時全表示 + 右サイドHUD + 下ログ
- メインASCII描画領域: 80×22タイル、現行セル 6×12px で 480×264px
- ミニマップとSelectから開く全体マップは置かず、探索情報はメインASCII表示へ集約する
- Full Map / 拡大全体マップは現方針では復活させない。必要ならメインASCII表示・探索済みセル・履歴表示を先に改善する
- 右サイドHUDは HP/Str/AC/Food/装備/状態異常/入力モードなど、状態確認の読みやすさを補助する用途に限定する
- これらは現在の実装値であり、固定仕様ではない
- ブラウザ、SteamDeck、中華ゲーム機で遊べることを重視し、画面サイズ変更時はレイアウト定数を一箇所で再計算できる設計に寄せる

## コーディング規約

- 定数 `UPPER_SNAKE`、クラス `PascalCase`、メソッド `snake_case`（短縮可: `msg`, `txt`, `kp`）
- カテゴリ: `CAT_POT`, `CAT_SCR`, `CAT_WPN`, `CAT_ARM`, `CAT_FOOD`, `CAT_GOLD`
- **データ駆動**: 新要素はテーブル追加で対応。コード分岐は最小限
- 全テキスト描画は `self.txt(x, y, s, col)` 経由
- ゲームログやUI文言は、段階的に `TextCatalog` 経由へ寄せる。新規文言は直書きだけで増やさず、日英切替を意識する
- Phase 4 以降の新規文言（指輪 / 杖 / 罠 / Amulet / 勝利 / search結果など）は最初から `TextCatalog` 経由にする
- 原作 Rogue 5.4.4 と照合しやすいよう、ゲームロジックと表示・入力処理の責務を混ぜすぎない
- Rogue2.Official は日本語表現の準拠元、Rogue 5.4.4 C ソースはゲーム挙動の準拠元として扱う
- Rogue 5.4.4 C ソースは、ローカルに `vendor/rogue544/` があれば必ずそこを先に参照する
- **ゲームメカニクスは常に Rogue 5.4.4 C ソース準拠**。確率、生成数、ターン消費、状態異常、攻撃判定、アイテム効果、罠、隠し要素、モンスターAIなど、ゲーム状態に影響する実装は該当する原作の関数・定数・テーブルを先に確認する
- 推測、現代ローグライクの慣習、Rogue2.Official、既存 Pyxel 実装をゲーム挙動の正解にしない。既存実装が Rogue 5.4.4 と食い違う場合は Rogue 5.4.4 を優先する
- Pyxel 都合の差分は表示・入力・移植UIに限定する。ゲーム状態が変わる差分が必要な場合は、理由と原作との差を `docs/design/rogue544.md` に記録してから実装する

## Rogue表記方針

- 詳細バージョンを書く場合は `Rogue 5.4.4` とする
- メジャーバージョンや系統を強調する場合は `Rogue V5` とする
- 詳細バージョンを途中で止めた短縮表記は新規に使わない

## README更新方針

- コード、操作体系、実装状況、セットアップ、Web版URL、ライセンスに影響する変更を行う場合は、`README.md` / `README.en.md` の更新要否を確認し、必要なら同じ変更で更新する
- README は外向けの入口、`docs/TODO.md` は詳細タスク、`docs/DESIGN.md` は設計判断の入口、`docs/design/*.md` は詳細仕様として役割を分ける

## 修正時のUX一貫性チェック

バグ修正・機能追加・UI変更では、場当たり的に該当箇所だけ直さず、触った機能の近傍でゲーム全体の一貫性も確認する。

- 同じ概念のUI・入力・文言が他にないか確認する
- キーボード/ゲームパッドの対応が揃っているか確認する
- 決定/キャンセル/戻り先が自然か確認する
- TextCatalog / README / DESIGN / docs/design / tests の更新要否を確認する
- 直す範囲は原則「同じ概念・同じ画面種別・同じ入力経路」までに留める
- 範囲が広がる場合は、今回直す範囲と別タスクに回す範囲を短く分けて提案する
- 一貫性として決めたことは、可能な限りテストか該当する `docs/design/*.md` に残す

## UI変更チェック

UI・入力・表示名を変更した場合は、完了前に以下を確認する。

- `NOTES.md` を作業前・作業後に読む
- `docs/design/ui.md` の疑似Markdown階層と role に合っているか確認する
- 表示名は単一ソースから出す。HUDだけ別翻訳キーなどを作らない
- 日本語表示だけ固定文言・直訳・不統一になっていないか確認する
- 入力変更は tap / hold / release の確定フレームを確認する
- 「出てはいけない表示」もテストする
- `NOTES.md` の終了項目を `Processed` へ移す

## バグ修正チェック

バグ・不具合を直した場合は、完了前に以下を行う。

- 作業前に `docs/BUG_PREVENTION.md` を読み、今回該当する見出しを選んで再発防止項目をチェックリスト化する。該当なしなら「該当なし」と明示してから進める
- なぜ埋め込んだかを短く振り返る
- 原因を二度と起こさない作業方策を考える
- その方策を現在のコードにも適用し、類似ケースを探す
- 必要な場合は `docs/BUG_PREVENTION.md` に `原因` / `再発防止` / `今回の適用` の形で追記する
- 仕様判断が変わる場合だけ、あわせて `docs/DESIGN.md` / `docs/design/*.md` / `docs/TODO.md` / `AGENTS.md` へ反映する
- 正しい挙動だけでなく、再発時に出るはずの誤表示・誤状態が出ないこともテストする
- 完了前に、作業前に作った再発防止チェックリストを消化したか確認する
- 一定期間ごと、または関連バグが続いた時は、直近の不具合傾向をまとめて作業ルールを更新する

## コミット方針

- コミットメッセージは、最後に触った変更だけでなく、前回コミットからの staged diff 全体を見て決める
- コミット前に `git diff --cached --stat` と必要に応じて `git diff --cached` を確認し、コード・テスト・設計文書の変更をまとめて表す件名にする
- 件名は断片的な作業名ではなく、ユーザーに見える成果や仕様変更のまとまりを表す。例: `Add in-game language toggle`、`Fix run input and document controls`
- 複数の独立した変更が混ざっている場合は、可能ならコミットを分ける。分けない場合でも、メッセージは全体をカバーする

## 操作方針

- 基本操作は A/B/Start/Select + D-pad を中心にする
- D-pad: 通常は8方向移動
- Start押下中: 斜め補助モード。離すと8方向移動モード（通常モード）に戻る
- 斜め補助モード中のD-padは、左上=NW、右上=NE、右下=SE、左下=SW の同時押しだけを受け付ける。上下左右単体は移動しない
- 斜め補助モード ON/OFF はステータス欄に表示する
- Start長押し依存は禁止（携帯機側の電源OFF等に割り当てられることがあるため）
- Select(Back): Info（Inventory / Log / Settings / Help）+ chord ショートカット。Info中のSelectは閉じる
- Select+A: quick throw（方向を選んでからアイテム選択）
- Select+B: 周囲8マス search
- Select+D-pad: 発見済み罠の種類確認（Rogue 5.4.4 `^` + 方向相当、ターン非消費）
- A: 決定 / 拾う / 階段 / 空押し時は正面1マス search
- A+B: 足踏み専用。search は兼ねない
- B: 短押しでメニュー/キャンセル、長押し+方向でダッシュ。ダッシュ後に離した瞬間の短押し誤発火を避ける
- X/Y/L/R: 当面は必須操作に割り当てない。将来のショートカット予約
- `btn()`=ホールド、`btnp()`=ワンショット。単押しと長押しの競合に注意する

## 技術要点

- フォント標準: `pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__), "examples", "assets", "umplus_j10r.bdf"))`
- `umplus_j10r.bdf` は ASCII 6px、CJK 10px、日本語対応
- 日本語表示は `PYXEL_ROGUE_LANG=ja pyxel run rogue.py` で確認でき、ゲーム中は Info の Settings タブの Language から日英を切り替えられる。現状は代表文言・用語のみ対応で、全メッセージ辞書化は継続タスク
- メッセージ分離は、全面リファクタを先行するより、触った機能周辺から段階的に進める
- 将来的なフォント選択は許容する。ただし ASCII ローグ表示に向く可読性を必須条件にする
- 右HUDタイトルの `Rogue V5 YYMMDD_HHMM` はテストプレイ用の改訂スタンプ。体感差の有無に関係なく、コード・テスト・設計文書などを変更したら同じ変更で `UI_BUILD` を更新する
- カメラ: 80×22地形領域の横幅は常時全表示。将来マップサイズ変更時に破綻しない互換処理として残す
- ダッシュ: B長押し＋方向。run 開始は `btnp()` ではなくホールド中の方向を拾い、B と D-pad の押下順に依存させない。壁・敵・ドア・分岐・階段で自動停止
- ダンジョン生成: Rogue 5.4.4 の C ソース確認を優先し、推測で似せない。通路生成は `do_passages()`, `conn()`, `door()`, `putpass()` の責務分担と比較できる形を保つ

## 禁止・注意事項

- Rogue 5.4.4 にない要素を追加しない（バージョン選択機能で対応予定）
- バージョン選択機能は短期的には低優先度。現行ターゲットは Rogue 5.4.4 に固定し、将来の Rogue V5 系を含む切替に備えて依存方向だけ整える
- 忠実度修正では、既知バグを baseline として固定しない。Rogue 5.4.4 の期待値テストを先に追加してから修正する
- 忠実度に関わる実装では、参照した Rogue 5.4.4 のファイル名・関数名・定数名をテスト名、コメント、または `docs/design/rogue544.md` から追えるようにする
- Phase 4 の完了条件は、26階の Amulet of Yendor 出現、Amulet 所持での1階帰還勝利、指輪・杖・罠・隠し要素が Rogue 5.4.4 の攻略判断に効く形で揃うこと
- 解像度変更時はレイアウト定数を全て再計算すること
- マップ本体は ASCII ローグライク描画を保つ
- Pyxel Web で動かすことを前提に、デスクトップ固有の挙動へ依存しすぎない
