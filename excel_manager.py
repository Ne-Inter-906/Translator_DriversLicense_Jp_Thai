import pandas as pd
import unicodedata

class Excel_Manager:
    def __init__(self, jp_csv, th_csv, batch_translator, row_translator):
        self.bt = batch_translator
        self.rt = row_translator
        jp_df = pd.read_csv(jp_csv)
        self.jp_dict = dict(zip(jp_df["before"], jp_df["after"]))
        th_df = pd.read_csv(th_csv, encoding="utf-8-sig")
        th_dict_df = th_df.fillna("")
        self.th_dict = dict(zip(th_dict_df["wrong"], th_dict_df["right"]))

    def _clean_ja(self, text):
        text = unicodedata.normalize("NFKC", str(text))
        for b, a in sorted(self.jp_dict.items(), key=lambda x: len(x[0]), reverse=True):
            text = text.replace(b, a)
        return text

    def _clean_th(self, text):
        text = unicodedata.normalize("NFKC", text)
        for w, r in sorted(self.th_dict.items(), key=lambda x: len(x[0]), reverse=True):
            text = text.replace(str(w), str(r))
        return text

    def execute(self, in_path, out_path, batch_size=16, mode="question", limit=None):

        # モードによって対象列を定義
        if mode == "question":
            print("問題文の翻訳を行います")
            src_idx, dst_idx = 1, 2  # B列, C列
        elif mode == "comment":
            print("解説文の翻訳を行います")
            src_idx, dst_idx = 5, 6  # F列, G列
        else:
            raise ValueError("mode は 'question' か 'comment' を指定してください")

        # 1. Excelの読み込み
        df = pd.read_excel(in_path)
        if limit: df = df.head(limit)
        
        # 指定したdst_idxの列が存在しない、または足りない場合に備えて拡張
        while df.shape[1] <= dst_idx:
            df[f"temp_{df.shape[1]}"] = "" 
        
        df.iloc[:, dst_idx] = df.iloc[:, dst_idx].fillna("").astype(object)

        # 2. 翻訳が必要な行のインデックスを抽出
        fail_msg = "การแปลล้มเหลว" # 翻訳に失敗しました、の意味
        
        targets = []
        for idx, row in df.iterrows():
            src_val = str(row.iloc[src_idx]).strip() if pd.notna(row.iloc[src_idx]) else ""
            dst_val = str(row.iloc[dst_idx]).strip() if pd.notna(row.iloc[dst_idx]) else ""
            
            # "nan" という文字列自体も除外する
            if src_val != "" and src_val.lower() != "nan" and (dst_val == "" or dst_val == fail_msg):
                targets.append(idx)
                
        if not targets:
            print(f"[{mode}] 翻訳が必要な未処理の行は見つかりませんでした。プロセスを終了します")
            return

        print(f"未処理/失敗行を {len(targets)} 件検出しました。翻訳を開始します。")

        # 3. 抽出したターゲットのみをバッチ処理
        for i in range(0, len(targets), batch_size):
            batch_indices = targets[i : i + batch_size]
            batch_texts = [self._clean_ja(df.iloc[idx, src_idx]) for idx in batch_indices]
            
            current_batch_results = []
            try:
                translated = self.bt.translate_batch(batch_texts)
                current_batch_results = [self._clean_th(r) for r in translated]
            except Exception as e:
                print(f"\n[Warning] バッチエラー。個別処理に切り替えます。")
                for text in batch_texts:
                    res = self.rt.translate_row(text)
                    current_batch_results.append(self._clean_th(res))

            # 4. 結果を DataFrame に書き戻し、その都度保存
            for idx, res in zip(batch_indices, current_batch_results):
                df.iloc[idx, dst_idx] = res
            
            df.to_excel(out_path, index=False)
            print(f"\r進捗: {i + len(batch_indices)} / {len(targets)} 件処理完了 (Excel更新済)", end="", flush=True)

        print(f"\nすべての未処理行が完了しました: {out_path}")