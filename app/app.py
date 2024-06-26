import os
import io
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from psd_tools import PSDImage
import requests
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the environment variable for Flask
os.environ['FLASK_ENV'] = 'production'

# Unsplash API Configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

app = Flask(__name__, static_folder='assets/src', static_url_path='/')
CORS(app)

# Path to the PSD file
psd_file_path = os.getenv('PSD_FILE_PATH', 'assets/template/design_render.psd')

# Ensure the return directory exists
output_dir = os.getenv('OUTPUT_DIR', 'output')
os.makedirs(output_dir, exist_ok=True)

# Base URL for image serving
BASE_URL = os.getenv('BASE_URL', 'https://bam.alhajmee.com')

def extract_text_layers(psd):
    text_layers = []
    for layer in psd:
        if layer.is_group():
            text_layers.extend(extract_text_layers(layer))
        elif layer.kind == 'type':
            text_layers.append(layer)
    return text_layers

def extract_image_layers(psd):
    image_layers = []
    for layer in psd:
        if layer.is_group():
            image_layers.extend(extract_image_layers(layer))
        elif layer.kind == 'pixel':
            image_layers.append(layer)
    return image_layers

def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line.strip())
    return lines

def get_font_size(draw, text, font_path, max_width, max_size, min_size):
    font_size = max_size
    while font_size >= min_size:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return font
        font_size -= 1
    return ImageFont.truetype(font_path, min_size)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

def clean_keyword(keyword):
    return keyword.replace(' ', '+')

def search_unsplash_image(keyword):
    try:
        cleaned_keyword = clean_keyword(keyword)
        url = f"https://api.unsplash.com/search/photos?query={cleaned_keyword}&per_page=1"
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
        else:
            logger.info(f"No images found for keyword: {keyword}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching Unsplash: {e}")
    return None

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        title = data.get('title', 'Default Title')
        subtitle = data.get('subtitle', 'Default Subtitle')
        category = data.get('category', 'Default Category')
        background_url = data.get('background_url')
        keywords = data.get('keywords', [])

        logger.info(f"Received request: title={title}, subtitle={subtitle}, category={category}")

        if not background_url and keywords:
            keyword = random.choice(keywords)
            background_url = search_unsplash_image(keyword)
            if not background_url:
                return jsonify({"error": f"Failed to find an image for the given keyword: {keyword}"}), 400

        logger.info(f"Using background URL: {background_url}")

        try:
            psd = PSDImage.open(psd_file_path)
        except Exception as e:
            logger.error(f"Failed to load PSD file: {e}")
            return jsonify({"error": "Failed to load PSD file"}), 500
        
        try:
            response = requests.get(background_url)
            response.raise_for_status()
            background = Image.open(io.BytesIO(response.content))
            
            bg_w, bg_h = background.size
            aspect_ratio = bg_w / bg_h
            if aspect_ratio > 1:
                new_width = int(aspect_ratio * 1080)
                background = background.resize((new_width, 1080), Image.LANCZOS)
                left = (new_width - 1080) // 2
                background = background.crop((left, 0, left + 1080, 1080))
            else:
                new_height = int(1080 / aspect_ratio)
                background = background.resize((1080, new_height), Image.LANCZOS)
                top = (new_height - 1080) // 2
                background = background.crop((0, top, 1080, top + 1080))

            final_image = Image.new("RGBA", (1080, 1080))
            final_image.paste(background, (0, 0))
            draw = ImageDraw.Draw(final_image)
        except Exception as e:
            logger.error(f"Error processing background image: {e}")
            return jsonify({"error": "Error processing background image"}), 500

        title_font_path = os.getenv('TITLE_FONT_PATH', "assets/fonts/Dubai-Bold.ttf")
        subtitle_font_path = os.getenv('SUBTITLE_FONT_PATH', "assets/fonts/Dubai-Regular.ttf")
        category_font_path = os.getenv('CATEGORY_FONT_PATH', "assets/fonts/Dubai-Medium.ttf")

        try:
            title_font = ImageFont.truetype(title_font_path, 100)
            subtitle_font = ImageFont.truetype(subtitle_font_path, 50)
            category_font = ImageFont.truetype(category_font_path, 42)
        except IOError as e:
            logger.error(f"Font file not found: {e}")
            return jsonify({"error": "Font file not found"}), 500

        image_layers = extract_image_layers(psd)
        for idx, layer in enumerate(image_layers):
            image = layer.composite()
            left, top, right, bottom = layer.bbox
            final_image.paste(image, (left, top), image)

        text_layers = extract_text_layers(psd)
        logger.info("Identified text layers:")
        
        max_width = int(1080 * 0.65)
        max_width_sub = int(1080 * 0.8)

        for layer in text_layers:
            logger.info(f"Processing layer: {layer.name}, Position: {layer.bbox}")
            left, top, right, bottom = layer.bbox
            try:
                if 'title' in layer.name.lower() and 'subtitle' not in layer.name.lower():
                    title_font = get_font_size(draw, title, title_font_path, max_width, 80, 60)
                    bbox = draw.textbbox((0, 0), title, font=title_font)
                    text_width = bbox[2] - bbox[0]
                    position_x = (1080 - text_width) // 2
                    title_y = top * 1.18
                    position = (position_x, title_y)
                    logger.info(f"Placing title: {title} at {position}")
                    draw.text(position, title, font=title_font, fill="white")
                elif 'subtitle' in layer.name.lower():
                    subtitle_font = get_font_size(draw, subtitle, subtitle_font_path, max_width_sub, 40, 32)
                    wrapped_subtitle = wrap_text(draw, subtitle, subtitle_font, max_width_sub)
                    subtitle_y = top * 1.03
                    for line in wrapped_subtitle:
                        bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                        text_width = bbox[2] - bbox[0]
                        position_x = (1080 - text_width) // 2
                        position = (position_x, subtitle_y)
                        logger.info(f"Placing subtitle line: {line} at {position}")
                        draw.text(position, line, font=subtitle_font, fill="white")
                        subtitle_y += bbox[3]
                elif 'category' in layer.name.lower():
                    category_font = get_font_size(draw, category, category_font_path, max_width, 30, 20)
                    bbox = draw.textbbox((0, 0), category, font=category_font)
                    text_width = bbox[2] - bbox[0]
                    center_x = (760 + 960) // 2
                    center_y = 20
                    position_x = center_x - text_width // 2
                    category_position = (position_x, center_y)
                    logger.info(f"Placing category: {category} at {category_position}")
                    draw.text(category_position, category, font=category_font, fill=(0, 43, 73))
            except Exception as e:
                logger.error(f"Error processing layer {layer.name}: {e}")

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        file_path = os.path.join(output_dir, filename)

        final_image.save(file_path, format='PNG')

        image_url = f"{BASE_URL}/output/{filename}"

        return jsonify({"image_url": image_url}), 200

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return jsonify({"error": "An error occurred while generating the image"}), 500

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
