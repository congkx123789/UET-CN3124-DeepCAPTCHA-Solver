import torch
from torch.utils.data import DataLoader
import string
import os
import sys

# Thêm đường dẫn để import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from model import CRNN
    from dataset import CaptchaDataset, collate_fn
except ImportError:
    from ai_model.model import CRNN
    from ai_model.dataset import CaptchaDataset, collate_fn

# Config
CHARACTERS = string.ascii_uppercase + string.digits
BATCH_SIZE = 64
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VAL_DIR = os.path.join(os.path.dirname(__file__), "../dataset/val")
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights/best_model.pth")

idx_to_char = {idx + 1: char for idx, char in enumerate(CHARACTERS)}

def decode_predictions(preds):
    # preds: [batch, seq_len]
    decoded_texts = []
    for p_seq in preds:
        text = ""
        last_char = 0
        for p in p_seq:
            p = p.item()
            if p != 0 and p != last_char:
                text += idx_to_char.get(p, "")
            last_char = p
        decoded_texts.append(text)
    return decoded_texts

def evaluate(model=None, val_loader=None):
    if val_loader is None:
        if not os.path.exists(VAL_DIR):
            print(f"Validation directory not found: {VAL_DIR}")
            return 0
            
        val_ds = CaptchaDataset(VAL_DIR, CHARACTERS)
        if len(val_ds) == 0:
            print("No validation data found!")
            return 0
            
        val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)
    
    if model is None:
        model = CRNN(num_chars=len(CHARACTERS) + 1).to(DEVICE)
        if os.path.exists(WEIGHTS_PATH):
            model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=DEVICE))
            print(f"Loaded weights from {WEIGHTS_PATH}")
        else:
            print("Model weights not found. Evaluating with random weights.")
            
    model.eval()
    
    correct = 0
    total = 0
    
    print("Evaluating validation samples...")
    
    with torch.no_grad():
        for images, labels, target_lengths in val_loader:
            images = images.to(DEVICE)
            outputs = model(images) # [seq_len, batch, num_chars]
            
            # Giải mã CTC
            _, preds = torch.max(outputs, dim=2)
            preds = preds.transpose(1, 0).contiguous() # [batch, seq_len]
            
            decoded_preds = decode_predictions(preds)
            
            # Trích xuất nhãn thực tế
            start_idx = 0
            for i, target_len in enumerate(target_lengths):
                end_idx = start_idx + target_len
                label_seq = labels[start_idx:end_idx].tolist()
                
                true_text = "".join([idx_to_char[idx] for idx in label_seq])
                pred_text = decoded_preds[i]
                
                if true_text == pred_text:
                    correct += 1
                
                total += 1
                start_idx = end_idx
                
    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"Validation Accuracy: {correct}/{total} ({accuracy:.2f}%)")
    return accuracy

if __name__ == "__main__":
    evaluate()
