from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def render():
    img = Image.new('L', (600, 800), color=255)  # 'L' = 8-bit grayscale
    draw = ImageDraw.Draw(img)

    font_path = 'fonts/CreatoDisplay-Regular.otf'
    font_path_header = 'fonts/CreatoDisplay-Bold.otf'
    font_large = ImageFont.truetype(font_path_header, 32)
    font_small = ImageFont.truetype(font_path, 18)

    draw.text((20, 40), "Weather Dashboard", fill=0, font=font_large)
    draw.text((20, 100), f"Temp: 75°F", fill=0, font=font_small)
    draw.text((20, 140), f"Clouds: Partly Cloudy", fill=0, font=font_small)
    draw.text((20, 780), f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fill=128, font=font_small)

    output = '/tmp/weather.png'
    img.save(output, optimize=True)
    return output