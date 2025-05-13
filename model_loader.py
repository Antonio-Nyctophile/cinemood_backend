from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import pickle

tokenizer = DistilBertTokenizerFast.from_pretrained("model/")
model = DistilBertForSequenceClassification.from_pretrained("model/")
model.eval()

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        pred_class = torch.argmax(logits, dim=1).item()
        return label_encoder.inverse_transform([pred_class])[0]
