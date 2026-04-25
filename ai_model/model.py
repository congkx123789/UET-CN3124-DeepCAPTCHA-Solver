import torch
import torch.nn as nn

class CRNN(nn.Module):
    def __init__(self, num_chars, hidden_size=256):
        super(CRNN, self).__init__()
        
        # CNN for feature extraction
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2), # 160x60 -> 80x30
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d(2, 2), # 80x30 -> 40x15
            
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d((2, 2), (2, 2)), # 40x16 -> 20x8
            
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(True),
            nn.MaxPool2d((2, 2), (2, 2)), # 20x8 -> 10x4
            
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.MaxPool2d((4, 1), (4, 1)), # 10x4 -> 10x1 (Height 4 -> 1)
        )
        
        # New last conv is not needed if height is already 1
        # But I'll use a 1x1 conv to keep the feature map size consistent
        self.conv_final = nn.Conv2d(512, 512, kernel_size=1)
        
        # RNN for sequence modeling
        self.rnn = nn.Sequential(
            nn.LSTM(512, hidden_size, bidirectional=True, num_layers=2, batch_first=False)
        )
        
        # Fully connected layer for character classification
        self.fc = nn.Linear(hidden_size * 2, num_chars)

    def forward(self, x):
        # x: [batch, 3, height, width]
        conv = self.cnn(x) # [batch, 512, h', w']
        conv = self.conv_final(conv)
        
        b, c, h, w = conv.size()
        assert h == 1, f"Custom CNN layers must result in height 1. Got {h}"
        
        conv = conv.squeeze(2) # [batch, 512, w']
        conv = conv.permute(2, 0, 1) # [w', batch, 512] (Sequence first for LSTM)
        
        output, _ = self.rnn(conv)
        
        seq_len, batch_size, _ = output.size()
        output = output.view(seq_len * batch_size, -1)
        output = self.fc(output)
        output = output.view(seq_len, batch_size, -1) # [seq_len, batch, num_chars]
        
        return output

if __name__ == "__main__":
    # Test model
    model = CRNN(num_chars=37) # 26 letters + 10 digits + 1 blank
    x = torch.randn(1, 3, 64, 160)
    out = model(x)
    print(f"Output shape: {out.shape}") # Expect [seq_len, 1, 37]
