import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class Batch_Translator:
    def __init__(self, model_name="facebook/nllb-200-3.3B", device="cuda"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, weights_only=False).to(device)
        self.thai_id = self.tokenizer.convert_tokens_to_ids("tha_Thai")

    def translate_batch(self, texts, penalty=1.2, max_tokens=100):
        self.tokenizer.src_lang = "jpn_Jpan"
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        
        with torch.no_grad():
            tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.thai_id,
                max_new_tokens=max_tokens,
                num_beams=1,
                # ループを物理的に遮断してフリーズを防ぐ（計算は軽い）
                no_repeat_ngram_size=3,
                repetition_penalty=penalty,
                do_sample=False
            )
        return self.tokenizer.batch_decode(tokens, skip_special_tokens=True)