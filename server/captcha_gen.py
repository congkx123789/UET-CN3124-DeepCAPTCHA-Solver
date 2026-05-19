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
        
    def _get_random_text(self):
        # Variable length from 4 to 7
        length = random.randint(4, 7)
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
        for _ in range(random.randint(10, 20)):
            draw.line(
                [(random.randint(0, self.width), random.randint(0, self.height)),
                 (random.randint(0, self.width), random.randint(0, self.height))],
                fill=self._get_random_color(80, 255), width=random.randint(1, 4)
            )
            
        # Add some random circles/ellipses
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(5, 25)
            draw.ellipse([x-r, y-r, x+r, y+r], outline=self._get_random_color(100, 255), width=random.randint(1, 3))
            
        # Draw text
        total_chars = len(text)
        # Dynamic start position and spacing to create overlap
        char_spacing = (self.width - 40) / total_chars
        
        for i, char in enumerate(text):
            # Vary font size slightly
            font_size = random.randint(32, 42)
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except:
                font = ImageFont.load_default()
                
            char_image = Image.new('RGBA', (45, 55), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((5, 0), char, font=font, fill=self._get_random_color(0, 50))
            
            # Rotate character (extreme range)
            char_image = char_image.rotate(random.randint(-50, 50), expand=1)
            
            # Paste character onto main image with significant overlap potential
            x_pos = int(10 + i * char_spacing + random.randint(-5, 5))
            y_pos = random.randint(0, 15)
            image.paste(char_image, (x_pos, y_pos), char_image)

        # Add salt and pepper noise (increased density)
        pixels = image.load()
        for _ in range(int(self.width * self.height * 0.15)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            pixels[x, y] = self._get_random_color(0, 255)

        # Apply a slight blur
        image = image.filter(ImageFilter.SMOOTH_MORE)
        
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
