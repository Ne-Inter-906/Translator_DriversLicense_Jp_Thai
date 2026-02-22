import customtkinter as ctk
import traceback # エラー詳細取得用
import threading # スレッド処理用
from tkinter import messagebox # ポップアップ通知用
from tkinter import filedialog # ファイル選択ダイアログ用

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 言語リソース辞書
TRANSLATIONS = {
    "Japanese": {
        "file_label": "【1】翻訳するファイルを選択",
        "file_placeholder": "ここにファイルパスが表示されます",
        "file_btn": "ファイル選択",
        "mode_label": "【2】実行モード選択",
        "target_label": "【3】翻訳対象（翻訳モード時のみ）",
        "chk_question": "問題文 (Question)",
        "chk_comment": "解説文 (Comment)",
        "limit_label": "【4】行数制限 (空なら全件)",
        "limit_placeholder": "例: 16",
        "start_btn": "実行開始",
        "running": "実行中...",
        "msg_error_file": "翻訳モードを実行するには、入力ファイルを選択してください。",
        "msg_error_target": "翻訳対象を少なくとも1つ選択してください",
        "msg_done": "処理が完了しました。",
        "msg_check_done": "チェックが完了しました！\n{}",
        "err_title": "エラー",
        "done_title": "完了"
    },
    "Thai": {
        "file_label": "【1】เลือกไฟล์ที่จะแปล (Select File)",
        "file_placeholder": "ที่อยู่ไฟล์จะแสดงที่นี่",
        "file_btn": "เลือกไฟล์",
        "mode_label": "【2】เลือกโหมด (Select Mode)",
        "target_label": "【3】เป้าหมายการแปล (Target)",
        "chk_question": "คำถาม (Question)",
        "chk_comment": "คำอธิบาย (Comment)",
        "limit_label": "【4】จำกัดจำนวนบรรทัด (Limit)",
        "limit_placeholder": "ตัวอย่าง: 16",
        "start_btn": "เริ่มทำงาน (Start)",
        "running": "กำลังทำงาน... (Running)",
        "msg_error_file": "กรุณาเลือกไฟล์นำเข้าเพื่อเริ่มโหมดการแปล",
        "msg_error_target": "กรุณาเลือกเป้าหมายการแปลอย่างน้อย 1 รายการ",
        "msg_done": "การทำงานเสร็จสมบูรณ์",
        "msg_check_done": "การตรวจสอบเสร็จสมบูรณ์!\n{}",
        "err_title": "ข้อผิดพลาด (Error)",
        "done_title": "เสร็จสิ้น (Done)"
    },
    "English": {
        "file_label": "[1] Select File to Translate",
        "file_placeholder": "File path will appear here",
        "file_btn": "Select File",
        "mode_label": "[2] Select Mode",
        "target_label": "[3] Translation Target (Translate Mode Only)",
        "chk_question": "Question",
        "chk_comment": "Comment",
        "limit_label": "[4] Limit Rows (Empty for all)",
        "limit_placeholder": "Example: 16",
        "start_btn": "Start Execution",
        "running": "Running...",
        "msg_error_file": "Please select an input file to run translation mode.",
        "msg_error_target": "Please select at least one translation target.",
        "msg_done": "Process completed.",
        "msg_check_done": "Check completed!\n{}",
        "err_title": "Error",
        "done_title": "Done"
    }
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Translator GUI v1.1")
        self.geometry("500x600")
        self.current_lang = "English" # デフォルト言語

        # 0. 言語選択 (UI display language)
        self.lang_label = ctk.CTkLabel(self, text="UI display language", font=("Arial", 12, "bold"))
        self.lang_label.pack(pady=(10, 0))
        self.lang_option = ctk.CTkOptionMenu(self, values=["Japanese", "Thai", "English"], command=self.change_language)
        self.lang_option.pack(pady=(0, 10))
        self.lang_option.set("English")

        # 1. 入力ファイル選択
        self.file_label = ctk.CTkLabel(self, text="", font=("HGｺﾞｼｯｸE", 16))
        self.file_label.pack(pady=(20, 5))

        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(fill="x", padx=20)

        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.file_button = ctk.CTkButton(self.file_frame, text="", width=100, command=self.select_file)
        self.file_button.pack(side="left")


        # 2. 実行モード選択
        self.mode_label = ctk.CTkLabel(self, text="", font=("HGｺﾞｼｯｸE", 16))
        self.mode_label.pack(pady=(20, 5))
        
        self.mode_option = ctk.CTkOptionMenu(self, values=["all", "translate", "layout", "check"])
        self.mode_option.pack(pady=10)

        # 3. 翻訳対象の選択（チェックボックス）
        self.target_label = ctk.CTkLabel(self, text="", font=("HGｺﾞｼｯｸE", 14))
        self.target_label.pack(pady=(20, 5))

        self.check_question = ctk.CTkCheckBox(self, text="")
        self.check_question.pack(pady=5)
        self.check_question.select() # デフォルトでチェック

        self.check_comment = ctk.CTkCheckBox(self, text="")
        self.check_comment.pack(pady=5)

        # 4. リミット設定
        self.limit_label = ctk.CTkLabel(self, text="", font=("HGｺﾞｼｯｸE", 14))
        self.limit_label.pack(pady=(20, 5))
        
        self.limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.limit_entry.pack(pady=5)

        # 5. 実行ボタン
        self.start_button = ctk.CTkButton(self, text="", 
                                         fg_color="green", hover_color="darkgreen",
                                         command=self.button_callback)
        self.start_button.pack(pady=30)

        # 初期表示の言語適用
        self.update_ui_text()

    def change_language(self, choice):
        """言語選択が変更されたときに呼ばれる"""
        self.current_lang = choice
        self.update_ui_text()

    def update_ui_text(self):
        """現在の言語設定に基づいてUIのテキストを更新する"""
        t = TRANSLATIONS[self.current_lang]
        
        self.file_label.configure(text=t["file_label"])
        self.file_entry.configure(placeholder_text=t["file_placeholder"])
        self.file_button.configure(text=t["file_btn"])
        self.mode_label.configure(text=t["mode_label"])
        self.target_label.configure(text=t["target_label"])
        self.check_question.configure(text=t["chk_question"])
        self.check_comment.configure(text=t["chk_comment"])
        self.limit_label.configure(text=t["limit_label"])
        self.limit_entry.configure(placeholder_text=t["limit_placeholder"])
        
        # 実行中でなければボタンのテキストも更新
        if self.start_button.cget("state") != "disabled":
            self.start_button.configure(text=t["start_btn"])

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
        
        # 現在の言語の辞書を取得
        t = TRANSLATIONS[self.current_lang]
        
        # 翻訳対象リストの作成
        targets = []
        if self.check_question.get(): targets.append("question")
        if self.check_comment.get(): targets.append("comment")

        if not input_file and mode in ["all", "translate"]:
            messagebox.showerror(t["err_title"], t["msg_error_file"])
            return

        if not targets and mode in ["all", "translate"]:
            messagebox.showerror(t["err_title"], t["msg_error_target"])
            return

        print(f"--- 実行: {mode} (Target: {targets}, Limit: {limit}) ---")
        # ボタンを無効化（連打防止）
        self.start_button.configure(state="disabled", text=t["running"])

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
                    self.after(0, lambda: messagebox.showinfo(t["done_title"], t["msg_check_done"].format(target_file.replace('.xlsx', '_checked.xlsx'))))
                
                else:
                    # 既存の翻訳・レイアウト処理
                    tm.main(mode=mode, limit=limit, targets=targets, input_file_path=input_file)
                    self.after(0, lambda: messagebox.showinfo(t["done_title"], t["msg_done"]))

            except Exception as e:
                error_msg = traceback.format_exc()
                print(f"エラーが発生しました：\n{error_msg}")
                self.after(0, lambda: messagebox.showerror(t["err_title"], f"Error:\n\n{str(e)}"))
            finally:
                # ボタン再有効化（メインスレッドから操作）
                self.after(0, lambda: self.start_button.configure(state="normal", text=t["start_btn"]))

        # スレッド開始
        threading.Thread(target=run_process, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()