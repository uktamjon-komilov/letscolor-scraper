import requests
from selenium.webdriver.chrome.options import Options
import json
import os
import re
from selenium import webdriver


def translate_text(text, from_lang, to_lang):
    from googletrans import Translator
    translator = Translator()
    result = translator.translate(str(text), src=from_lang, dest=to_lang)
    return result.text


def generate_category_map(title, link, image=None):
    data = {
        "title_ru": title,
        "title_uz": translate_text(title, "ru", "uz"),
        "title_en": translate_text(title, "ru", "en"),
        "link": "https://letscolor.uz{}".format(link),
        "children": []
    }
    if image:
        data["image"] = image
        data["local_image"] = "/category/photos/{}".format(image.split("/")[-1])
    
    return data


def generate_category_map_in_ru(title, link):
    return {
        "title": title,
        "link": "https://letscolor.uz{}".format(link),
        "children": []
    }


def download(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


def send_category(category, parent=None):
    data = {
        "translations": json.dumps({
            "ru": {
                "name": category["title_ru"]
            },
            "en": {
                "name": category["title_en"]
            },
            "uz": {
                "name": category["title_uz"]
            }
        }),
        "slug": category["link"].split("/")[-1]
    }

    if parent:
        data["parent"] = parent
    
    files = {}
    if category.get("image", None):
        filename = category["image"].split("/")[-1]
        filepath = os.path.join(os.getcwd(), "category", "photos", filename)
        download(category["image"], filepath)
    
        files["icon"] = (filename, open(filepath, "rb"))

    result = requests.post("http://45.129.170.154/api/categories/", files=files, data=data)
    if result.status_code == 200 or result.status_code == 201:
        return result
    else:
        print(result.status_code)
        print(result.content)
        return send_category(category, parent)


def convert_to_float(dom_element):
    try:
        price = re.findall("\d+\,\d+", str(dom_element))[0].replace(",", ".")
    except:
        price = re.findall("\d+", str(dom_element))[0]
    
    try:
        result = float(price)
    except:
        result = 0.0
    return result * 1000


def get_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return get_content(url)


def get_product_detail(link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="C:\Program Files (x86)\chromedriver.exe", chrome_options=chrome_options)
    driver.get(link)
    product = {
        "title": get_product_title(driver),
        "slug": link.split("/")[-1].split(".")[0],
        "category": get_product_category(driver),
        "price": get_product_price(driver),
        "description": get_product_description(driver),
        "photo": get_product_photo(driver),
    }

    return product


def get_product_title(driver):
    return driver.find_element_by_xpath("/html/body/div[5]/div[2]/div[1]/h1").text


def get_product_category(driver):
    return driver.find_element_by_xpath("/html/body/div[5]/div[2]/div[1]/h6").text


def get_product_price(driver):
    return convert_to_float(driver.find_element_by_xpath("/html/body/div[5]/div[2]/div[1]/div/h2").text)


def get_product_description(driver):
    return driver.find_element_by_xpath("/html/body/div[5]/div[4]/div[1]/div[1]/p").text


def get_product_photo(driver):
    try:
        photo = driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[1]/div/ul/li/a/img").get_attribute("src")
    except:
        photo = ""
    return photo


def localize_photo(product):
    if product.get("photo", None):
        filename = product["photo"].split("/")[-1]
        filepath = os.path.join(os.getcwd(), "product", "photos", filename)
        download(product["photo"], filepath)
        product["local_photo"] = str(os.path.join("product", "photos", filename))
    return product


def send_product(product):
    result = requests.post("http://45.129.170.154/api/products/", json=product)
    if result.status_code == 200 or result.status_code == 201:
        return result
    else:
        print(result.status_code)
        return send_product(product)