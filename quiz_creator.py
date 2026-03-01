import pandas as pd
import json
import base64
from io import BytesIO
from openpyxl import load_workbook
from PIL import Image

class Quiz_Creator:
    @staticmethod
    def create_questions_js(excel_path, output_path):
        print(f"Reading : {excel_path}")
        try:
            #画像データ抽出
            wb = load_workbook(excel_path)
            ws = wb.active
            image_loader = {}
            for image in ws._images:
                row = image.anchor._from.row + 1  # 0始まりなので+1してExcelの行番号に合わせる
                
                # 画像をバイナリとして読み込み
                img_data = image._data()

                # --- Pillowを使って画像をリサイズ ---
                img = Image.open(BytesIO(img_data))
                
                # フォーマットを取得 (リサイズするとimg.formatが消えることがあるため先に取得)
                img_format = img.format
                if not img_format:
                    img_format = 'PNG'

                # 画像の最大幅を250pxに設定し、アスペクト比を維持してリサイズ
                max_width = 250
                if img.width > max_width:
                    w_percent = (max_width / float(img.width))
                    h_size = int((float(img.height) * float(w_percent)))
                    # 高品質なリサンプリング方法(LANCZOS)を指定
                    img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)

                # リサイズした画像をメモリ上のバイナリに変換
                buffered = BytesIO()
                img.save(buffered, format=img_format)
                img_data = buffered.getvalue()
                # --- リサイズ処理ここまで ---

                # MIMEタイプを決定
                mime_type = f"image/{img_format.lower()}"
                if img_format.upper() == 'JPEG':
                    mime_type = 'image/jpeg'

                # Base64に変換
                b64_str = base64.b64encode(img_data).decode('utf-8')
                # data URI形式にする (MIMEタイプを動的に設定)
                image_loader[row] = f"data:{mime_type};base64,{b64_str}"

            #テキストデータ抽出
            df = pd.read_excel(excel_path)
            fixed_keys = [
                "id"
                ,"state"
                ,"state_Translated"
                ,"image"
                ,"answer"
                ,"exp"
                ,"exp_Translated"
            ]

            df = df.iloc[:,:7]
            df.columns = fixed_keys

            for index, row in df.iterrows():
                excel_row_num = index + 2
                if excel_row_num in image_loader:
                    df.at[index, 'image'] = image_loader[excel_row_num]
                else:
                    df.at[index, 'image'] = ""

            # JSON形式（辞書のリスト）に変換
            questions = df.to_dict(orient='records')

            # JSファイルとして書き出し
            # ブラウザで直接読み込めるように変数定義を頭に付けます
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("const questions = ")
                json.dump(questions, f, ensure_ascii=False, indent=4)
                f.write(";")
            
            print(f"Successfully created: {output_path}")

        except Exception as e:
            print(f"Error: {e}")