import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import string
import os
try:
    from .model import CRNN
    from .dataset import CaptchaDataset, collate_fn
    from .evaluate import evaluate
except ImportError:
    from model import CRNN
    from dataset import CaptchaDataset, collate_fn
    from evaluate import evaluate

# Config
CHARACTERS = string.ascii_uppercase + string.digits
BATCH_SIZE = 64
LR = 1e-4
EPOCHS = 50
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import time

def log_event(msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/training.log", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def train():
    log_event("=== AI Training Pipeline Initialized ===")
    # Paths
    train_dir = "dataset/train"
    val_dir = "dataset/val"
    weights_dir = "ai_model/weights"
    os.makedirs(weights_dir, exist_ok=True)
    
    # Dataset
    train_ds = CaptchaDataset(train_dir, CHARACTERS, augment=True) # Enabled augmentation
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    
    val_ds = CaptchaDataset(val_dir, CHARACTERS, augment=False)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)
    
    # Model
    model = CRNN(num_chars=len(CHARACTERS) + 1).to(DEVICE)
    weights_path = os.path.join(weights_dir, "best_model.pth")
    
    best_acc = 0.0
    
    if os.path.exists(weights_path):
        print(f"Resuming from {weights_path}...")
        log_event(f"Resuming training from weights: {weights_path}")
        model.load_state_dict(torch.load(weights_path, map_location=DEVICE))
        print("Evaluating initial model...")
        best_acc = evaluate(model, val_loader)
        log_event(f"Initial model validation accuracy: {best_acc:.2f}%")
        
    criterion = nn.CTCLoss(blank=0, reduction='mean', zero_infinity=True)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    
    print(f"Starting training on {DEVICE}...")
    log_event(f"Starting training loop on device: {DEVICE} (Epochs: {EPOCHS}, Batch Size: {BATCH_SIZE}, LR: {LR})")
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        
        for i, (images, labels, target_lengths) in enumerate(train_loader):
            images = images.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(images)
            input_lengths = torch.full(size=(outputs.size(1),), fill_value=outputs.size(0), dtype=torch.long).to(DEVICE)
            loss = criterion(outputs, labels, input_lengths, target_lengths)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            if i % 100 == 0:
                print(f"Epoch [{epoch+1}/{EPOCHS}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{EPOCHS}] completed. Average Train Loss: {avg_loss:.4f}")
        
        val_acc = evaluate(model, val_loader)
        log_event(f"Epoch [{epoch+1}/{EPOCHS}] Summary - Train Loss: {avg_loss:.4f} | Validation Acc: {val_acc:.2f}%")
        
        torch.save(model.state_dict(), os.path.join(weights_dir, f"checkpoint_epoch_{epoch+1}.pth"))
        
        if val_acc > best_acc:
            msg = f"Validation accuracy improved from {best_acc:.2f}% to {val_acc:.2f}%. Saving best model..."
            print(msg)
            log_event(f"[IMPROVEMENT] {msg}")
            best_acc = val_acc
            torch.save(model.state_dict(), os.path.join(weights_dir, "best_model.pth"))
        else:
            print(f"Validation accuracy did not improve (Best: {best_acc:.2f}%).")

if __name__ == "__main__":
    train()
