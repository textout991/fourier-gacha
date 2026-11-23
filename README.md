# Fourier Gacha

A Blender 3.6 LTS add-on that generates random organic 3D shapes
from a double Fourier series. Press "Gacha!" and a new shape appears.



https://github.com/user-attachments/assets/330beca7-d5f4-4915-85f1-32562b436846



## 概要

2重フーリエ級数を使って、球と同相なランダムな有機的形状を生成するBlenderアドオンです。
「Gacha!」ボタンを押すたびに、新しい形が出てきます。
「分割数」でメッシュの細かさを、「形状レベル」で形状の複雑さを調整できます。

## 動作確認環境

- Blender 3.6 LTS
- OS：Windows10
- 4.x以降は動作未確認です（動かない可能性があります）。

## インストール方法

1. [Releases] https://github.com/textout991/fourier-gacha/releases からPythonファイル（.py）をダウンロードします。
2. Blenderで「編集 > プリファレンス > アドオン > インストール」を開き、ダウンロードしたファイルを選びます。
3. 一覧に出る「Add Mesh: Fourier Gacha」にチェックを入れて有効化します。

## 使い方

1. 3Dビューポートで N キーを押してサイドバーを開き、「Gacha」タブを選びます。
2. 「Gacha!」を押すと、形状が生成されます。もう一度押すと、新しい形に置き換わります。
3. スライダーで調整します。
   - **分割数**：2～8。大きいほど滑らかです。
   - **形状レベル**：1～64。大きいほど形状が複雑になります。

### 注意

- オブジェクトモードで使ってください。
- 形はファイルを保存すれば残ります。気に入った形は、OBJなどで書き出すこともできます。
- 手で編集したメッシュは、スライダーを動かすと、元の形で上書きされます。

## ライセンス・注意事項

- ライセンス：GPL-3.0-or-later
- 無保証です。自己責任でご利用ください。
- 多言語表示に対応していますが、翻訳は機械的に作成したもので、ネイティブの確認を受けていません。誤りがあればお知らせください。

## 感想・不具合

[Issues] https://github.com/textout991/fourier-gacha/issues までお気軽にどうぞ。

## 作者

textout
