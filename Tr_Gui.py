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
        "file_label_translate": "【2】翻訳元ファイルを選択",
        "file_label_quiz": "【2】アプリ作成元ファイルを選択",
        "file_placeholder": "ここにファイルパスが表示されます",
        "file_btn": "ファイル選択",
        "mode_label": "【1】実行モード選択",
        "target_label": "【3】翻訳対象（翻訳モード時のみ）",
        "chk_question": "問題文 (Question)",
        "chk_comment": "解説文 (Comment)",
        "limit_label": "【4】行数制限 (空なら全件)",
        "limit_placeholder": "例: 16",
        "threshold_label": "【3】判定しきい値 (0.0 - 1.0)",
        "threshold_placeholder": "例: 0.75 (デフォルト)",
        "start_btn": "実行開始",
        "running": "実行中...",
        "msg_error_file": "実行するには、入力ファイルを選択してください。",
        "msg_error_target": "翻訳対象を少なくとも1つ選択してください",
        "msg_done": "処理が完了しました。",
        "msg_check_done": "チェックが完了しました！\n{}",
        "err_title": "エラー",
        "done_title": "完了"
    },
    "Thai": {
        "file_label_translate": "【2】เลือกไฟล์ต้นฉบับ (Select Source File)",
        "file_label_quiz": "【2】เลือกไฟล์สำหรับแอป (Select Quiz File)",
        "file_placeholder": "ที่อยู่ไฟล์จะแสดงที่นี่",
        "file_btn": "เลือกไฟล์",
        "mode_label": "【1】เลือกโหมด (Select Mode)",
        "target_label": "【3】เป้าหมายการแปล (Target)",
        "chk_question": "คำถาม (Question)",
        "chk_comment": "คำอธิบาย (Comment)",
        "limit_label": "【4】จำกัดจำนวนบรรทัด (Limit)",
        "limit_placeholder": "ตัวอย่าง: 16",
        "threshold_label": "【3】เกณฑ์ความเหมือน (Threshold 0.0 - 1.0)",
        "threshold_placeholder": "ตัวอย่าง: 0.75",
        "start_btn": "เริ่มทำงาน (Start)",
        "running": "กำลังทำงาน... (Running)",
        "msg_error_file": "กรุณาเลือกไฟล์นำเข้าเพื่อเริ่มทำงาน",
        "msg_error_target": "กรุณาเลือกเป้าหมายการแปลอย่างน้อย 1 รายการ",
        "msg_done": "การทำงานเสร็จสมบูรณ์",
        "msg_check_done": "การตรวจสอบเสร็จสมบูรณ์!\n{}",
        "err_title": "ข้อผิดพลาด (Error)",
        "done_title": "เสร็จสิ้น (Done)"
    },
    "English": {
        "file_label_translate": "[2] Select Source File",
        "file_label_quiz": "[2] Select Quiz Source File",
        "file_placeholder": "File path will appear here",
        "file_btn": "Select File",
        "mode_label": "[1] Select Mode",
        "target_label": "[3] Translation Target (Translate Mode Only)",
        "chk_question": "Question",
        "chk_comment": "Comment",
        "limit_label": "[4] Limit Rows (Empty for all)",
        "limit_placeholder": "Example: 16",
        "threshold_label": "[3] Similarity Threshold (0.0 - 1.0)",
        "threshold_placeholder": "Example: 0.75",
        "start_btn": "Start Execution",
        "running": "Running...",
        "msg_error_file": "Please select an input file to run.",
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
        self.geometry("500x650")
        self.current_lang = "English" # デフォルト言語

        # 0. 言語選択 (Top Right)
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        self.lang_option = ctk.CTkOptionMenu(self.lang_frame, values=["Japanese", "Thai", "English"], command=self.change_language, width=100)
        self.lang_option.pack(side="right")
        self.lang_option.set("English")
        
        self.lang_label = ctk.CTkLabel(self.lang_frame, text="Language:", font=("Arial", 12, "bold"))
        self.lang_label.pack(side="right", padx=10)

        # Main Content Frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # 1. 実行モード選択 (Left Aligned)
        self.mode_label = ctk.CTkLabel(self.content_frame, text="", font=("HGｺﾞｼｯｸE", 16, "bold"))
        self.mode_label.pack(anchor="w", pady=(10, 5))
        
        self.mode_option = ctk.CTkOptionMenu(self.content_frame, values=["all", "translate", "layout", "check", "create_quiz"], command=self.on_mode_change, width=200)
        self.mode_option.pack(anchor="w", pady=5)

        # 2. 入力ファイル選択
        self.file_label = ctk.CTkLabel(self.content_frame, text="", font=("HGｺﾞｼｯｸE", 16, "bold"))
        # Packed in on_mode_change

        self.file_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        # Packed in on_mode_change

        self.file_entry = ctk.CTkEntry(self.file_frame, placeholder_text="")
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.file_button = ctk.CTkButton(self.file_frame, text="", width=100, command=self.select_file)
        self.file_button.pack(side="right")

        # 3. 翻訳対象
        self.target_label = ctk.CTkLabel(self.content_frame, text="", font=("HGｺﾞｼｯｸE", 14, "bold"))
        
        self.check_question = ctk.CTkCheckBox(self.content_frame, text="")
        self.check_question.select() # デフォルトでチェック

        self.check_comment = ctk.CTkCheckBox(self.content_frame, text="")

        # 4. Limit
        self.limit_label = ctk.CTkLabel(self.content_frame, text="", font=("HGｺﾞｼｯｸE", 14, "bold"))
        
        self.limit_entry = ctk.CTkEntry(self.content_frame, placeholder_text="", width=200)

        # 4.5 Threshold
        self.threshold_label = ctk.CTkLabel(self.content_frame, text="", font=("HGｺﾞｼｯｸE", 14, "bold"))
        
        # 0.60 から 0.95 まで 0.05 刻みのリストを作成
        threshold_values = [f"{x:.2f}" for x in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]]
        self.threshold_option = ctk.CTkOptionMenu(self.content_frame, values=threshold_values, width=200)
        self.threshold_option.set("0.75") # デフォルト値

        # 5. 実行ボタン
        self.start_button = ctk.CTkButton(self.content_frame, text="", 
                                         fg_color="green", hover_color="darkgreen",
                                         height=50, font=("Arial", 16, "bold"),
                                         command=self.button_callback)

        # 初期表示の言語適用
        self.update_ui_text()
        
        # 初期表示のモードに合わせてUIを整理
        self.on_mode_change(self.mode_option.get())

    def change_language(self, choice):
        """言語選択が変更されたときに呼ばれる"""
        self.current_lang = choice
        self.update_ui_text()

    def update_ui_text(self):
        """現在の言語設定に基づいてUIのテキストを更新する"""
        t = TRANSLATIONS[self.current_lang]
        
        # モードに応じてファイルラベルを切り替え
        current_mode = self.mode_option.get()
        if current_mode == "create_quiz":
            self.file_label.configure(text=t["file_label_quiz"])
        else:
            self.file_label.configure(text=t["file_label_translate"])

        self.file_entry.configure(placeholder_text=t["file_placeholder"])
        self.file_button.configure(text=t["file_btn"])
        self.mode_label.configure(text=t["mode_label"])
        self.target_label.configure(text=t["target_label"])
        self.check_question.configure(text=t["chk_question"])
        self.check_comment.configure(text=t["chk_comment"])
        self.limit_label.configure(text=t["limit_label"])
        self.limit_entry.configure(placeholder_text=t["limit_placeholder"])
        self.threshold_label.configure(text=t["threshold_label"])
        
        # 実行中でなければボタンのテキストも更新
        if self.start_button.cget("state") != "disabled":
            self.start_button.configure(text=t["start_btn"])

    def on_mode_change(self, mode):
        """モード変更時に不要なUI要素を隠す"""
        # 一旦、可変部分とボタンを画面から外す（非表示にする）
        self.file_label.pack_forget()
        self.file_frame.pack_forget()
        self.target_label.pack_forget()
        self.check_question.pack_forget()
        self.check_comment.pack_forget()
        self.limit_label.pack_forget()
        self.limit_entry.pack_forget()
        self.threshold_label.pack_forget()
        self.threshold_option.pack_forget()
        self.start_button.pack_forget()

        # ファイル選択が必要なモードの場合のみ表示
        if mode in ["all", "translate", "create_quiz"]:
            self.file_label.pack(anchor="w", pady=(20, 5))
            self.file_frame.pack(fill="x", pady=5)

        # 翻訳が必要なモードの場合のみ、設定項目を再配置（表示）する
        if mode in ["all", "translate"]:
            self.target_label.pack(anchor="w", pady=(20, 5))
            self.check_question.pack(anchor="w", pady=5, padx=20)
            self.check_comment.pack(anchor="w", pady=5, padx=20)
            self.limit_label.pack(anchor="w", pady=(20, 5))
            self.limit_entry.pack(anchor="w", pady=5)
        
        # チェックモードの場合のみ、閾値設定を表示
        elif mode == "check":
            self.threshold_label.pack(anchor="w", pady=(20, 5))
            self.threshold_option.pack(anchor="w", pady=5)

        # ボタンは常に一番下に再配置
        self.start_button.pack(pady=40, fill="x", padx=40)
        
        # ラベルテキストの更新（モード切り替えでラベルが変わるため）
        self.update_ui_text()

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
        
        # 閾値の取得（チェックモード用）
        threshold_str = self.threshold_option.get()
        try:
            threshold_val = float(threshold_str) if threshold_str else 0.75
        except ValueError:
            threshold_val = 0.75 # エラー時はデフォルト
        
        # 現在の言語の辞書を取得
        t = TRANSLATIONS[self.current_lang]
        
        # 翻訳対象リストの作成
        targets = []
        if self.check_question.get(): targets.append("question")
        if self.check_comment.get(): targets.append("comment")

        if not input_file and mode in ["all", "translate", "create_quiz"]:
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

            try:
                if mode == "check":
                    # チェックモード専用の処理
                    out_path = tm.main(mode="check", input_file_path=None, threshold=threshold_val)
                    self.after(0, lambda: messagebox.showinfo(t["done_title"], t["msg_check_done"].format(out_path)))
                
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