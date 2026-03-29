import os
import shutil
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# CTranslate2のインポート（インストールされていない場合の対策）
try:
    import ctranslate2
except ImportError:
    ctranslate2 = None

class Batch_Translator:
    def __init__(self, model_name="facebook/nllb-200-3.3B", device="cuda", use_ct2=False, ct2_dir="ct2_model", tgt_lang="tha_Thai"):
        self.use_ct2 = use_ct2
        self.ct2_dir = ct2_dir
        self.device = device
        self.model_name = model_name
        self.tgt_lang = tgt_lang
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if self.use_ct2:
            if ctranslate2 is None:
                raise ImportError("CTranslate2 library is not installed. Please run 'pip install ctranslate2'.")
            
            # モデル変換の確認と実行
            if not os.path.exists(self.ct2_dir):
                print(f"[Info] Converting model to CTranslate2 format: {self.ct2_dir} ...")
                # 変換には少し時間がかかります
                converter = ctranslate2.converters.TransformersConverter(
                    self.model_name,
                    copy_files=["tokenizer.json", "special_tokens_map.json", "tokenizer_config.json"]
                )
                converter.convert(self.ct2_dir, quantization="int8")
                print("[Info] Conversion completed.")

            # CTranslate2 Translatorのロード (CPU高速化のためdevice="cpu"推奨だが、GPUも可)
            # ここではGPUがないユーザー想定でCPU、量子化int8を使用
            self.ct2_translator = ctranslate2.Translator(self.ct2_dir, device="cpu", compute_type="int8")
        else:
            # 既存のPyTorchモード
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, weights_only=False).to(device)
            self.tgt_lang_id = self.tokenizer.convert_tokens_to_ids(self.tgt_lang)

    def translate_batch(self, texts, penalty=1.2, max_tokens=100, num_beams=1):
        if self.use_ct2:
            return self._translate_ct2(texts, penalty, max_tokens, num_beams)
        else:
            return self._translate_pytorch(texts, penalty, max_tokens, num_beams)

    def _translate_pytorch(self, texts, penalty, max_tokens, num_beams):
        self.tokenizer.src_lang = "jpn_Jpan"
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        with torch.no_grad():
            tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tgt_lang_id,
                max_new_tokens=max_tokens,
                num_beams=num_beams,
                # ループを物理的に遮断してフリーズを防ぐ（計算は軽い）
                no_repeat_ngram_size=3,
                repetition_penalty=penalty,
                do_sample=False
            )
        return self.tokenizer.batch_decode(tokens, skip_special_tokens=True)

    def _translate_ct2(self, texts, penalty, max_tokens, num_beams):
        # CTranslate2用の推論処理
        # ソース言語を明示的に設定（これがないと翻訳されずそのまま出力される場合があります）
        self.tokenizer.src_lang = "jpn_Jpan"

        # 1. Tokenize (Transformersのtokenizerを使用)
        source = [self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(t)) for t in texts]

        # 2. Translate
        # NLLB等はターゲット言語トークンをprefixとして渡す必要があります
        target_prefix = [[self.tgt_lang]] * len(source)
        
        results = self.ct2_translator.translate_batch(
            source,
            target_prefix=target_prefix,
            beam_size=num_beams,
            max_decoding_length=max_tokens,
            repetition_penalty=penalty,
            no_repeat_ngram_size=3,
            disable_unk=True
        )

        # 3. Detokenize
        # results[i].hypotheses[0] が最もスコアの高い翻訳結果（トークンリスト）
        decoded_texts = [
            self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(r.hypotheses[0]), skip_special_tokens=True)
            for r in results
        ]
        return decoded_texts