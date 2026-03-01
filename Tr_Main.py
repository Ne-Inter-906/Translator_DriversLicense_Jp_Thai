import os
import sys
from Layout_Manager import Layout_Manager
from quiz_creator import Quiz_Creator

def get_paths():
    # ディレクトリパスを取得
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 相対パスで指定
    return {
        "jp_csv":  os.path.join(base_dir, "config", "jp_norm.csv"),
        "th_csv":  os.path.join(base_dir, "config", "th_norm.csv"),
        "in_file": os.path.join(base_dir, "data", "input.xlsx"),
        "out_file": os.path.join(base_dir, "data", "output.xlsx"),
        "template_file": os.path.join(base_dir, "templates", "Driver'sLisence_MockTest.xlsx"),
        "json_file": os.path.join(base_dir, "quizApp","questions.js"),
        "checked_file" : os.path.join(base_dir, "data", "output_checked.xlsx")
    }

def main(mode="all",limit=None,targets=None, input_file_path=None, threshold=0.75):
    if targets is None:
        targets = ["question"]
    paths = get_paths()

    # UIから渡されたファイルパスがあれば、デフォルトの in_file を上書き
    if input_file_path:
        paths["in_file"] = input_file_path

    if mode == "create_quiz":
        print("webアプリ作成モード")
        quiz_input = paths["checked_file"]
        if input_file_path:
            quiz_input = input_file_path
        Quiz_Creator.create_questions_js(quiz_input, paths["json_file"])

    if mode in ["all","translate"]:
        print("翻訳モード")
        # 各クラスのインスタンス化
        # 翻訳機能を使う場合のみ重いライブラリをインポートする
        from batch_translator import Batch_Translator
        from row_translator import Row_Translator
        from excel_manager import Excel_Manager

        bt = Batch_Translator()
        rt = Row_Translator(bt)
        em = Excel_Manager(paths["jp_csv"], paths["th_csv"], bt, rt)

        for target in targets:
        
            current_in = paths["in_file"] if target == targets[0] else paths["out_file"]
            
            em.execute(current_in, paths["out_file"], batch_size=16, mode=target, limit=limit)
    
    if mode in ["all","layout"]:
        print("整形モード")
        lm = Layout_Manager()
        template_path = paths["template_file"]
        lm.sync_layout(template_path,paths["out_file"],paths["out_file"])
        
    if mode == "check":
        print("チェックモード")
        from Similarity_Checker import SimilarityChecker
        
        target_file = input_file_path if input_file_path else paths["out_file"]
        
        columns = {
            '問題文': '問題文', 
            'ปัญหา': 'ปัญหา', 
            '解説': '解説', 
            'คำอธิบาย': 'คำอธิบาย'
        }
        
        checker = SimilarityChecker()
        return checker.check_file(target_file, columns, threshold=threshold)
    