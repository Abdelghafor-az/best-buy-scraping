import io
import re
import requests
from tqdm import tqdm
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from PIL import Image
import json


def download_image(download_path, url, file_name):
    image_content = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"}).content
    image = Image.open(io.BytesIO(image_content))
    file_path = download_path + file_name

    with open(file_path, 'wb') as f:
        image.save(f, 'PNG')

    return file_path


def write_json(new_data, filename='data.json'):
    try:
        with open(filename, 'r+') as file:
            file_data = json.load(file)
            file_data = file_data + new_data
            file.seek(0)
            json.dump(file_data, file, indent=2)
    except:
        with open(filename, 'w') as file:
            json.dump(new_data, file, indent=2)


wd = Chrome()

categories = [
    {
        'url': 'https://www.bestbuy.com/site/promo/small-appliance-deals',
        'category': 'Small Appliances, Floor Care & Home Air Quality'
    },
    {
        'url': 'https://www.bestbuy.com/site/promo/smart-home-wi-fi-security-deals',
        'category': 'Smart Home, Security & Wi-Fi'
    },
    {
        'url': 'https://www.bestbuy.com/site/promo/printer-and-home-office-deals',
        'category': 'Printers & Computer Accessories'
    },
    {
        'url': 'https://www.bestbuy.com/site/promo/hoverboards-and-electric-scooters-deals',
        'category': 'Hoverboard & Electric Scooter'
    },
]
hrefs = []
id_count = 1
products = []

for category in categories:

    for i in range(1, 3):
        page_url = category['url'] + "?intl=nosplash&cp=" + str(i)
        wd.get(page_url)
        products_links = wd.find_elements(By.CSS_SELECTOR, ".sku-title a")

        for product_link in products_links:
            hrefs.append(product_link.get_property('href'))

    for href in tqdm(hrefs):
        wd.get(href)

        try:
            image_url = wd.find_element(By.CSS_SELECTOR, 'img.primary-image').get_property('src').split(';')[0]
            title = wd.find_element(By.CLASS_NAME, "sku-title").text
            price = wd.find_element(By.CLASS_NAME, "priceView-customer-price").find_elements(By.TAG_NAME, 'span')[0].text
            description = wd.find_element(By.CSS_SELECTOR, "meta[name='description']").get_attribute('content')
            image_path = download_image("images/", image_url, str(id_count) + ".png")
            rating = wd.find_element(By.CLASS_NAME, 'ugc-c-review-average').text
        except:
            continue

        products.append({
            'id': id_count,
            'title': title,
            'image': image_path,
            'price': float(re.search(r'\d+\.\d+', price).group()),
            'description': description,
            'availability': True,
            'category': category['category'],
            'rating': float(rating),
        })
        id_count += 1

    write_json(products, "data.json")
