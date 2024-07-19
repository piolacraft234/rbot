import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from loguru import logger

from src.rbot.constants import PathConstants


class ImageUtilities:
    @staticmethod
    @logger.catch
    def create_welcome_image(member_name: str, avatar_url: str) -> BytesIO:
        """
        Create a welcome image for a new member.
        :param member_name: Name of the member.
        :param avatar_url: URL of the member's avatar.
        :return: BytesIO object with the image.
        """
        # Load the background image
        background: Image.Image = Image.open(PathConstants.WELCOME_BACKGROUND_PATH).convert("RGBA")
        width, height = background.size

        # Download and resize the user's avatar
        response: requests.Response = requests.get(avatar_url)
        avatar: Image.Image = Image.open(BytesIO(response.content)).resize((850, 850))

        # Create a circular mask for the avatar
        mask: Image.Image = Image.new("L", avatar.size, 0)
        draw: ImageDraw.Draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar.size, fill=255)
        avatar.putalpha(mask)

        # Coordinates to center the avatar
        avatar_x = (width - avatar.width) // 2
        avatar_y = (height - avatar.height) // 2 - 100  # Adjustment for text

        # Paste the avatar onto the background image
        background.paste(avatar, (avatar_x, avatar_y), avatar)

        # Add the text
        draw = ImageDraw.Draw(background)
        font_large: ImageFont.FreeTypeFont = ImageFont.truetype("arial.ttf", 250)
        font_small: ImageFont.FreeTypeFont = ImageFont.truetype("arial.ttf", 200)

        text_welcome = "Welcome to my server"
        text_member = member_name

        # Coordinates to center the text
        text_welcome_bbox = draw.textbbox((0, 0), text_welcome, font=font_large)
        text_welcome_width, text_welcome_height = text_welcome_bbox[2] - text_welcome_bbox[0], text_welcome_bbox[3] - text_welcome_bbox[1]

        text_member_bbox = draw.textbbox((0, 0), text_member, font=font_small)
        text_member_width, text_member_height = text_member_bbox[2] - text_member_bbox[0], text_member_bbox[3] - text_member_bbox[1]

        text_welcome_x = (width - text_welcome_width) // 2
        text_welcome_y = avatar_y + avatar.height + 20  # Adjustment below the avatar

        text_member_x = (width - text_member_width) // 2
        text_member_y = text_welcome_y + text_welcome_height + 10  # Adjustment below the welcome text

        # Draw the text on the image
        draw.text((text_welcome_x, text_welcome_y), text_welcome, font=font_large, fill="white")
        draw.text((text_member_x, text_member_y), text_member, font=font_small, fill="white")

        # Save the image to a BytesIO object
        output: BytesIO = BytesIO()
        background.save(output, format="PNG")
        output.seek(0)

        return output