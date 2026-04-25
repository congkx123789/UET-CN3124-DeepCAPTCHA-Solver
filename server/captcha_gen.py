import random
import string
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class CaptchaGenerator:
    def __init__(self, font_path=None, width=160, height=60, characters=string.ascii_uppercase + string.digits):
        self.width = width
        self.height = height
        self.characters = characters
        self.font_path = font_path or "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        
    def _get_random_text(self, length=5):
        return ''.join(random.choices(self.characters, k=length))

    def _get_random_color(self, start=0, end=200):
        return (random.randint(start, end), random.randint(start, end), random.randint(start, end))

    def generate(self, text=None):
        if text is None:
            text = self._get_random_text()
        
        # Create a background color
        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Add some noise lines
        for _ in range(random.randint(2, 5)):
            draw.line(
                [(random.randint(0, self.width), random.randint(0, self.height)),
                 (random.randint(0, self.width), random.randint(0, self.height))],
                fill=self._get_random_color(150, 255), width=2
            )
            
        # Draw text
        try:
            font = ImageFont.truetype(self.font_path, 36)
        except:
            font = ImageFont.load_default()
            
        text_width = draw.textlength(text, font=font)
        start_x = (self.width - text_width) / 2
        
        for i, char in enumerate(text):
            char_image = Image.new('RGBA', (40, 50), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((5, 0), char, font=font, fill=self._get_random_color(0, 100))
            
            # Rotate character
            char_image = char_image.rotate(random.randint(-30, 30), expand=1)
            
            # Paste character onto main image
            image.paste(char_image, (int(start_x + i * 25), random.randint(5, 15)), char_image)

        # Add salt and pepper noise
        pixels = image.load()
        for _ in range(int(self.width * self.height * 0.05)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            pixels[x, y] = self._get_random_color(0, 255)

        # Apply a slight blur
        image = image.filter(ImageFilter.SMOOTH)
        
        return image, text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--output", type=str, default="test.png")
    args = parser.parse_args()
    
    gen = CaptchaGenerator()
    img, text = gen.generate()
    img.save(args.output)
    print(f"Generated captcha: {text}")
