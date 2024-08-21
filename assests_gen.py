import os
import shutil
from gradio_client import Client

# Set environmental variable for asset directory if not defined already
asset_dir_path = os.environ.get('ASSET_DIR_PATH', 'assets')

def generate_image(prompt, name, negative_prompt="null", seed=0, randomize_seed=True, width=1024, height=1024, guidance_scale=5,
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
        new_image_filename = f"{name}.webp"
        existing_count = 1
        while os.path.exists(os.path.join(asset_dir_path, new_image_filename)):
            new_image_filename = f"{name}_{existing_count}.webp"
            existing_count += 1

        # Move and rename the image file to the assets directory
        shutil.move(image_filepath, os.path.join(asset_dir_path, new_image_filename))

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