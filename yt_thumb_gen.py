from gradio_client import Client
import json
import logging
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import re
from llm.llama import LLM, api_key
import traceback
import time
from colorama import Fore, Style, init
from rembg import remove
import io
import argparse

if api_key is None:
    os.environ["GROQ_API_KEY"] = input("please insert api key for groq: ")
    print("api key set, restart the module")
    exit()

# Initialize colorama for colored console output
init(autoreset=True)

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
    """Generates an asset based on the provided parameters and saves it as a PNG file."""
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

        new_image_filename = f"{name}.png"
        existing_count = 1
        while os.path.exists(os.path.join(ASSET_DIR_PATH, new_image_filename)):
            new_image_filename = f"{name}_{existing_count}.png"
            existing_count += 1

        # Convert to PNG and optimize
        with Image.open(image_filepath) as img:
            img = img.convert("RGBA")
            output_path = os.path.join(ASSET_DIR_PATH, new_image_filename)
            img.save(output_path, format="PNG", optimize=True, quality=85)

        os.remove(image_filepath)  # Remove the original file
        logging.info(f"{Fore.GREEN}Asset '{name}' generated and saved as PNG: '{new_image_filename}'{Style.RESET_ALL}")
        return output_path, seed_value

    except Exception as e:
        logging.error(f"{Fore.RED}An error occurred during asset generation: {e}{Style.RESET_ALL}")
        return None, None  # Return None for both output_path and seed_value

def extract_code(text, language):
    """Extracts code blocks of a specific language from text."""
    logging.info(f"{Fore.CYAN}Extracting {language} code{Style.RESET_ALL}")
    
    # First, try to find code within triple backticks
    pattern = rf"```{language}?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    else:
        # If no code block is found, check if the entire response looks like Python code
        lines = text.strip().split('\n')
        code_lines = [line for line in lines if line.strip() and not line.startswith('#')]
        
        if code_lines and all(line.strip().startswith(('add_to_thumbnail', 'add_text_to_thumbnail', 'save_thumbnail', 'remove_bg_from_asset')) or '=' in line for line in code_lines):
            return '\n'.join(lines)
    
    return ""

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

def execute_llm_instructions(instructions, max_retries=3, retry_delay=20):
    """Executes LLM instructions and handles responses with retry logic."""
    for attempt in range(max_retries):
        try:
            response = LLM(messages, instructions, "system")
            if response is None:
                raise ValueError("LLM response is None")

            code = extract_code(response, 'python')
            if not code:
                logging.warning(f"{Fore.YELLOW}No Python code found in LLM response (attempt {attempt + 1}/{max_retries}). Full response:\n{response}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    logging.info(f"{Fore.CYAN}Retrying in {retry_delay} seconds...{Style.RESET_ALL}")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise ValueError("Max retries reached. No Python code found in LLM responses.")

            logging.info(f"{Fore.GREEN}Executing code:\n{code}{Style.RESET_ALL}")
            exec(code, globals())  # Ensure this is safe and trusted
            return  # Success, exit the function
        except Exception as e:
            logging.error(f"{Fore.RED}Error executing LLM instructions (attempt {attempt + 1}/{max_retries}): {e}{Style.RESET_ALL}")
            if attempt < max_retries - 1:
                logging.info(f"{Fore.CYAN}Retrying in {retry_delay} seconds...{Style.RESET_ALL}")
                time.sleep(retry_delay)
            else:
                raise  # Re-raise the last exception if all retries failed

def generate_assets(topic, messages, image_delay=60):
    try:
        response = LLM(messages, topic, "user")
        if response is None:
            raise ValueError("LLM response is None")

        # Add error handling for JSON parsing
        try:
            imgs_info = json.loads(response)
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON from LLM response: {response}")
            return []

        imgs_data = validate_json_structure(imgs_info)

        generated_assets = []
        for img in imgs_data:
            try:
                simple_name = img.get('simple_name_of_asset')
                prompt = img.get('prompt')
                width = img.get('width', 1024)  # Use default value if not provided
                height = img.get('height', 1024)  # Use default value if not provided
                logging.info(f"Generating asset '{simple_name}' with prompt '{prompt}'")
                
                asset_path, seed = generate_asset(prompt, simple_name, width=width, height=height)
                
                if asset_path:
                    generated_assets.append({
                        'name': simple_name,
                        'path': asset_path,
                        'seed': seed
                    })
                else:
                    logging.warning(f"Failed to generate asset '{simple_name}'")
                
                logging.info(f"Waiting {image_delay} seconds before generating the next asset...")
                time.sleep(image_delay)
            except KeyError as e:
                logging.error(f"Missing key in image data: {e}")
            except Exception as e:
                logging.error(f"Error generating asset '{img.get('simple_name_of_asset', 'unknown')}': {e}")
        
        return generated_assets
    except Exception as e:
        logging.error(f"Error generating assets: {e}")
        return []

def add_to_thumbnail(asset_name, location_x, location_y):
    """Adds an asset to the thumbnail at a specific location."""
    logging.info(f"{Fore.CYAN}Adding asset '{asset_name}' to thumbnail{Style.RESET_ALL}")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            asset_path = os.path.join(ASSET_DIR_PATH, asset_name)
            with Image.open(asset_path) as asset:
                thumbnail.paste(asset, (location_x, location_y), asset)
                thumbnail.save(THUMBNAIL_PATH, format="PNG")
        logging.info(f"{Fore.GREEN}Added '{asset_name}' to the thumbnail at ({location_x}, {location_y}){Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Error adding asset to thumbnail: {e}{Style.RESET_ALL}")

def add_text_to_thumbnail(text, font_path, color, position='center'):
    """Adds text to the thumbnail."""
    logging.info(f"{Fore.CYAN}Adding text '{text}' to thumbnail{Style.RESET_ALL}")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            draw = ImageDraw.Draw(thumbnail)
            try:
                font = ImageFont.truetype(font_path, size=FONT_SIZE)
            except IOError:
                logging.warning(f"{Fore.YELLOW}Font file '{font_path}' not found. Using default font.{Style.RESET_ALL}")
                font = ImageFont.load_default()
            text_width, text_height = draw.textsize(text, font=font)
            width, height = thumbnail.size
            if position == 'center':
                position = ((width - text_width) / 2, (height - text_height) / 2)
            draw.text(position, text, fill=color, font=font)
            thumbnail.save(THUMBNAIL_PATH, format="PNG")
        logging.info(f"{Fore.GREEN}Added text '{text}' to the thumbnail{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Error adding text to thumbnail: {e}{Style.RESET_ALL}")

def save_thumbnail(filename):
    """Saves the thumbnail with the given filename."""
    logging.info(f"{Fore.CYAN}Saving thumbnail as '{filename}.png'{Style.RESET_ALL}")
    try:
        with Image.open(THUMBNAIL_PATH) as thumbnail:
            thumbnail.save(f'{filename}.png', format="PNG")
        logging.info(f"{Fore.GREEN}Thumbnail saved as '{filename}.png'{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}Error saving thumbnail: {e}{Style.RESET_ALL}")

def remove_bg_from_asset(asset_name):
    """Removes the background from an asset and optimizes the output."""
    logging.info(f"{Fore.CYAN}Removing background from asset '{asset_name}'{Style.RESET_ALL}")
    try:
        asset_path = os.path.join(ASSET_DIR_PATH, asset_name)
        if os.path.exists(asset_path):
            with Image.open(asset_path) as img:
                # Convert to RGB if the image is in RGBA mode
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Remove background
                output = remove(img)
                
                # Optimize the image
                output = output.convert("RGBA")
                
                # Create a new filename with .png extension
                base_name = os.path.splitext(asset_name)[0]
                output_filename = f"nobg_{base_name}.png"
                output_path = os.path.join(ASSET_DIR_PATH, output_filename)
                
                # Save the optimized PNG
                output.save(output_path, format="PNG", optimize=True, quality=85)
                
            logging.info(f"{Fore.GREEN}Removed background from '{asset_name}' and saved as '{output_filename}'{Style.RESET_ALL}")
            return output_filename
        else:
            logging.warning(f"{Fore.YELLOW}Asset '{asset_name}' not found in assets{Style.RESET_ALL}")
            return None
    except Exception as e:
        logging.error(f"{Fore.RED}Error removing background from asset: {e}{Style.RESET_ALL}")
        return None

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Generate YouTube thumbnail based on a topic.")
        parser.add_argument("topic", help="The topic for the thumbnail")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        args = parser.parse_args()

        # Set logging level based on debug flag
        if args.debug:
            logger.setLevel(logging.DEBUG)
            handler.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            handler.setLevel(logging.INFO)

        if not args.topic:
            logging.error(f"{Fore.RED}No topic provided. Exiting.{Style.RESET_ALL}")
        else:
            assets = generate_assets(args.topic, messages)
            if not assets:
                logging.error(f"{Fore.RED}No assets were generated. Exiting.{Style.RESET_ALL}")
                exit(1)

            # Instructions for LLM to assemble the thumbnail
            assembly_messages = """
            Imagine the images you generated. Now, provide code to assemble the thumbnail.
            Use the following functions:

            - `add_to_thumbnail(asset_name, location_x, location_y)`
            - `add_text_to_thumbnail(text, font_path, color, position='center')`
            - `save_thumbnail(filename)`
            - `remove_bg_from_asset(asset_name)`  # Use this to remove background from an asset. Returns the new filename with 'nobg_' prefix and '.png' extension.

            All assets are now in PNG format. Respond ONLY with a Python code block. Do not include triple backticks in your response.
            """
            execute_llm_instructions(assembly_messages)
    except Exception as e:
        logging.error(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
        logging.error(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")

# Modify the logger to include colors
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{Style.RESET_ALL}"

# Update the logger configuration
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)