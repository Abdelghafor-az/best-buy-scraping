from dotenv import load_dotenv
import os
import json
import random
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize the Cohere client
# api_key = os.getenv('COHERE_API_KEY')
# co = cohere.Client(api_key)

# def generate_category_pub(category_name):

#     prompt = f"""Generate an attractive and engaging phrase that describes the following category for a publication in a marketplace:

# Category: {category_name}

# The phrase should be catchy, informative, and appeal to potential readers or customers. It should highlight the essence or key aspects of the category.

# Phrase:"""

#     response = co.generate(
#         model='command',
#         prompt=prompt,
#         max_tokens=50,
#         temperature=0.7,
#         k=0,
#         stop_sequences=[],
#         return_likelihoods='NONE'
#     )

#     return response.generations[0].text.strip()

def escape_quotes(text):
    """Escape single and double quotes for SQL insertion."""
    if text:
        return text.replace("'", "''").replace('"', '\"')
    return text

def generate_sql(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    # List all files in the folder
    files = os.listdir(folder_path)

    if not files:
        print(f"The folder {folder_path} is empty.")
        return
    
    # Open image url mapping (old url: cloud url)
    image_url_mapping_path = './image_url_mapping.json'
    with open(image_url_mapping_path, 'r', encoding='utf-8') as file:
        url_mapping = json.load(file)

    # Initialize lists to store SQL queries
    category_sql = []
    product_sql = []
    review_sql = []
    
    category_id_counter = 1
    product_id_counter = 1
    review_id_counter = 1

     # Read and print the contents of each file
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        
        # Check if it's a file (not a subdirectory)
        if os.path.isfile(file_path):
            print(f"\nReading file: {file_name}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                    # Extract category information
                    category_name = file_name.split('.')[0]
                    formatted_category_name = category_name.replace('_', ' ').title()
                    category_sql.append(f"INSERT INTO Category (id, name, image, image_key, pub) VALUES "
                                        f"({category_id_counter}, '{formatted_category_name}', 'category-image', 'category-image-key', 'pub');")

                    # Process each product
                    for item in data:                        
                        # Extract product information
                        idCategory = category_id_counter
                        idSeller = 100 + random.randint(1, 100)  # Random idSeller between 1 and 100
                        name = escape_quotes(item.get("name", ""))
                        description = escape_quotes(item.get("description", ""))
                        stock = item.get("stock", random.randint(1, 25))
                        offers = item.get("offers")
                        if offers.get('price'):
                            price = offers.get('price')
                        else:
                            price = offers.get('highPrice')
                        date_creation = datetime.now().isoformat()
                        imageKey = item.get("sku", "")
                        old_image_url = item.get("images", [])[0] if item.get("images") else None
                        cloud_image_url = url_mapping.get(category_name, {}).get(old_image_url)
                        # clean db
                        if not cloud_image_url or not price:
                            continue
                        
                        product_sql.append(f"INSERT INTO Product (id, id_category, id_seller, name, description, price, stock, date_creation, image, image_key) VALUES "
                                        f"({product_id_counter}, {idCategory}, {idSeller}, '{name}', '{description}', {price}, {stock}, '{date_creation}', '{cloud_image_url}', '{imageKey}');")
                        
                        # Extract reviews
                        for review in item.get("reviews", []):
                            # idUser = review.get("author", {}).get("name", "")
                            idUser = random.randint(1, 100)
                            rating = review.get("reviewRating", {}).get("ratingValue", 0)
                            comment = review.get("reviewBody", "")

                            # Handle multi-line comments
                            comment_lines = comment.split("\n")
                            comment_sql = escape_quotes(comment_lines[0])

                            review_sql.append(f"INSERT INTO Review (id, id_user, id_product, date, rating, comment) VALUES "
                                            f"({review_id_counter}, '{idUser}', {product_id_counter}, '{datetime.now().isoformat()}', {rating}, '{comment_sql}');")
                            review_id_counter += 1
                        
                        product_id_counter += 1
            
            except Exception as e:
                print(f"Error reading {file_name}: {str(e)}")
        
        # Increment category id
        category_id_counter += 1
    
    return category_sql, product_sql, review_sql

# Example usage

def write_sql_file():
    folder_path = "./bestbuy_json_data"
    category_sql, product_sql, review_sql = generate_sql(folder_path)
    # print(category_sql)
    # print(product_sql)

    # Write all SQL statements to the file
    with open('./init.sql', 'w') as file:
        file.write("\n".join(category_sql))
        file.write('\n')
        file.write("\n".join(product_sql))
        file.write('\n')
        file.write("\n".join(review_sql))

write_sql_file()

# pub = generate_category_pub("printers")
# print(pub)
