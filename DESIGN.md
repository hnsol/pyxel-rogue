# DESIGN.md — 設計判断の記録

## プロジェクトの発端

黎明期の名作を Pyxel で再現する企画から、ローグをコントローラ操作対応で作る方向に決定。その後「過剰にオーバースペックな Pyxel 版・元祖ローグ」にコンセプトが発展した。

最終目標は、Pyxel 版をクリアしたら本物の Rogue 5.4 をクリアしたと言える状態にすること。Rogue 5.4 準拠を主軸にし、将来的にはフォント切替 / 日英切替 / BGM / 拡大画面+マップ / バージョン選択（3.6 / 5.2 / 5.4）を検討する。

実装は、原作と同じロジックか検証できる構造を優先する。表示・入力・移植性の都合で Pyxel 向けの実装差分が必要な場合も、ゲームロジックは原作と照合しやすく保つ。

短期的にはバージョン選択機能の優先度を下げ、Rogue 5.4 を単一ターゲットとして忠実度を上げる。将来の 3.6 / 5.2 / 5.4 切替に備えて、ゲームロジック、文言、入力・描画の依存方向は分離しやすく保つが、今はバージョン別分岐を先行追加しない。

## 対象環境

対象をデスクトップに限定せず、Python/Pyxel 本体に加えて Pyxel Web でも遊べることを前提にしたい。ブラウザ、SteamDeck、中華ゲーム機などでも破綻しない入力・画面構成を重視する。

512×320 画面を新しい基準にし、48×24 マップ、3×3セクターグリッドを常時全表示する方針にする。移植性のため、レイアウト定数は将来的に画面サイズから再計算できるようにする。

## 画面レイアウト

目標レイアウトは、48×24 のメインASCIIダンジョン表示を常時すべて見せる。現行セル 7×12px なら描画領域は 336×288px になり、512×320 画面の左側に収める。右側にはサイドHUD、下部には短いメッセージログを置く。

ミニマップと全体マップUIは廃止する。元祖ローグでは、見えているASCIIダンジョン表示そのものが地図であり、別レイヤーの地図UIを足すと探索体験が現代ローグライク寄りになりすぎるため。探索情報はメインASCII表示に集約する。

現代的UIは探索情報を増やすためではなく、状態確認を読みやすくするために使う。右サイドHUDには HP、Str、AC、Food、装備、状態異常、Depth、Turn、Gold、入力モードなどをまとめる。常時インベントリ全表示、敵一覧、周辺警告レーダーのような便利すぎる情報は通常画面には置かない。詳細な履歴表示は後続のメッセージ履歴スクロールで扱う。

## 操作体系

当初は GB 版「風来のシレン」の D-pad + 少数ボタン操作を参考にした。現方針では、より携帯機・ブラウザ・Pyxel Web 向けに、A/B/Start/Select + D-pad を基本操作にする。

```
D-pad                 通常は8方向移動
Start短押し          斜め補助モード / 8方向移動モード（通常モード）のトグル
斜め補助モード中      左上/右上/右下/左下の同時押しだけを NW/NE/SE/SW として扱う
A                     決定 / 拾う / 階段
B短押し               キャンセル / メニュー
B長押し + D-pad       ダッシュ
Select(Back)          補助メニュー（Status / Help / Search）
X/Y/L/R               当面は必須操作にしない。将来のショートカット予約
```

Start長押しは携帯機側の電源OFF等に割り当てられることがあるため、ゲーム操作として依存しない。斜め補助モードは、SteamDeck、ブラウザ、携帯機で斜め入力を安定させるための移植UIとして扱う。通常時の8方向移動とは別扱いにし、斜め補助モード中は上下左右単体入力では移動しない。

B はダッシュ（ホールド）とキャンセル/メニュー（単押し）を兼務する。`btn()` と `btnp()` の扱い、離した瞬間の誤発火には注意する。斜め補助モード ON/OFF はステータス欄に表示し、現在の入力モードが常に分かるようにする。

Select(Back) は補助メニューにする。ステータス、ヘルプ、search の入口を1か所にまとめることで、A/B/Start/Select + D-pad だけで主要操作を完結させる。マップは常時48×24で全表示するため、補助メニューには置かない。

ダッシュ/走行は Rogue 5.4 の `command.c` / `move.c` / `misc.c` を参照し、`do_run()`, `do_move()`, `turn_ok()`, `look()` の挙動へ寄せる。通路のL字角では、前方が壁で左右どちらか一方だけに曲がれる場合、`turn_ok()` 相当の判定で方向転換して走り続ける。部屋内では Rogue 5.4 の `door_stop` 相当を常時ONとして扱い、壁沿いに走っているとき前方側の周囲に扉や分岐が見えたら停止する。

HP自然回復と空腹は Rogue 5.4 の `daemons.c` にある `doctor()` / `stomach()` を基準にする。HPはターン経過で `quiet` が進み、低レベルではゆっくり、高レベルでは速く回復する。空腹は `HUNGERTIME`, `MORETIME`, `STOMACHSIZE`, `STARVETIME` の閾値を使い、食料切れ直後から毎ターンHPを削る挙動にはしない。

## フォント

Pyxel 標準フォント 4×6px は小さく、ASCII ローグの可読性に不安があった。`pyxel.Font(path)` で BDF 読込可能と判明し、現行では Pyxel 同梱の `umplus_j10r.bdf` を標準にしている。ASCII 6px / CJK 10px / 7187文字で日本語にも対応する。

```python
import os
font = pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__),
                                "examples", "assets", "umplus_j10r.bdf"))
```

当面は `umplus_j10r.bdf` を使うが、将来的なフォント選択は許容する。ただしローグの画面表示に向く可読性を必須条件にする。

## 日本語 / 英語切替

ゲーム挙動は Rogue 5.4 準拠、日本語表現は Rogue2.Official 準拠として扱う。Rogue2.Official は日本語メッセージ、アイテム名、モンスター名、ヘルプ文言などの表現ソースであり、ゲームロジックや確率・ターン処理の正解としては使わない。

参照元:

- https://github.com/suzukiiichiro/Rogue2.Official
- `mesg_J`: 日本語メッセージ・用語
- `mesg_E`: 英語メッセージとの対応確認

現行実装では `TextCatalog` と `LANG_EN` / `LANG_JA` を導入し、`PYXEL_ROGUE_LANG=ja python3 rogue.py` で日本語表示を選べる入口を用意した。まだ全メッセージ辞書化は完了していない。歓迎文、空腹、探索、戦闘、拾得、メニュー項目、アイテム名・モンスター名の代表範囲から段階的に `TextCatalog` 経由へ移行している。

翻訳層はゲーム状態を変えない表示レイヤーとして扱う。同じ seed と同じ操作なら、英語 / 日本語の違いでプレイヤー位置、所持品、ターン、HP、モンスター配置などのゲーム状態が変わってはいけない。

## カメラ

現行48×24マップを常時全表示する目標レイアウトでは、通常プレイ中のカメラスクロールは不要になる。カメラ処理は、将来マップサイズを変更した場合や表示タイル数がマップより小さい場合にも破綻しない互換処理として残す。

## ダンジョン生成

元祖ローグの3×3セクターグリッドアルゴリズムを再現。現行では48×24マップを16×8セクターに分割、6〜9部屋配置、隣接セクター間を通路接続、flood fill で到達保証している。

マップ寸法は現行値であり固定仕様ではないが、原作ロジックとの比較可能性を崩さないことを優先する。

通路生成は Rogue 5.4 C ソースの `passages.c` を参照し、推測で似せない。特に `do_passages()` が部屋グラフを作り、`conn()` が接続方向に応じて壁上のドア位置を選び、`door()` が部屋の出口を記録し、`putpass()` が通路を掘る責務分担を基準にする。

現スプリントでは通常部屋の通路接続だけを対象にする。`ISGONE` / `ISMAZE`、隠しドア、隠し通路は後続タスクとして残し、実装時に Rogue 5.4 の該当ロジックと照合する。

## 死亡画面とスコア

死亡画面はブラウザ・携帯機でのテストプレイを続けやすくする移植UIとして追加する。Depth、Level、Gold、Exp、Turn、死因を表示し、A または Start で新規ゲームへ戻れるようにする。

スコア履歴保存は死亡画面とは分ける。JSONによるハイスコア保存と履歴画面は Phase 7 の仕上げタスクとして扱う。

## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

## ファイル構成

現行実装は `rogue.py` 中心だが、単一ファイルは前提にしない。見通しがよく、Rogue 5.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。

分割する場合は、ゲームロジック、データテーブル、入力、描画、プラットフォーム差分の境界を意識する。

現時点では大規模分割よりも、依存方向を整える小さな整理を優先する。`Game` 内にはまだロジック、入力、描画、文言が同居しているため、まず `TextCatalog` とロジックテストで境界を作り、以後の機能追加時に必要な範囲から分離する。

## テスト方針

最初の一手は「最小テスト → 最小翻訳層 → baseline 拡充」とする。翻訳層はリファクタリングなので、最低限のテストで import / 初期化 / ダンジョン到達性 / 初期装備を守り、その後に翻訳層込みの baseline を増やす。

テストは標準ライブラリの `unittest` で実行できる。

```bash
python3 -m unittest
PYXEL_ROGUE_LANG=ja python3 -m unittest
```

baseline テストは「壊れてほしくない現状」を固定するためのもの。Rogue 5.4 と違う既知バグを正当化するためには使わない。忠実度修正では、Rogue 5.4 C ソースの該当関数・定数に基づく期待値テストを先に追加し、失敗を確認してから実装を直す。

## BGM（しろもふさん自動演奏ツール）

参照候補:

- しろもふさん自動演奏ツール: https://github.com/shiromofufactory/8bit-bgm-generator
- Pyxel組み込み例: https://github.com/hnsol/pyxel-hadegame の `pyxelhg/bgm/bgm_generator.py`

Pyxel サウンド / ミュージックへの組み込み方、Pyxel Web での鳴り方、モジュール化して import する方法を検討する。

## 元祖ローグのソース参照先

https://github.com/Davidslv/rogue （Rogue 5.4 C ソース）

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
