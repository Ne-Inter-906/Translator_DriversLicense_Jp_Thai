import customtkinter as ctk
import traceback # エラー詳細取得用
import threading # スレッド処理用
from tkinter import messagebox # ポップアップ通知用
from tkinter import filedialog # ファイル選択ダイアログ用

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Translator GUI v1.1")
        self.geometry("500x550")

        # 1. 入力ファイル選択
        self.file_label = ctk.CTkLabel(self, text="【1】翻訳するファイルを選択", font=("HGｺﾞｼｯｸE", 16))
        self.file_label.pack(pady=(20, 5))

        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(fill="x", padx=20)

        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="ここにファイルパスが表示されます")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.file_button = ctk.CTkButton(self.file_frame, text="ファイル選択", width=100, command=self.select_file)
        self.file_button.pack(side="left")


        # 2. 実行モード選択
        self.mode_label = ctk.CTkLabel(self, text="【2】実行モード選択", font=("HGｺﾞｼｯｸE", 16))
        self.mode_label.pack(pady=(20, 5))
        
        self.mode_option = ctk.CTkOptionMenu(self, values=["all", "translate", "layout", "check"])
        self.mode_option.pack(pady=10)

        # 3. 翻訳対象の選択（チェックボックス）
        self.target_label = ctk.CTkLabel(self, text="【3】翻訳対象（翻訳モード時のみ）", font=("HGｺﾞｼｯｸE", 14))
        self.target_label.pack(pady=(20, 5))

        self.check_question = ctk.CTkCheckBox(self, text="問題文 (Question)")
        self.check_question.pack(pady=5)
        self.check_question.select() # デフォルトでチェック

        self.check_comment = ctk.CTkCheckBox(self, text="解説文 (Comment)")
        self.check_comment.pack(pady=5)

        # 4. リミット設定
        self.limit_label = ctk.CTkLabel(self, text="【4】行数制限 (空なら全件)", font=("HGｺﾞｼｯｸE", 14))
        self.limit_label.pack(pady=(20, 5))
        
        self.limit_entry = ctk.CTkEntry(self, placeholder_text="例: 16")
        self.limit_entry.pack(pady=5)

        # 5. 実行ボタン
        self.start_button = ctk.CTkButton(self, text="実行開始", 
                                         fg_color="green", hover_color="darkgreen",
                                         command=self.button_callback)
        self.start_button.pack(pady=30)

    def select_file(self):
        """ファイル選択ダイアログを開き、選択されたパスをエントリーに入力する"""
        filepath = filedialog.askopenfilename(
            title="翻訳するExcelファイルを選択",
            filetypes=[("Excelファイル", "*.xlsx")]
        )
        if filepath:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filepath)

    def button_callback(self):
        mode = self.mode_option.get()
        limit_str = self.limit_entry.get()
        limit = int(limit_str) if limit_str.isdigit() else None
        input_file = self.file_entry.get()
        
        # 翻訳対象リストの作成
        targets = []
        if self.check_question.get(): targets.append("question")
        if self.check_comment.get(): targets.append("comment")

        if not input_file and mode in ["all", "translate"]:
            messagebox.showerror("エラー", "翻訳モードを実行するには、入力ファイルを選択してください。")
            return

        if not targets and mode in ["all", "translate"]:
            messagebox.showerror("エラー", "翻訳対象を少なくとも1つ選択してください")
            return

        print(f"--- 実行: {mode} (Target: {targets}, Limit: {limit}) ---")
        # ボタンを無効化（連打防止）
        self.start_button.configure(state="disabled", text="実行中...")

        # 別スレッドで実行する関数
        def run_process():
            # 重いライブラリはここでインポート（GUI起動の高速化）
            import Tr_Main as tm
            from Similarity_Checker import SimilarityChecker

            try:
                if mode == "check":
                    # チェックモード専用の処理
                    # パスを Tr_Main から取得（一元管理）
                    paths = tm.get_paths()
                    target_file = paths["out_file"]
                    
                    # 列名のマッピング（エクセルの実際の見出し名と合わせる）
                    columns = {
                        '問題文': '問題文', 
                        'ปัญหา': 'ปัญหา', # ここは実際のエクセルの列名に書き換えてください
                        '解説': '解説', 
                        'คำอธิบาย': 'คำอธิบาย' # ここも同様
                    }
                    
                    checker = SimilarityChecker()
                    checker.check_file(target_file, columns)
                    self.after(0, lambda: messagebox.showinfo("完了", f"チェックが完了しました！\n{target_file.replace('.xlsx', '_checked.xlsx')}"))
                
                else:
                    # 既存の翻訳・レイアウト処理
                    tm.main(mode=mode, limit=limit, targets=targets, input_file_path=input_file)
                    self.after(0, lambda: messagebox.showinfo("完了", "処理が完了しました。"))

            except Exception as e:
                error_msg = traceback.format_exc()
                print(f"エラーが発生しました：\n{error_msg}")
                self.after(0, lambda: messagebox.showerror("エラー", f"実行中にエラーが発生しました：\n\n{str(e)}"))
            finally:
                # ボタン再有効化（メインスレッドから操作）
                self.after(0, lambda: self.start_button.configure(state="normal", text="実行開始"))

        # スレッド開始
        threading.Thread(target=run_process, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()