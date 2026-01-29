# AutoTranslator with Layout Preserving

Excelのレイアウト（セル結合、幅、高さ、書式）を維持したまま、
AIで日本語からタイ語へ翻訳を行うツールです。

## 特徴
- セルの結合やフォント設定を崩さずに翻訳結果を書き戻し
- 独自の対訳辞書による用語固定機能（wrong列はユニーク、right列は重複可）
- バッチ処理による高速な翻訳

## セットアップ
1. ライブラリのインストール
   pip install -r requirements.txt

2. 翻訳元ファイルの準備
　 temlates\Driver'sLisence_MockTest.xslxと同じセル構成で出力されますので、同様の構造のinput.xlsxを作成してdataフォルダ内に配置します
   そのinput.xlsxのB列2行目以降に翻訳したい日本語問題文、同じくF列に解説の問題文をセットしてください

3. 実行
   python Tr_Main.py