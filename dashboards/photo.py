import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import pillow_heif
pillow_heif.register_heif_opener()

def get_random_photo(api_url, api_key):
    try:
        headers = {"x-api-key": api_key}
        resp = requests.get(f"{api_url}/api/assets/random", headers=headers, timeout=10)
        resp.raise_for_status()
        print(f"Response status: {resp.status_code}")
        print(f"Response text: {resp.text}")
        assets = resp.json()
        assets = [a for a in assets if a.get("type") == "IMAGE" and not a.get("originalFileName", "").lower().endswith(".mov")]
        if not assets:
            raise ValueError("No image assets available")
        if not assets or not isinstance(assets, list):
            raise ValueError("Invalid asset list returned")

        photo_meta = random.choice(assets)

        if "id" not in photo_meta:
            raise ValueError("Invalid photo metadata")

        asset_id = photo_meta["id"]
        filename = photo_meta.get("originalFileName", "photo.jpg")
        timestamp = photo_meta.get("exifInfo", {}).get("dateTimeOriginal", "")
        location = f"{photo_meta.get("exifInfo", {}).get("city", "Unknown City")}, {photo_meta.get("exifInfo", {}).get("state", "N/A")}, {photo_meta.get("exifInfo", {}).get("country", "N/A")}"

        image_url = f"{api_url}/api/assets/{asset_id}/original"
        image_resp = requests.get(image_url, headers=headers, timeout=10)
        image_resp.raise_for_status()

        try:
            img = Image.open(BytesIO(image_resp.content))
        except Exception as heic_err:
            print(f"Primary image load failed, retrying with HEIC decode: {heic_err}")
            try:
                heif_file = pillow_heif.read_heif(BytesIO(image_resp.content))
                img = Image.frombytes(
                    heif_file.mode, 
                    heif_file.size, 
                    heif_file.data,
                    "raw"
                )
            except Exception as heic_decode_err:
                print(f"Failed to decode HEIC image: {heic_decode_err}")
                raise heic_decode_err
        return img, filename, timestamp, location

    except Exception as e:
        print(f"Failed to fetch photo: {e}")
        return None, "N/A", "N/A"

def render():
    IMMICH_API = os.getenv("IMMICH_URL", "http://localhost:2283/api")
    IMMICH_KEY = os.getenv("IMMICH_KEY", "your-api-key")

    img = Image.new('L', (600, 800), color=255)
    draw = ImageDraw.Draw(img)

    photo, name, timestamp, location = get_random_photo(IMMICH_API, IMMICH_KEY)

    font_path = 'fonts/CreatoDisplay-Regular.otf'
    font_small = ImageFont.truetype(font_path, 20)

    if photo:
        photo = photo.convert("L").resize((600, 700))
        img.paste(photo, (0, 0))
        draw.rectangle([(0, 700), (600, 800)], fill=255)
        draw.text((10, 710), f"{timestamp} • {name}", fill=0, font=font_small)
        draw.text((10, 735), f"{location}", fill=0, font=font_small)
        
    else:
        font_large = ImageFont.truetype(font_path, 32)
        draw.text((20, 300), "No photo available", fill=0, font=font_large)

    output = '/tmp/photo.png'
    img.save(output, optimize=True)
    return output