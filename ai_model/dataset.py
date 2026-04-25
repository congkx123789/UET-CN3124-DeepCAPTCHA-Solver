import os
import torch
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as T

class CaptchaDataset(Dataset):
    def __init__(self, root_dir, characters, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.characters = characters
        self.char_to_idx = {char: idx + 1 for idx, char in enumerate(characters)} # 0 is blank for CTC
        self.images = [f for f in os.listdir(root_dir) if f.endswith('.png')]

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_name = self.images[idx]
        # label is extracted from filename (e.g. ABCD1_uuid.png)
        label_text = img_name.split('_')[0]
        
        img_path = os.path.join(self.root_dir, img_name)
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        else:
            # Default transform
            image = T.Compose([
                T.Resize((64, 160)),
                T.ToTensor(),
                T.Normalize((0.5,), (0.5,))
            ])(image)
            
        label = [self.char_to_idx[char] for char in label_text]
        label = torch.LongTensor(label)
        
        target_lengths = torch.LongTensor([len(label)])
        
        return image, label, target_lengths

def collate_fn(batch):
    images, labels, target_lengths = zip(*batch)
    images = torch.stack(images, 0)
    
    # Pad labels for batching if necessary (though our labels are likely fixed length)
    # But CTC requires them to be concatenated or handled with lengths
    flat_labels = torch.cat(labels, 0)
    flat_target_lengths = torch.cat(target_lengths, 0)
    
    return images, flat_labels, flat_target_lengths
