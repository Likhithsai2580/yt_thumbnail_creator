from llm.llama import LLM
import json
import logging
from assests_gen import generate_image as ag
from PIL import Image, ImageDraw, ImageFont

# Configuration
THUMBNAIL_PATH = 'static/thumbnail.png'
FONT_SIZE = 50
logging.basicConfig(level=logging.INFO)

import re

def filter_python(txt):
    print("Filtering Python code")
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    if matches:
        python_code = matches[0].strip()
        return python_code
    else:
        return txt

def filter_json(txt):
    print("Filtering JSON code")
    pattern = r"```json(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    if matches:
        json_code = matches[0].strip()
        return json_code
    else:
        return txt


messages = [
    {
        "role": "system",
        "content": """
        You are a professional thumbnail designer on YouTube. Generate a thumbnail idea 
        and write prompts for asset generation. 
        ***Do not directly generate a thumbnail with the asset generator.***

        Respond in this JSON format:

        ```json
        {
            "imgs_data": [
                {
                    "simple_name_of_asset": "background", 
                    "prompt": "A vibrant cityscape at sunset",
                    "width": 1920,
                    "height": 1080
                },
                {
                    "simple_name_of_asset": "main_subject",
                    "prompt": "A cheerful dog wearing headphones",
                    "width": 500,
                    "height": 500
                }
            ]
        }
        ```

        The assets should be in the order of usage (e.g., background first). 
        Do not respond with anything else.

        The topic will be sent by the user in the next message.
        """
    }
]

def generate_assets(topic, messages):
    """Generates assets based on the given topic using the LLM."""
    try:
        response = LLM(messages, topic, "user")
        if response is None:
            raise ValueError("LLM response is None")
        logging.info(f"LLM response: {response}")

        # Extract and filter JSON response
        json_response = filter_json(response)
        if not json_response:
            raise ValueError("Filtered JSON response is None")
        
        try:
            imgs_info = json.loads(json_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decoding failed: {e}")

        # Ensure imgs_info is a dictionary and contains 'imgs_data'
        if not isinstance(imgs_info, dict):
            raise ValueError("Parsed JSON is not a dictionary")

        imgs_data = imgs_info.get('imgs_data', [])
        if not isinstance(imgs_data, list):
            raise ValueError("'imgs_data' is not a list")

        # Generate assets
        for img in imgs_data:
            try:
                if not isinstance(img.get('simple_name_of_asset'), str):
                    raise ValueError("Expected string for 'simple_name_of_asset'")
                if not isinstance(img.get('prompt'), str):
                    raise ValueError("Expected string for 'prompt'")
                if not isinstance(img.get('width'), int):
                    raise ValueError("Expected integer for 'width'")
                if not isinstance(img.get('height'), int):
                    raise ValueError("Expected integer for 'height'")
                
                logging.info(f"Generating asset with name '{img['simple_name_of_asset']}' and prompt '{img['prompt']}'")
                print(f"running ag with parameters {img['simple_name_of_asset'], 
                img['prompt'], 
                img['width'],
                img['height'],
                }")
                ag(name=img['simple_name_of_asset'], 
                prompt=img['prompt'], 
                width=img['width'],
                height=img['height'])  # Add negative_prompt here

            except KeyError as e:
                logging.error(f"Missing key in image data: {e}")
            except Exception as e:
                logging.error(f"Error generating asset {img.get('simple_name_of_asset', 'unknown')}: {e}")
    except Exception as e:
        logging.error(f"Error generating assets: {e}")


def add_to_thumbnail(asset_name, location_x, location_y):
    """Adds an asset to the thumbnail at a specific location."""
    logging.info(f"Adding asset {asset_name} to thumbnail")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            asset_path = f'{asset_name}'
            with Image.open(asset_path) as asset:
                thumbnail.paste(asset, (location_x, location_y), asset)
                thumbnail.save(THUMBNAIL_PATH)
        logging.info(f"Added {asset_name} to the thumbnail at ({location_x}, {location_y})")
    except Exception as e:
        logging.error(f"Error adding to thumbnail: {e}")

def add_text_to_thumbnail(text, font_path, color, position='center'):
    """Adds text to the thumbnail."""
    logging.info(f"Adding text '{text}' to thumbnail")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            draw = ImageDraw.Draw(thumbnail)
            try:
                font = ImageFont.truetype(font_path, size=FONT_SIZE)
            except IOError:
                logging.warning(f"Font file '{font_path}' not found. Using default font.")
                font = ImageFont.load_default()
            text_width, text_height = draw.textsize(text, font=font)
            width, height = thumbnail.size
            if position == 'center':
                position = ((width - text_width) / 2, (height - text_height) / 2)
            draw.text(position, text, fill=color, font=font)
            thumbnail.save(THUMBNAIL_PATH)
    except Exception as e:
        logging.error(f"Error adding text to thumbnail: {e}")

def save_thumbnail(filename):
    """Saves the thumbnail with the given filename."""
    logging.info("Saving thumbnail")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            thumbnail.save(f'{filename}.png')
        logging.info(f"Thumbnail saved as {filename}.png")
    except Exception as e:
        logging.error(f"Error saving thumbnail: {e}")

def execute_llm_instructions(messages_prompt):
    """Executes LLM instructions and handles responses."""
    try:
        response = LLM(messages, messages_prompt, "system")
        logging.info(f"LLM response: {response}")
        if response is None:
            raise ValueError("LLM response is None")
        code = filter_python(response)
        if code is None:
            raise ValueError("Filtered Python code is None")
        
        logging.info(f"Code to execute: {code}")
        exec(code)  # Ensure this is safe and trusted
    except Exception as e:
        logging.error(f"Error executing LLM instructions: {e}")

if __name__ == "__main__":
    topic = input("Enter the topic: ")
    generate_assets(topic, messages)

    # Instructions for LLM to assemble the thumbnail
    assembly_messages = """
    Imagine the images you generated. Now, provide code to assemble the thumbnail.
    Use the following functions:

    - `add_to_thumbnail(asset_name, location_x, location_y)`
    - `add_text_to_thumbnail(text, font_path, color, position='center')`
    - `save_thumbnail(filename)`

    For example:

    ```python
    add_to_thumbnail('background', 0, 0)
    add_to_thumbnail('main_subject', 100, 100)
    add_text_to_thumbnail('My Cool Thumbnail', 'arial.ttf', 'white')
    save_thumbnail('final_thumbnail') 
    ```
    """
    execute_llm_instructions(assembly_messages)
