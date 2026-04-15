# DESIGN.md — 設計判断の記録

## プロジェクトの発端

黎明期の名作を Pyxel で再現する企画から、ローグをコントローラ操作対応で作る方向に決定。その後「過剰にオーバースペックな Pyxel 版・元祖ローグ」にコンセプトが発展した。

最終目標は、Pyxel 版をクリアしたら本物の Rogue 5.4 をクリアしたと言える状態にすること。Rogue 5.4 準拠を主軸にし、将来的にはフォント切替 / 日英切替 / BGM / 拡大画面+マップ / バージョン選択（3.6 / 5.2 / 5.4）を検討する。

実装は、原作と同じロジックか検証できる構造を優先する。表示・入力・移植性の都合で Pyxel 向けの実装差分が必要な場合も、ゲームロジックは原作と照合しやすく保つ。

## 対象環境

対象をデスクトップに限定せず、Python/Pyxel 本体に加えて Pyxel Web でも遊べることを前提にしたい。ブラウザ、SteamDeck、中華ゲーム機などでも破綻しない入力・画面構成を重視する。

現行の 480×310 画面、48×24 マップ、3×3セクターグリッドは実装値であり、固定仕様ではない。移植性のため、レイアウト定数は将来的に画面サイズから再計算できるようにする。

## 操作体系

当初は GB 版「風来のシレン」の D-pad + 少数ボタン操作を参考にした。現方針では、より携帯機・ブラウザ・Pyxel Web 向けに、A/B/Start/Select + D-pad を基本操作にする。

```
D-pad          通常は8方向移動
Start短押し   斜め移動モード / 8方向移動モード（通常モード）のトグル
A              決定 / 拾う / 階段
B              キャンセル / メニュー / ダッシュ補助の中心候補
Select(Back)   マップまたは補助操作の候補
X/Y/L/R        当面は必須操作にしない。将来のショートカット予約
```

Start長押しは携帯機側の電源OFF等に割り当てられることがあるため、ゲーム操作として依存しない。斜め移動モードは、D-padで斜め4方向を安定して出すための入力補助として扱う。

B はダッシュ（ホールド）とキャンセル/メニュー（単押し）を兼務する可能性がある。`btn()` と `btnp()` の扱い、離した瞬間の誤発火には注意する。

## フォント

Pyxel 標準フォント 4×6px は小さく、ASCII ローグの可読性に不安があった。`pyxel.Font(path)` で BDF 読込可能と判明し、現行では Pyxel 同梱の `umplus_j10r.bdf` を標準にしている。ASCII 6px / CJK 10px / 7187文字で日本語にも対応する。

```python
import os
font = pyxel.Font(os.path.join(os.path.dirname(pyxel.__file__),
                                "examples", "assets", "umplus_j10r.bdf"))
```

当面は `umplus_j10r.bdf` を使うが、将来的なフォント選択は許容する。ただしローグの画面表示に向く可読性を必須条件にする。

## カメラ

1歩ごとの中央追従は酔いやすいため、現行はデッドゾーン方式。現在の実装値は `DEAD_ZONE = 5` だが、追従開始が端すぎる体感がある。

次の調整では、追従開始を早める。具体値は実装時に `DEAD_ZONE` を広げるか、表示範囲に対する比率で指定する方式を検討する。

## ダンジョン生成

元祖ローグの3×3セクターグリッドアルゴリズムを再現。現行では48×24マップを16×8セクターに分割、6〜9部屋配置、隣接セクター間を通路接続、flood fill で到達保証している。

マップ寸法は現行値であり固定仕様ではないが、原作ロジックとの比較可能性を崩さないことを優先する。

## アイテム識別

ゲーム開始時にポーション12色・巻物音節名をシャッフル。使用で判明。IdentTable クラスで管理。

## ファイル構成

現行実装は `rogue.py` 中心だが、単一ファイルは前提にしない。見通しがよく、Rogue 5.4 の原作ロジックと比較しやすく、テストしやすい構造になるなら分割してよい。

分割する場合は、ゲームロジック、データテーブル、入力、描画、プラットフォーム差分の境界を意識する。

## BGM（しろもふさん自動演奏ツール）

参照候補:

- しろもふさん自動演奏ツール: https://github.com/shiromofufactory/8bit-bgm-generator
- Pyxel組み込み例: https://github.com/hnsol/pyxel-hadegame の `pyxelhg/bgm/bgm_generator.py`

Pyxel サウンド / ミュージックへの組み込み方、Pyxel Web での鳴り方、モジュール化して import する方法を検討する。

## 元祖ローグのソース参照先

https://github.com/Davidslv/rogue （Rogue 5.4 C ソース）

## ロジックテスト用 mock 手順

`python3` の REPL か `python3 -c` で実行する想定。

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
