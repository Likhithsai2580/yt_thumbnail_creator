import os
import shutil
from gradio_client import Client
from PIL import Image

# Set environmental variable for asset directory if not defined already
asset_dir_path = os.environ.get('ASSET_DIR_PATH', 'assets')

def generate_image(prompt, name, negative_prompt="(deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation", seed=0, randomize_seed=True, width=1024, height=1024, guidance_scale=5,
num_inference_steps=28, api_name="/infer"):
    try:
        # Initialize the Gradio client with the model's identifier
        client = Client("stabilityai/stable-diffusion-3-medium")

        # Make the prediction request with the provided parameters
        result = client.predict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            randomize_seed=randomize_seed,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            api_name=api_name
        )

        # Extract the image file path and the seed from the result
        image_filepath, seed_value = result

        # Ensure asset directory exists
        os.makedirs(asset_dir_path, exist_ok=True)

        # Create unique filename if it already exists
        new_image_filename = f"{name}.png"
        existing_count = 1
        while os.path.exists(os.path.join(asset_dir_path, new_image_filename)):
            new_image_filename = f"{name}_{existing_count}.png"
            existing_count += 1

        # Convert to PNG and optimize
        with Image.open(image_filepath) as img:
            img = img.convert("RGBA")
            output_path = os.path.join(asset_dir_path, new_image_filename)
            img.save(output_path, format="PNG", optimize=True, quality=85)

        os.remove(image_filepath)  # Remove the original file

        return os.path.join(asset_dir_path, new_image_filename), seed_value

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    new_image_path, seed_value = generate_image(
        prompt="humandroid robots",
        negative_prompt="null",
        name="my_generated_image",
        seed=0,
        randomize_seed=True,
        width=1024,
        height=1024,
        guidance_scale=5,
        num_inference_steps=28,
        api_name="/infer"
    )

    if new_image_path:
        print(f"Image saved to: {new_image_path}")
        print(f"Seed value: {seed_value}")
