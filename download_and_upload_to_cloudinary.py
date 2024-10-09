import cloudinary.api
import cloudinary.uploader

import os
import re
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Directory containing JSON files
json_data_folder = './bestbuy_json_data'

# Path to save the image URL mapping JSON
mapping_file_path = 'image_url_mapping.json'

# Initialize the mapping dictionary (organized by category)
url_mapping = {}

# Load the existing mapping if it exists, or create a new one
if os.path.exists(mapping_file_path):
    with open(mapping_file_path, 'r', encoding='utf-8') as mapping_file:
        url_mapping = json.load(mapping_file)

# Headers with User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to check Cloudinary connection
def check_cloudinary_connection():
    try:
        # Fetch the first resource to check the connection
        result = cloudinary.api.resources(max_results=1)
        if result:
            print("Cloudinary connection successful!")
        else:
            print("Cloudinary connection failed!")
    except Exception as e:
        print(f"Error connecting to Cloudinary: {str(e)}")
        exit(1)

# Check Cloudinary connection
check_cloudinary_connection()

def format_product_name(product_name):
    # Replace problematic characters with underscores
    formatted_name = re.sub(r'[<>:"/\\|?*]', '_', product_name)  # Replace invalid characters
    formatted_name = re.sub(r'\s+', '_', formatted_name)  # Replace spaces with underscores
    formatted_name = formatted_name.strip('_')  # Remove leading/trailing underscores
    formatted_name = formatted_name[:50]  # Optional: Limit length to 100 characters
    return formatted_name

# Function to process each JSON file and update URL mapping
def process_json_file(category_name, file_path):
    # Load the JSON data
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Ensure that the category exists in the mapping
    if category_name not in url_mapping:
        url_mapping[category_name] = {}

    # Iterate through each product in the JSON
    for product in data:
        product_name = format_product_name(product.get('name', 'Unknown_Product'))
        images = product.get('images', [])
        
        print('----------------')
        if images:
            image_url = images[0]
            
            # Check if this image has already been uploaded
            if image_url in url_mapping[category_name]:
                print(f"Image already uploaded for {product_name} in category {category_name}, using Cloudinary URL: {url_mapping[category_name][image_url]}")
                continue
            
            # Download and upload image to Cloudinary
            try:
                response = requests.get(image_url, headers=headers)
                print(response.status_code)
                if response.status_code == 200:
                    image_file_name = f"{product_name}_image.jpg"
                    with open(image_file_name, 'wb') as img_file:
                        img_file.write(response.content)
                    print(f"Downloaded image for {product_name} in category {category_name}")
                    
                    # Upload to Cloudinary
                    cloudinary_response = cloudinary.uploader.upload(image_file_name)
                    cloudinary_url = cloudinary_response.get('secure_url')
                    print(f"Uploaded to Cloudinary: {cloudinary_url}")
                    
                    # Add to the category mapping (old URL -> new Cloudinary URL)
                    url_mapping[category_name][image_url] = cloudinary_url

                    # Remove the local file after upload
                    os.remove(image_file_name)
                else:
                    print(f"Failed to download image for {product_name} in category {category_name}: {image_url}")
            except Exception as e:
                print(f"Error downloading or uploading image for {product_name}: {str(e)}")
        else:
            print(f"No images found for {product_name} in category {category_name}")

# Iterate through each JSON file in the json_data folder
for file_name in os.listdir(json_data_folder):
    if file_name.endswith('.json'):
        category_name = file_name.split('.')[0]  # Use the file name (without extension) as the category
        file_path = os.path.join(json_data_folder, file_name)
        print(f"Processing category: {category_name}, file: {file_path}")
        process_json_file(category_name, file_path)
    # break

# Save the updated URL mapping to the JSON file
with open(mapping_file_path, 'w', encoding='utf-8') as mapping_file:
    json.dump(url_mapping, mapping_file, indent=4)
    print(f"Image URL mapping saved to {mapping_file_path}")
