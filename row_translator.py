import re

class Row_Translator:
    def __init__(self, batch_translator):
        self.bt = batch_translator

    def _split_sentences(self, text):
        keywords = ["。", "が、", "ものの、", "けれど、"]
        pattern = "|".join([f"(?<={re.escape(k)})" for k in keywords])
        context_words = ["その", "この", "当該", "同"]

        raw_sentences = re.split(pattern, str(text))
        raw_sentences = [s.strip() for s in raw_sentences if s.strip() != ""]

        refined_sentences = []
        temp_sentence = ""
        for s in raw_sentences:
            starts_with_context = any(s.startswith(w) for w in context_words)
            if starts_with_context and temp_sentence != "":
                temp_sentence += s
            else:
                if temp_sentence != "":
                    refined_sentences.append(temp_sentence)
                temp_sentence = s
        if temp_sentence:
            refined_sentences.append(temp_sentence)
        return refined_sentences

    def translate_row(self, text):
        if not text.strip():
            return ""
        try:
            # 単一行処理。ループ防止(ngram_size)を入れつつ、少し慎重な設定
            result = self.bt.translate_batch([text], penalty=1.5, max_tokens=128)
            return result[0]
        except Exception as e:
            # 完全に失敗した場合、指定のタイ語を入れて行数を維持する
            print(f"\n[Row Error] 翻訳失敗: {text[:15]}... ({e})")
            return "การแปลล้มเหลว"