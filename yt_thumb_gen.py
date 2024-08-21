from gradio_client import Client
import json
import logging
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import re
from llm.llama import LLM

# Configuration
THUMBNAIL_PATH = 'static/thumbnail.png'
FONT_SIZE = 50
ASSET_DIR_PATH = os.environ.get('ASSET_DIR_PATH', 'assets')

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

logging.basicConfig(level=logging.INFO)

# Initialize the Gradio client
client = Client("stabilityai/stable-diffusion-3-medium")

# System messages for LLM
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

def generate_asset(prompt, name, negative_prompt=None, seed=0, randomize_seed=True, width=1024, height=1024, guidance_scale=5, num_inference_steps=28):
    """Generates an asset based on the provided parameters and saves it to the asset directory."""
    try:
        result = client.predict(
            prompt=prompt,
            negative_prompt=negative_prompt or "(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation",
            seed=seed,
            randomize_seed=randomize_seed,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            api_name="/infer"
        )

        image_filepath, seed_value = result
        os.makedirs(ASSET_DIR_PATH, exist_ok=True)

        new_image_filename = f"{name}.webp"
        existing_count = 1
        while os.path.exists(os.path.join(ASSET_DIR_PATH, new_image_filename)):
            new_image_filename = f"{name}_{existing_count}.webp"
            existing_count += 1

        shutil.move(image_filepath, os.path.join(ASSET_DIR_PATH, new_image_filename))
        logging.info(f"Asset '{name}' generated and saved to '{new_image_filename}'")
        return os.path.join(ASSET_DIR_PATH, new_image_filename), seed_value

    except Exception as e:
        logging.error(f"An error occurred during asset generation: {e}")
        return None

def extract_code(text, language):
    """Extracts code blocks of a specific language from text."""
    logging.info(f"Extracting {language} code")
    pattern = rf"```{language}(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0].strip() if matches else ""

def validate_json_structure(imgs_info):
    """Validates the structure of the parsed JSON."""
    if not isinstance(imgs_info, dict):
        raise ValueError("Parsed JSON is not a dictionary")
    
    imgs_data = imgs_info.get('imgs_data', [])
    if not isinstance(imgs_data, list):
        raise ValueError("'imgs_data' is not a list")

    for img in imgs_data:
        if not isinstance(img.get('simple_name_of_asset'), str):
            raise ValueError("Expected string for 'simple_name_of_asset'")
        if not isinstance(img.get('prompt'), str):
            raise ValueError("Expected string for 'prompt'")
        if not isinstance(img.get('width'), int):
            raise ValueError("Expected integer for 'width'")
        if not isinstance(img.get('height'), int):
            raise ValueError("Expected integer for 'height'")
    return imgs_data

def generate_assets(topic, messages):
    """Generates assets based on the given topic using the LLM."""
    try:
        response = LLM(messages, topic, "user")
        if response is None:
            raise ValueError("LLM response is None")

        json_response = extract_code(response, 'json')
        if not json_response:
            raise ValueError("Filtered JSON response is None")

        imgs_info = json.loads(json_response)
        imgs_data = validate_json_structure(imgs_info)

        for img in imgs_data:
            try:
                logging.info(f"Generating asset '{img['simple_name_of_asset']}' with prompt '{img['prompt']}'")
                generate_asset(
                    name=img['simple_name_of_asset'],
                    prompt=img['prompt'],
                    width=img['width'],
                    height=img['height']
                )
            except KeyError as e:
                logging.error(f"Missing key in image data: {e}")
            except Exception as e:
                logging.error(f"Error generating asset '{img.get('simple_name_of_asset', 'unknown')}': {e}")
    except Exception as e:
        logging.error(f"Error generating assets: {e}")

def add_to_thumbnail(asset_name, location_x, location_y):
    """Adds an asset to the thumbnail at a specific location."""
    logging.info(f"Adding asset '{asset_name}' to thumbnail")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            asset_path = os.path.join(ASSET_DIR_PATH, asset_name)
            with Image.open(asset_path) as asset:
                thumbnail.paste(asset, (location_x, location_y), asset)
                thumbnail.save(THUMBNAIL_PATH)
        logging.info(f"Added '{asset_name}' to the thumbnail at ({location_x}, {location_y})")
    except Exception as e:
        logging.error(f"Error adding asset to thumbnail: {e}")

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
        logging.info(f"Added text '{text}' to the thumbnail")
    except Exception as e:
        logging.error(f"Error adding text to thumbnail: {e}")

def save_thumbnail(filename):
    """Saves the thumbnail with the given filename."""
    logging.info(f"Saving thumbnail as '{filename}.png'")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            thumbnail.save(f'{filename}.png')
        logging.info(f"Thumbnail saved as '{filename}.png'")
    except Exception as e:
        logging.error(f"Error saving thumbnail: {e}")

def execute_llm_instructions(instructions):
    """Executes LLM instructions and handles responses."""
    try:
        response = LLM(messages, instructions, "system")
        if response is None:
            raise ValueError("LLM response is None")

        code = extract_code(response, 'python')
        if not code:
            raise ValueError("Filtered Python code is None")

        logging.info(f"Executing code: {code}")
        exec(code, globals())  # Ensure this is safe and trusted
    except Exception as e:
        logging.error(f"Error executing LLM instructions: {e}")

if __name__ == "__main__":
    topic = "JARVIS A VIRTUAL ARTIFICIAL INTELLEGENCE DEMO"
    if not topic:
        logging.error("No topic provided. Exiting.")
    else:
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
        add_text_to_thumbnail('Sample Text', 'arial.ttf', 'white')
        save_thumbnail('final_thumbnail') 
        ```
        """
        execute_llm_instructions(assembly_messages)
