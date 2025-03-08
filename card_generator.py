import os, uuid, logging
from PIL import Image, ImageDraw
import requests
from io import BytesIO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BACKGROUND_URL = "https://raw.githubusercontent.com/The-fouda/welcomecard/refs/heads/main/Untitleds-2.png"

def download_image(url, default_size=(255, 255)):
    try:
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {e}")
        return Image.new("RGBA", default_size, (200, 200, 200, 255))

def generate_welcome_card(avatar_url):
    try:
        # Debugging: Check the received avatar URL
        print(f"Avatar URL received: {avatar_url}")
        if not avatar_url or not avatar_url.startswith("http"):
            logger.error(f"Invalid avatar URL: {avatar_url}")
            return None

        bg_width, bg_height = 847, 422
        background = download_image(BACKGROUND_URL, default_size=(bg_width, bg_height)).resize((bg_width, bg_height))

        avatar_size = 330
        avatar = download_image(avatar_url, default_size=(avatar_size, avatar_size)).resize((avatar_size, avatar_size))
        if avatar.mode != "RGBA":
            avatar = avatar.convert("RGBA")

        mask = Image.new("L", (avatar_size, avatar_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
        avatar.putalpha(mask)

        avatar_pos = (75, 45)
        background.paste(avatar, avatar_pos, avatar)

        temp_dir = os.path.join(os.getcwd(), "static")
        os.makedirs(temp_dir, exist_ok=True)
        output_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
        background.save(output_path, "PNG")

        logger.info(f"Card saved at: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error generating welcome card: {e}")
        return None
