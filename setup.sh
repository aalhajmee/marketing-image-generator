#!/bin/bash

# Ensure script is run as root
if [ "$EUID" -ne 0 ]
then echo "Please run as root"
  exit
fi

# Update and install dependencies
apt-get update
apt-get upgrade -y
apt-get install -y python3 python3-pip python3-venv git

# Create a project directory and navigate into it
PROJECT_DIR="/marketing-image-generator"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone the repository
git clone https://github.com/aalhajmee/marketing-image-generator.git .
 
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r assets/lib/requirements.txt

# Set up environment variables
cat <<EOL > .env
UNSPLASH_ACCESS_KEY="YOUR_UNSPLASH_ACCESS_KEY"
PSD_FILE_PATH=assets/template/design_render.psd
OUTPUT_DIR=output
BASE_URL=https://your-app-domain.com
PORT=8000
TITLE_FONT_PATH=assets/fonts/Inter-Bold.ttf
SUBTITLE_FONT_PATH=assets/fonts/Inter-Regular.ttf
CATEGORY_FONT_PATH=assets/fonts/Inter-Medium.ttf
EOL

echo "Please update the .env file with the correct values."

# Set up Gunicorn service
cat <<EOL > /etc/systemd/system/marketing-image-generator.service
[Unit]
Description=Gunicorn instance to serve marketing-image-generator
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd to apply changes
systemctl daemon-reload

# Enable and start the Gunicorn service
systemctl enable marketing-image-generator.service
systemctl start marketing-image-generator.service

# Set up NGINX (if not already configured)
if ! [ -x "$(command -v nginx)" ]; then
  apt-get install -y nginx
fi

# Configure NGINX
cat <<EOL > /etc/nginx/sites-available/marketing-image-generator
server {
    listen 80;
    server_name your-app-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $PROJECT_DIR/assets/src;
    }

    location /output {
        alias $PROJECT_DIR/output;
    }
}
EOL

# Enable the NGINX site configuration
ln -s /etc/nginx/sites-available/marketing-image-generator /etc/nginx/sites-enabled/

# Test NGINX configuration and reload
nginx -t && systemctl reload nginx

echo "Setup complete. Please ensure the .env file is correctly configured."
