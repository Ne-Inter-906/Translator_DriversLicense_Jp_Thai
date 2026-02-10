import customtkinter as ctk
import Tr_Main as tm
import traceback # エラー詳細取得用
from tkinter import messagebox # ポップアップ通知用
from Similarity_Checker import SimilarityChecker

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Translator GUI v1.0")
        self.geometry("500x450")

        # 1. 実行モード選択
        self.mode_label = ctk.CTkLabel(self, text="【1】実行モード選択", font=("HGｺﾞｼｯｸE", 16))
        self.mode_label.pack(pady=(20, 5))
        
        self.mode_option = ctk.CTkOptionMenu(self, values=["all", "translate", "layout", "check"])
        self.mode_option.pack(pady=10)

        # 2. 翻訳対象の選択（チェックボックス）
        self.target_label = ctk.CTkLabel(self, text="【2】翻訳対象（翻訳モード時のみ）", font=("HGｺﾞｼｯｸE", 14))
        self.target_label.pack(pady=(20, 5))

        self.check_question = ctk.CTkCheckBox(self, text="問題文 (Question)")
        self.check_question.pack(pady=5)
        self.check_question.select() # デフォルトでチェック

        self.check_comment = ctk.CTkCheckBox(self, text="解説文 (Comment)")
        self.check_comment.pack(pady=5)

        # 3. リミット設定
        self.limit_label = ctk.CTkLabel(self, text="【3】行数制限 (空なら全件)", font=("HGｺﾞｼｯｸE", 14))
        self.limit_label.pack(pady=(20, 5))
        
        self.limit_entry = ctk.CTkEntry(self, placeholder_text="例: 16")
        self.limit_entry.pack(pady=5)

        # 4. 実行ボタン
        self.start_button = ctk.CTkButton(self, text="実行開始", 
                                         fg_color="green", hover_color="darkgreen",
                                         command=self.button_callback)
        self.start_button.pack(pady=30)

    # --- Tr_Gui.py 内の button_callback ---
    def button_callback(self):
        mode = self.mode_option.get()
        limit_str = self.limit_entry.get()
        limit = int(limit_str) if limit_str.isdigit() else None
        
        # 翻訳対象リストの作成
        targets = []
        if self.check_question.get(): targets.append("question")
        if self.check_comment.get(): targets.append("comment")

        if not targets and mode != "layout":
            print("エラー: 翻訳対象を少なくとも1つ選択してください")
            return

        print(f"--- 実行: {mode} (Target: {targets}, Limit: {limit}) ---")
        # ボタンを無効化（連打防止）
        self.start_button.configure(state="disabled", text="実行中...")
        # main関数を呼び出し（targets引数を追加）
        try:
            if mode == "check":
                # チェックモード専用の処理
                # ファイルパスはひとまず Tr_Main 等で定義している出力先を指定
                target_file = "data/output.xlsx" 
                
                # 列名のマッピング（エクセルの実際の見出し名と合わせる）
                columns = {
                    '問題文': '問題文', 
                    'ปัญหา': 'ปัญหา', # ここは実際のエクセルの列名に書き換えてください
                    '解説': '解説', 
                    'คำอธิบาย': 'คำอธิบาย' # ここも同様
                }
                
                checker = SimilarityChecker()
                checker.check_file(target_file, columns)
                messagebox.showinfo("完了", f"チェックが完了しました！\n{target_file.replace('.xlsx', '_checked.xlsx')}")
            
            else:
                # 既存の翻訳・レイアウト処理
                tm.main(mode=mode, limit=limit, targets=targets)
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"エラーが発生しました：\n{error_msg}")
            messagebox.showerror("エラー", f"実行中にエラーが発生しました：\n\n{str(e)}")
        finally:
            #ボタン最有効化
            self.start_button.configure(state="normal", text="実行開始")


if __name__ == "__main__":
    app = App()
    app.mainloop()