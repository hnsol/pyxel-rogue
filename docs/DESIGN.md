# DESIGN.md — 設計判断の入口

この文書は設計文書の入口、索引、大方針を置く。詳細仕様は `docs/design/` 配下を読む。

## 大方針

プロジェクト名・体験名は `Rogue V5 on Pyxel` とする。ゲームメカニクスの基準は Rogue 5.4.4 だが、プロジェクト全体は Rogue V5 系の Pyxel 版として扱う。

最終目標は、Pyxel 版をクリアしたら Rogue V5 をクリアしたと言える状態にすること。Rogue 5.4.4 は、Rogue V5 系のゲームメカニクスを検証可能にするための底本として扱う。

実装は、原作と同じロジックか検証できる構造を優先する。表示・入力・移植性の都合で Pyxel 向けの実装差分が必要な場合も、ゲームロジックは原作と照合しやすく保つ。

詳細なバージョンを書く場合は `Rogue 5.4.4` とし、メジャーバージョンや系統を強調する場合は `Rogue V5` とする。詳細バージョンを途中で止めた短縮表記は新規に使わない。

README は外向け仕様、遊び方、公開リンク、実装概要の入口として扱う。詳細な作業一覧は `docs/TODO.md`、設計判断の詳細は `docs/design/` に置く。

## 設計文書索引

- `docs/design/ui.md`: 表示、入力、パレット、フォント、言語、移植UI。
- `docs/design/rogue544.md`: Rogue 5.4.4 忠実度、原作参照、ゲームメカニクス、生成、AI、アイテム。
- `docs/design/project.md`: プロジェクトの発端、Rogue表記、README運用。
- `docs/design/architecture.md`: ファイル分割、repo美化、テスト、mock、コミット運用。
- `docs/design/bgm.md`: BGM生成、再生タイミング、ゲーム乱数からの分離。
- `docs/design/online.md`: 死亡・勝利・スコア・オンライン同期・名前入力。
- `docs/design/variants.md`: 難易度、将来候補、Rogue V5系バリアント。

## 作業別に読む文書

- UI、入力、表示名、パレット、フォント、言語を触る: `docs/design/ui.md`
- 確率、ターン消費、状態異常、攻撃、アイテム、罠、AI、ダンジョン生成を触る: `docs/design/rogue544.md`
- プロジェクト説明、Rogue表記、README運用を触る: `docs/design/project.md`
- 難易度、バージョン選択、将来候補を触る: `docs/design/variants.md`
- BGMや音まわりを触る: `docs/design/bgm.md`
- スコア、死亡・勝利画面、オンライン同期、名前入力を触る: `docs/design/online.md`
- ファイル分割、テスト、repo整理、mock、コミット運用を触る: `docs/design/architecture.md`

## 運用

設計判断を追加するときは、まず上の索引から置き場を選ぶ。複数文書へ同じ詳細を重複させず、入口には短い概要とリンクだけを置く。

仕様変更を伴う場合は、必要に応じて `docs/TODO.md`、`README.md`、`README.en.md`、`AGENTS.md` も同じ変更で更新する。
