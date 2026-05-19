import torch
import torchvision.transforms as T
from PIL import Image
import io
import base64
import string

CHARACTERS = string.ascii_uppercase + string.digits
idx_to_char = {idx + 1: char for idx, char in enumerate(CHARACTERS)}

def decode_prediction(outputs):
    # outputs: [seq_len, batch, num_chars]
    # We take the argmax for the first element in the batch
    _, preds = torch.max(outputs, dim=2)
    preds = preds.transpose(1, 0).contiguous() # [batch, seq_len]
    
    decoded_text = ""
    last_char = 0 # 0 is blank
    
    # Simple CTC decoding (greedy)
    for p in preds[0]:
        p = p.item()
        if p != 0 and p != last_char:
            decoded_text += idx_to_char.get(p, "")
        last_char = p
        
    return decoded_text

def preprocess_image(image_b64):
    # Decode base64
    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    
    transform = T.Compose([
        T.Resize((64, 160)),
        T.ToTensor(),
        T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    return transform(image).unsqueeze(0) # Add batch dimension
