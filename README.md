# crop2png_re

## 何ができるソフトですか？
自炊した画像ファイルから学習用データの加工を**定型サイズで高速トリミング**するソフト(位置決めは手動です)

コードはChatGPTにより出力されたものに手修正を入れています。

![image](https://github.com/user-attachments/assets/0a93d646-f082-4cc4-b77e-1789047ab4f3)

## 使い方
1. トリミングしたいファイルをどこかのフォルダにまとめてファイルかフォルダをウインドウにドラッグアンドドロップします。
2. トリミングしたいサイズをプリセットから選択、または直接入力して「Apply」ボタンをクリック(初期値は1024*1024px)
   ![image](https://github.com/user-attachments/assets/f90023e6-24e2-4f25-9c3d-fe6415743186)

1. トリミング枠が画像に表示されるので、赤枠、もしくは内側の部分をドラッグしてトリミングする範囲を調整します。
1. 範囲が問題なければキーボードのsを押すと、トリミング枠の部分をトリミングして画像で保存します。
1. 画像全体を使用する場合はキーボードのaでトリミング範囲を無視して全範囲を画像で保存します。
2. マウスホイールの前後で前後の画像ファイルを表示します。最後のファイルに到達したらフォルダの最初のファイルに戻ります。
1. トリミング範囲の画像(PNG形式)がソフトのoutputフォルダに作成されます。

## 注意
日本語やスペースを含むフォルダ構成でも使用可能にしたつもりですが、できる限り、フォルダ名は英数字のみを推奨します。またProgram Files等の特殊なフォルダにおいて使用することは推奨しません。
画像に対してトリミング枠が大きい場合は画像のサイズを最大として、画像を塗りつぶし等で拡張はしません。
何かあればissueに投げていただけると助かります。

### 初期プリセット一覧
presets.csvを修正すれば追加可能です。
|プリセット名|width|height|
|---|---|---|
|正1024×1024(1:1)|1024|1024|
|横1152×896(およそ4:3)|1152|896|
|横1216×832(およそ3:2)|1216|832|
|横1344×768(およそ16:9)|1344|768|
|横1568×672(21:9)|1568|672|
|横1728×576(3:1)|1728|576|
|縦512×2048(1:4)|512|2048|
|縦576×1728(1:3)|576|1728|
|縦768×1344(およそ9:16)|768|1344|
|縦832×1216(およそ2:3)|832|1216|
|縦896×1152(3:4)|896|1152|
