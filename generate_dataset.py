import os
import uuid
from server.captcha_gen import CaptchaGenerator
from tqdm import tqdm

def generate_bulk(count, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    gen = CaptchaGenerator()
    
    print(f"Generating {count} images in {output_dir}...")
    for i in tqdm(range(count)):
        img, text = gen.generate()
        # Save with format: TEXT_UUID.png to ensure uniqueness
        filename = f"{text}_{uuid.uuid4().hex[:8]}.png"
        img.save(os.path.join(output_dir, filename))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=int, default=15000)
    parser.add_argument("--val", type=int, default=5000)
    args = parser.parse_args()
    
    generate_bulk(args.train, "CTF_Auto_Solver/dataset/train")
    generate_bulk(args.val, "CTF_Auto_Solver/dataset/val")
