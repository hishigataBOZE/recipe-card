import requests
from bs4 import BeautifulSoup
import re
import csv


# メイン
def main():
    # TODO read csv
    # url_list = ["https://mariegohan.com/6841", "https://mariegohan.com/5328"]
    # url_list = ["https://cookien.com/recipe/22918/", "https://cookien.com/recipe/1557/"]
    url_list = ["https://mayukitchen.com/komatsuna-fried-tofu-chinese-sauce/"]

    csv_list = []
    header = ['#URL', 'タイトル', '画像URL', '人数', '材料']
    csv_list.append(header)

    for url in url_list:
        csv_list.append(scrape2array(url))

    # CSV出力
    # print(csv_list)
    with open('./output/recipe_scraped.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)


# スクレイピングして配列化
def scrape2array(url):
    url2func = {'mariegohan.com': 'scrape_mariegohan',
                'cookien.com': 'scrape_cookien',
                'mayukitchen.com': 'scrape_mayukitchen'}

    # サイトごとのスクレイピング実行
    for uri, func in url2func.items():
        if uri in url:
            return eval(func)(url)


# スクレイピング：cookien.com
def scrape_cookien(url):
    body = []
    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")
    base = soup.select_one("div#r_contents")

    # 記事URL
    body.append(url)

    # レシピ名
    name = soup.select('h1.entry-title')[0].text.strip()
    body.append(name)

    # 画像URL
    img = soup.select_one("div.entry-content").select_one("img").get("src")
    body.append(img)

    # 人数
    num_people = base.h2.select_one("span.addexp").string
    body.append(num_people)

    # 材料
    tmp_ingredient = ""
    contents_ingredients = base.find_all("p")
    for line in contents_ingredients:
        tmp_ingredient += line.get_text() + '\n'

    body.append(tmp_ingredient)

    return body


# スクレイピング：mayukitchen.com
def scrape_mayukitchen(url):
    body = []
    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")
    base = soup.select_one("div.entry-content").select_one('h2')
    # next_sibling2つで4人分の位置。3つで8人分の位置
    base = base.next_sibling.next_sibling.next_sibling

    # 記事URL
    body.append(url)

    # レシピ名
    name = soup.select_one('h1.entry-title').text.strip()
    body.append(name)

    # 画像URL
    img = soup.select_one("div.entry-content").select_one("img").get("src")
    body.append(img)

    # 人数
    base_num = base.p.span.text
    body.append(base_num)

    # 材料
    tmp_ind = ""
    base_ind = base.ul.find_all("li")
    for ind in base_ind:
        if ind.string != "\n":
            tmp_ind += ind.string + "\n"
    body.append(tmp_ind)

    return body


# スクレイピング：mariegohan
def scrape_mariegohan(url):
    body = []
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    title_ingredients = soup.find(class_="ingredients")

    # 記事URL
    body.append(url)

    # レシピ名
    title_recipe = soup.find(class_="entry-title")
    body.append(title_recipe.string)

    # 画像URL
    img = soup.section.img.get('data-src')
    body.append(img)

    # 人数
    num_people_content = title_ingredients.previous_sibling.previous_sibling
    num_people = re.search(r'(人数：.+)$', num_people_content.string)
    body.append(num_people.group())

    # 材料
    contents_ingredients = title_ingredients.next_sibling.next_sibling.contents

    tmp_ingredient = ''
    for ingredient in contents_ingredients:
        if ingredient != '\n':
            tmp_ingredient += ingredient.string + '\n'

    body.append(tmp_ingredient.rstrip())

    return body


main()
