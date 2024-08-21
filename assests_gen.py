import os
import shutil
from gradio_client import Client

def generate_image(prompt, name,negative_prompt="null", seed=0, randomize_seed=True, width=1024, height=1024, guidance_scale=5, num_inference_steps=28, api_name="/infer"):
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
    
    # Define the assets directory
    assets_dir = "assets"
    
    # Ensure the assets directory exists
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Define the new path for the image with a .webp extension
    new_image_filename = f"{name}.webp"
    new_image_filepath = os.path.join(assets_dir, new_image_filename)
    
    # Move and rename the image file to the assets directory
    shutil.move(image_filepath, new_image_filepath)
    
    # Return the path of the saved image and the seed value
    return new_image_filepath, seed_value

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
    print(f"Image saved to: {new_image_path}")
    print(f"Seed value: {seed_value}")
