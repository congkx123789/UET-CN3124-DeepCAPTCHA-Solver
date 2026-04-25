import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import string
import os
try:
    from .model import CRNN
    from .dataset import CaptchaDataset, collate_fn
except ImportError:
    from model import CRNN
    from dataset import CaptchaDataset, collate_fn

# Config
CHARACTERS = string.ascii_uppercase + string.digits
BATCH_SIZE = 64
LR = 1e-4
EPOCHS = 30
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train():
    # Paths
    train_dir = "dataset/train"
    val_dir = "dataset/val"
    weights_dir = "ai_model/weights"
    os.makedirs(weights_dir, exist_ok=True)
    
    # Dataset
    train_ds = CaptchaDataset(train_dir, CHARACTERS)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    
    # Model
    model = CRNN(num_chars=len(CHARACTERS) + 1).to(DEVICE)
    weights_path = os.path.join(weights_dir, "best_model.pth")
    if os.path.exists(weights_path):
        print(f"Resuming from {weights_path}...")
        model.load_state_dict(torch.load(weights_path, map_location=DEVICE))
        
    criterion = nn.CTCLoss(blank=0, reduction='mean', zero_infinity=True)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    
    print(f"Starting training on {DEVICE}...")
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        
        for i, (images, labels, target_lengths) in enumerate(train_loader):
            images = images.to(DEVICE)
            
            optimizer.zero_grad()
            
            # Forward pass
            # Output shape: [seq_len, batch, num_chars]
            outputs = model(images)
            
            input_lengths = torch.full(size=(outputs.size(1),), fill_value=outputs.size(0), dtype=torch.long).to(DEVICE)
            
            # Loss
            loss = criterion(outputs, labels, input_lengths, target_lengths)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            if i % 100 == 0:
                print(f"Epoch [{epoch+1}/{EPOCHS}], Step [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{EPOCHS}] completed. Average Loss: {avg_loss:.4f}")
        
        # Save checkpoint
        torch.save(model.state_dict(), os.path.join(weights_dir, f"checkpoint_epoch_{epoch+1}.pth"))
        torch.save(model.state_dict(), os.path.join(weights_dir, "best_model.pth"))

if __name__ == "__main__":
    train()
