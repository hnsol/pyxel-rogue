[[English](README.en.md) | 日本語]

# Pyxel Rogue

オリジナルのローグ（Rogue 5.4.4）を Pyxel で再現します。

目指しているのは「この Pyxel 版をクリアしたら、Rogue 5.4.4 をクリアしたと言える」状態にすること。Rogue V5 系の手触りを大事にしながら、ゲームメカニクスは Rogue 5.4.4 のソースを一次情報にし、表示・入力・移植性は Pyxel / Pyxel Web で遊びやすい形へ調整しています。

## 目指していること

- ASCII ベースの Pyxel 版・元祖ローグを作る
- Rogue 5.4.4 C ソースに照合しやすいゲームロジックを保つ
- ブラウザ、デスクトップ、SteamDeck、中華ゲーム機などで遊べる形に近づける
- 便利すぎる現代UIではなく、Rogue らしい探索判断と緊張感を残す
- 日本語版ローグの文脈も参照しながら、日英切替できる実装へ育てる

詳しい設計判断は [DESIGN.md](DESIGN.md)、作業状況は [TODO.md](TODO.md) を参照してください。

## スクリーンショット

![Pyxel Rogue screenshot](docs/images/pyxel-rogue-screenshot.png)

Rogue 5.4.4 準拠の80桁ASCIIマップ、右HUD、下ログを表示したプレイ画面。

## Webで遊ぶ

ブラウザでは Pyxel Web Launcher から起動できます。

[Pyxel Rogue をWebで起動する](https://kitao.github.io/pyxel/web/launcher/?run=hnsol/pyxel-rogue/master/rogue&gamepad=enabled)

Web版は Python や Pyxel を手元に入れずに試せます。ゲームパッドを有効にしていますので、スマートフォンやタブレットでも遊べます。

## 手元でダウンロードして遊ぶ

Python 3.10+ と Pyxel が必要です。

```bash
git clone https://github.com/hnsol/pyxel-rogue.git
cd pyxel-rogue
pip install pyxel
pyxel run rogue.py
```

日本語表示で起動する場合:

```bash
PYXEL_ROGUE_LANG=ja pyxel run rogue.py
```

開発者向けの簡易チェック:

```bash
python3 -m unittest
PYXEL_ROGUE_LANG=ja python3 -m unittest
```

Rogue 5.4.4 準拠の実装確認を行う場合は、原作 C ソースをローカル参照用に置けます。このディレクトリは `.gitignore` で除外され、リポジトリには含めません。

```bash
mkdir -p vendor
git clone https://github.com/Davidslv/rogue.git vendor/rogue544
```

## 操作

ゲームパッド:

- D-pad: 8方向移動
- Start短押し: 斜め補助モード / 通常8方向モードを切替
- A: 決定 / 拾う / 階段 / 正面1マスsearch
- B短押し: メニュー / キャンセル
- B長押し + D-pad: ダッシュ
- A+B: 足踏み
- Select: 補助メニュー
- Select+A: 周囲8マスsearch
- Select+B: quick throw（方向を選んでからアイテム選択）
- Select+D-pad: 発見済み罠の種類確認

キーボード:

- 矢印 / HJKL: 移動
- YUBN: 斜め移動
- Space: 斜め補助モード切替
- Enter: 決定 / 拾う / 階段 / 正面1マスsearch
- Enter+Esc: 足踏み
- Shift+方向: ダッシュ
- Esc: メニュー / キャンセル
- Tab: 補助メニュー
- 補助メニュー: Inventory / Help / Search / Trap / Pickup / Language / Palette / Quit
- Tab+Enter: 周囲8マスsearch
- Tab+Esc: quick throw
- Tab+方向: 発見済み罠の種類確認
- .: 足踏み
- s: 周囲8マスsearch
- t: quick throw
- ^: Trap Inspect（方向指定）
- i: Inventory
- ?: Help
- q/r/e/z: Quaff / Read / Eat / Zap
- w/W/T: Wear / Wield / Take off

杖はメニューの Zap から選び、方向を指定して振ります。

## 主な実装状況

実装済みの概要:

- Rogue 5.4.4 準拠の80x24論理マップ、80x22地形表示、576x360の16:10寄りレイアウト、短縮装備表示つき右HUD、7行下ログ
- 3x3セクターのダンジョン生成、部屋、通路、ドア
- 26種モンスター、戦闘、空腹、HP自然回復
- ポーション、巻物、食料、武器、防具、指輪、識別、インベントリ、呪い
- 杖の14種テーブル、ランダム素材名、チャージ、Zap方向指定入口、light、単体モンスター対象系、haste/slow monster の効果
- search、罠、隠しドア、隠し通路、Trap Inspect
- Amulet of Yendor、Amulet 所持での1階帰還勝利
- 自動拾得ON/OFF、投擲アニメーション
- 墓石つき死亡画面
- 起動ロゴ、タイトル画面、英数字8文字のプレイヤー名入力
- Google Sheets + Apps Script 連携用の Daily Top Ten / Weekly Rivals / Season Legends オンラインランキング雛形
- ゲームパッド向け A/B/Start/Select + D-pad 操作
- JSONメッセージカタログによる日英切替基盤、ロジックテスト基盤
- Rogue2.Official の `mesg_E` / `mesg_J` を参考データとして同梱

実装状況の詳細は [TODO.md](TODO.md) を参照してください。

オンラインランキングは Google Sheets + Apps Script 連携用の雛形を `docs/apps_script_scoreboard.gs` に置いています。公開先を差し替える場合は `PYXEL_ROGUE_SCORE_URL` を指定してください。スコアボードは入場時に Daily / Weekly / Season をまとめて同期し、タブ切替では通信せず、R / Select で3期間を手動更新できます。オンライン投稿はゲーム終了時のみ行い、`score_id` で重複行を抑止します。Pyxel Rogue は起動ロゴ中に `?action=seedDummy` を呼び、Apps Script が各期間の表示Top10に足りない分だけダミー行を生成して Sheet に一括書き込みします。

## 今後の予定

- 杖の bolt / magic missile / drain life 系効果
- Rogue 5.4.4 期待値テスト拡充
- HUD / Inventory / Help / Death の文言辞書化
- 可変レイアウト、フォント選択
- BGM
- ハイスコア全履歴、オンラインランキング運用改善
- リプレイ

## 参考リンク

Rogue / Rogue 5.4.4:

- [RogueBasin: Rogue](https://www.roguebasin.com/?title=Rogue)
- [Davidslv/rogue: Original Rogue Game 5.4.4](https://github.com/Davidslv/rogue)

Rogue Clone / 日本語版ローグ:

- [RogueBasin: Rogue Clone](https://www.roguebasin.com/index.php/Rogue_Clone)
- [suzukiiichiro/Rogue2.Official](https://github.com/suzukiiichiro/Rogue2.Official)

Pyxel:

- [Pyxel User Guide](https://kitao.github.io/pyxel/web/user-guide/)
- [kitao/pyxel](https://github.com/kitao/pyxel)
- [Pyxel PyPI](https://pypi.org/project/pyxel/)
- [How To Use Pyxel Web](https://github.com/kitao/pyxel/wiki/How-To-Use-Pyxel-Web/3c7ccc624e95584ecc1c9696628cafca91bff7df)

## ライセンス

MIT License です。詳細は [LICENSE](LICENSE) を参照してください。
