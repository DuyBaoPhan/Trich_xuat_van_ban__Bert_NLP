from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

class QAModel:
    def __init__(self, model_path="model-distilbert-finetuned-squadv2"):
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_path)

    def get_answer(self, question, context):
        # Tokenize inputs
        inputs = self.tokenizer(question, context, return_tensors="pt")

        # Perform inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get the answer
        answer_start_index = outputs.start_logits.argmax()
        answer_end_index = outputs.end_logits.argmax()
        predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]

        # Decode the answer
        answer = self.tokenizer.decode(predict_answer_tokens)
        return answer
