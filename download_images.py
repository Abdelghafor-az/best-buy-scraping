import cloudinary.api
import cloudinary.uploader

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Folder to save the downloaded images
download_folder = 'product_images'

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

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

# check_cloudinary_connection()
# exit(0)

# Path to save the image URL mapping JSON
# mapping_file_path = 'image_url_mapping.json'

# Initialize the mapping dictionary
# url_mapping = {}

# Load the existing mapping if it exists, or create a new one
# if os.path.exists(mapping_file_path):
#     with open(mapping_file_path, 'r', encoding='utf-8') as mapping_file:
#         url_mapping = json.load(mapping_file)

# Create the download folder if it doesn't exist
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Load the JSON file
json_file_path = './json_data/printers.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Headers with User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Iterate through each product in the JSON
for product in data:
    # Get the product name and first image URL
    product_name = product.get('name', 'Unknown_Product').replace(' ', '_').replace('/', '_')
    images = product.get('images', [])
    
    if images:
        # Get the first image
        image_url = images[0]
        
        # Generate a local file path to save the image
        image_file_name = f"{product_name}_image.jpg"
        image_file_path = os.path.join(download_folder, image_file_name)
        
        # Download the image
        try:
            response = requests.get(image_url, headers=headers)
            if response.status_code == 200:
                with open(image_file_path, 'wb') as img_file:
                    img_file.write(response.content)
                print(f"Downloaded image for {product_name}: {image_file_path}")

                # Upload the image to Cloudinary
                # cloudinary_response = cloudinary.uploader.upload(image_file_path)
                # cloudinary_url = cloudinary_response.get('secure_url')
                # print(f"Uploaded to Cloudinary: {cloudinary_url}")

                # Add to the mapping (old URL -> new Cloudinary URL)
                # url_mapping[image_url] = cloudinary_url
            
            else:
                print(f"Failed to download image for {product_name}: {image_url}")
        except Exception as e:
            print(f"Error downloading image for {product_name}: {str(e)}")
    else:
        print(f"No images found for {product_name}")

# Save the updated URL mapping to the JSON file
# with open(mapping_file_path, 'w', encoding='utf-8') as mapping_file:
#     json.dump(url_mapping, mapping_file, indent=4)
#     print(f"Image URL mapping saved to {mapping_file_path}")