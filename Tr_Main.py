import os
import sys
from Layout_Manager import Layout_Manager
from batch_translator import Batch_Translator
from row_translator import Row_Translator
from excel_manager import Excel_Manager

def main(mode="all",limit=None,targets=None):

    if targets is None:
        targets = ["question"]

    # ディレクトリパスを取得
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 相対パスで指定
    paths = {
        "jp_csv":  os.path.join(base_dir, "config", "jp_norm.csv"),
        "th_csv":  os.path.join(base_dir, "config", "th_norm.csv"),
        "in_file": os.path.join(base_dir, "data", "input.xlsx"),
        "out_file": os.path.join(base_dir, "data", "output.xlsx")
    }
    

    if mode in ["all","translate"]:
        print("翻訳モード")
        # 各クラスのインスタンス化
        bt = Batch_Translator()
        rt = Row_Translator(bt)
        em = Excel_Manager(paths["jp_csv"], paths["th_csv"], bt, rt)

        for target in targets:
        
            current_in = paths["in_file"] if target == targets[0] else paths["out_file"]
            
            em.execute(current_in, paths["out_file"], batch_size=16, mode=target, limit=limit)
    
    if mode in ["all","layout"]:
        print("整形モード")
        lm = Layout_Manager()
        template_path = os.path.join(base_dir, "templates", "Driver'sLisence_MockTest.xlsx")

        lm.sync_layout(template_path,paths["out_file"],paths["out_file"])

if __name__ == "__main__":
    main(mode="layout",limit=None)