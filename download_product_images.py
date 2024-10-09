import os
import re
import json
import requests

# Define the download folder
download_folder = 'products_images'

# Create the download folder if it doesn't exist
os.makedirs(download_folder, exist_ok=True)

# Directory containing JSON files
json_data_folder = './bestbuy_json_data'

# Headers with User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

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

    # Iterate through each product in the JSON
    for product in data:
        product_name = format_product_name(product.get('name', 'Unknown_Product'))
        images = product.get('images', [])
        
        print('----------------')
        if images:
            image_url = images[0]
            
            # Download
            try:
                response = requests.get(image_url, headers=headers)
                print(f"Download status: {response.status_code}")
                if response.status_code == 200:
                    image_file_name = f"{product_name}_image.jpg"
                    image_path = os.path.join(download_folder, image_file_name)
                    with open(image_path, 'wb') as img_file:
                        img_file.write(response.content)
                    print(f"Downloaded image for {product_name} in category {category_name}")
                    
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
