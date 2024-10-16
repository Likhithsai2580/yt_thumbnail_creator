# YouTube Thumbnail Generator

An AI-powered YouTube thumbnail generator that leverages Stable Diffusion and Large Language Models (LLM) to create custom, eye-catching thumbnails based on a given topic.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Detailed Function Descriptions](#detailed-function-descriptions)
- [Customization](#customization)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Intelligent Thumbnail Ideation**: Utilizes LLM to generate creative thumbnail concepts and asset prompts.
- **High-Quality Asset Generation**: Employs Stable Diffusion 3 to create visually appealing assets.
- **Automated Thumbnail Assembly**: Combines generated assets into cohesive thumbnails.
- **Background Removal**: Supports automatic background removal from assets for cleaner integration.
- **Text Overlay**: Adds customizable text to thumbnails for increased engagement.
- **Image Optimization**: Ensures output images are optimized for YouTube's requirements.

## Requirements

- Python 3.7+
- gradio_client
- Pillow
- rembg
- colorama
- Custom LLM implementation (llm/llama.py)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Likhithsai2580/yt_thumbnail_creator.git
   cd yt_thumbnail_creator
   ```

2. Install the required packages:
   ```
   pip install gradio_client Pillow rembg colorama
   ```

3. Set up the custom LLM implementation:
   - Ensure you have the `llm/llama.py` file in your project directory.
   - Follow any additional setup instructions for your specific LLM implementation.

4. Configure environment variables:
   - Set `ASSET_DIR_PATH` to specify where generated assets should be stored.
   - (Optional) Set any API keys or credentials required for Stable Diffusion or your LLM.

## Usage

1. Run the script:
   ```
   python yt_thumb_gen.py --topic "Your Topic"
   ```
2. The generated thumbnail will be saved to the path specified in `THUMBNAIL_PATH`.

## Configuration

Modify the following variables in the script to customize the thumbnail generation:

- `THUMBNAIL_PATH`: Path where the final thumbnail will be saved.
- `FONT_SIZE`: Default font size for text on thumbnails.
- `ASSET_DIR_PATH`: Directory to store generated assets.
- `THUMBNAIL_SIZE`: Size of the generated thumbnail (default: 1280x720).

## Detailed Function Descriptions

### `generate_image(prompt, name, negative_prompt, seed, randomize_seed, width, height, guidance_scale, num_inference_steps, api_name)`
Generates an image using the most efficient way and saves it as a PNG file.

### `generate_asset(prompt, name, negative_prompt, seed, randomize_seed, width, height, guidance_scale, num_inference_steps)`
Generates an asset using the most efficient way and saves it as a PNG file.

### `extract_code(response)`
Extracts Python code from LLM responses for further processing.

### `generate_assets(topic)`
Generates all necessary assets for a thumbnail based on the given topic.

### `add_to_thumbnail(thumbnail, asset_path, x, y)`
Adds an asset to the thumbnail at the specified (x, y) coordinates.

### `add_text_to_thumbnail(thumbnail, text, position, font_size, color)`
Adds text to the thumbnail with customizable position, font size, and color.

### `save_thumbnail(thumbnail)`
Saves the final thumbnail to the specified path.

### `remove_bg_from_asset(asset_path)`
Removes the background from an asset using the rembg library.

## Customization

To generate thumbnails for different topics:

1. Open `yt_thumb_gen.py` in your preferred text editor.
2. Locate the `__main__` section at the bottom of the script.
3. Modify the `topic` variable with your desired thumbnail topic.
4. Save the file and run the script as described in the [Usage](#usage) section.

## Logging

The script uses colorized logging via the `colorama` library to provide clear feedback on the thumbnail generation process. Different colors are used to highlight various stages and potential issues:

- Green: Successful operations
- Yellow: Warnings or important information
- Red: Errors or critical issues
- Blue: Processing steps

## Troubleshooting

- **Asset Generation Fails**: Ensure you have proper API credentials for Stable Diffusion and that your internet connection is stable.
- **LLM Errors**: Check that your custom LLM implementation is correctly set up and that any required models are properly loaded.
- **File Permission Issues**: Verify that the script has write permissions for the `ASSET_DIR_PATH` and `THUMBNAIL_PATH` directories.
- **Missing Dependencies**: Run `pip install -r requirements.txt` to ensure all required packages are installed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Stable Diffusion](https://stability.ai/) for providing the image generation capabilities.
- The developers of [rembg](https://github.com/danielgatis/rembg) for the background removal functionality.
- All contributors who have helped shape and improve this project.

---

For any questions or support, please open an issue on the GitHub repository.
