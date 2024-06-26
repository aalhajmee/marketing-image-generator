# Marketing Image Generator Documentation

## Overview

The Marketing Image Generator is a Flask-based application that generates customized images using a PSD template and user-provided data. It leverages various libraries such as Pillow for image processing and psd-tools for PSD file manipulation. The application allows users to specify titles, subtitles, categories, and background images either through a URL or by selecting from Unsplash using keywords.

## Features

- Generate images dynamically based on user input.
- Support for custom titles, subtitles, and categories.
- Fetch background images from Unsplash based on user-provided keywords or use a custom URL.
- Output generated images in PNG format.
- REST API endpoint for image generation.

## Directory Structure

```bash
app/
├── app.py                      # Main application script
├── assets/                     # Directory for static assets
│   ├── fonts/                  # Directory for font files
│   │   ├── Inter-Bold.ttf
│   │   ├── Inter-Regular.ttf
│   │   └── Inter-Medium.ttf
│   ├── lib/                    # Directory for dependencies
│   │   └── requirements.txt    # Dependency list
│   ├── src/                    # Directory for frontend assets
│   │   ├── index.html          # HTML form for image generation
│   │   ├── styles.css          # CSS styles for the HTML form
│   │   └── script.js           # JavaScript for handling form submission
│   └── template/               # Directory for PSD template
│       └── design_render.psd   # PSD template file for image generation
├── documentation/              # Directory for documentation
│   └── App_Documentation.md    # This documentation file
├── output/                     # Directory where generated images are saved
├── restart.sh                  # Script to restart application services
├── setup.sh                    # Script to set up the application environment
└── .env                        # Environment variables file
```

## Setup Instructions

### Prerequisites

- Linux server with root access
- Python 3.8 or later installed
- pip package manager installed

### Installation Steps

1. **Clone the repository to your server**:
    ```bash
    git clone https://github.com/aalhajmee/marketing-image-generator.git
    cd marketing-image-generator
    ```

2. **Set up environment variables**:

    Create a `.env` file in the root directory (`app/`) and populate it with the following variables:
    ```makefile
    UNSPLASH_ACCESS_KEY="YOUR_UNSPLASH_ACCESS_KEY"
    PSD_FILE_PATH=assets/template/design_render.psd
    OUTPUT_DIR=output
    BASE_URL=https://your-app-domain.com
    PORT=8000
    TITLE_FONT_PATH=assets/fonts/Inter-Bold.ttf
    SUBTITLE_FONT_PATH=assets/fonts/Inter-Regular.ttf
    CATEGORY_FONT_PATH=assets/fonts/Inter-Medium.ttf
    ```

    Replace `YOUR_UNSPLASH_ACCESS_KEY` with your actual Unsplash API access key.

3. **Install dependencies**:

    Edit the script below to enter your domain name where needed. Then run the setup script to install Python dependencies:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    This script installs the necessary Python packages listed in `assets/lib/requirements.txt`.

4. **Start the application**:

    Use Gunicorn to run the Flask application in a production environment:
    ```bash
    gunicorn -w 4 -b 0.0.0.0:8000 app:app
    ```

5. **Set up NGINX (optional)**:

    If not already configured, set up NGINX to act as a reverse proxy to handle client requests.

6. **Enable and start services**:

    Use the `restart.sh` script to reload configuration and restart services:
    ```bash
    chmod +x restart.sh
    ./restart.sh
    ```

## API Documentation

### Endpoint

#### `POST /generate-image`

Generates an image based on the provided JSON input and returns the image URL.

##### Request

- **URL**: `/generate-image`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
  - `title`: The title text for the image.
  - `subtitle`: The subtitle text for the image.
  - `category`: The category text for the image.
  - `background_url`: The URL of a custom background image.
  - `keywords`: Keywords to search Unsplash for a background image.

Example Request:
```json
{
  "title": "Example Title",
  "subtitle": "Example Subtitle",
  "category": "Example Category",
  "background_url": "https://example.com/image.jpg",
  "keywords": ["keyword1", "keyword2"]
}
```

##### Response

- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Body**:
  - `image_url`: The URL of the generated image.

Example Response:
```json
{
  "image_url": "https://your-app-domain.com/output/image.png"
}
```

If there is an error, the response will include:

- **Status Code**: `400 Bad Request` or `500 Internal Server Error`
- **Content-Type**: `application/json`
- **Body**:
  - `error`: A message describing the error.

Example Error Response:
```json
{
  "error": "Error message"
}
```

## Example Usage

To generate an image, you can use `curl` to send a POST request to the `/generate-image` endpoint:
```bash
curl -X POST https://your-app-domain.com/generate-image   -H "Content-Type: application/json"   -d '{
        "title": "Example Title",
        "subtitle": "Example Subtitle",
        "category": "Example Category",
        "background_url": "https://example.com/image.jpg",
        "keywords": ["keyword1", "keyword2"]
      }'
```

This command sends a POST request to generate an image using the specified parameters.

## Troubleshooting

### Common Issues

- **Dependency Installation Errors**: Ensure all dependencies are correctly installed by running `setup.sh`.
- **Font File Not Found**: Verify that font files are placed in the correct directory (`assets/fonts/`).
- **Background Image Issues**: Ensure that URLs are valid and accessible.
- **Service Restart**: Use `restart.sh` to reload services after making configuration changes.

### Logs

Check application logs for detailed error messages and status updates.

## Restarting the Application

To restart the application services, run the restart script:
```bash
chmod +x restart.sh
./restart.sh
```

## Contact

For any issues or questions, please contact the API maintainer at [ammar@alhajmee.com](mailto:ammar@alhajmee.com).

## Environment Variables

Ensure the `.env` file is configured with the correct environment variables:

```dotenv
UNSPLASH_ACCESS_KEY="YOUR_UNSPLASH_ACCESS_KEY"
PSD_FILE_PATH=assets/template/design_render.psd
OUTPUT_DIR=output
BASE_URL=https://your-app-domain.com
PORT=8000
TITLE_FONT_PATH=assets/fonts/Inter-Bold.ttf
SUBTITLE_FONT_PATH=assets/fonts/Inter-Regular.ttf
CATEGORY_FONT_PATH=assets/fonts/Inter-Medium.ttf
```
