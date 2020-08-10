import requests
from bs4 import BeautifulSoup
import re
import csv
from urllib.parse import urlparse
import qrcode
import pathlib
import os
import shutil


# メイン
def main():
    # 出力ディレクトリお掃除
    output_dir = "./output/"
    shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    # 出力準備
    header = ['#No', 'URL', 'タイトル', '画像URL', '人数', '材料', 'QRコード画像']
    csv_list = []
    csv_list.append(header)

    # URL読み込み
    with open('./data/url_list.csv', 'r') as f:
        next(csv.reader(f))
        reader = csv.reader(f)
        for row in reader:
            csv_line = []
            no = row[0]
            url = row[1]
            csv_line.append(no)
            csv_line.extend([url])
            scraped_rows = scrape2array(url)
            if scraped_rows:
                qr_abs_path = qr_save(url, output_dir + no.zfill(3) + '.png')
                csv_line.extend(scraped_rows)
                csv_line.extend([qr_abs_path])
            print(csv_line)
            csv_list.append(csv_line)

    print(csv_list)
    # return

    # DEBUG
    # url_list = ["https://mariegohan.com/6841", "https://mariegohan.com/5328"]
    # url_list = ["https://cookien.com/recipe/22918/", "https://cookien.com/recipe/1557/"]
    # url_list = [["1", "https://mayukitchen.com/komatsuna-fried-tofu-chinese-sauce/"]]

    # CSV出力
    # print(csv_list)
    with open('./output/recipe_scraped.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)


# QRコードを保存したら絶対パスを返す
def qr_save(url, qr_path):
    img = qrcode.make(url)
    img.save(qr_path)
    return str(pathlib.Path(qr_path).resolve())


# スクレイピングして配列化
def scrape2array(url):
    url2func = {'mariegohan.com': 'scrape_mariegohan',
                'cookien.com': 'scrape_cookien',
                'mayukitchen.com': 'scrape_mayukitchen'}

    # サイトごとのスクレイピング実行
    for uri, func in url2func.items():
        if uri in url:
            return eval(func)(url)
        else:
            return False


# スクレイピング：cookien.com
def scrape_cookien(url):
    body = []
    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")
    base = soup.select_one("div#r_contents")

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

    # レシピ名
    name = soup.select_one('h1.entry-title').text.strip()
    body.append(name)

    # 画像URL
    img = soup.select_one("div.entry-content").select_one("img").get("src")
    parsed_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
    # 相対パス→絶対パスに変換
    body.append(parsed_url + img)

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

    # レシピ名
    title_recipe = soup.find(class_="entry-title")
    body.append(title_recipe.string)

    # 画像URL
    img = soup.section.img.get('data-src')
    body.append(img)

    # 人数
    try:
        num_people_content = title_ingredients.previous_sibling.previous_sibling
        num_people = re.search(r'(人数.+)$', num_people_content.string)
        num_people_res = num_people.group()
    except:
        num_people_res = ""
    body.append(num_people_res)

    # 材料
    contents_ingredients = title_ingredients.next_sibling.next_sibling.contents

    tmp_ingredient = ''
    for ingredient in contents_ingredients:
        if ingredient != '\n':
            tmp_ingredient += ingredient.string + '\n'

    body.append(tmp_ingredient.rstrip())

    return body


main()
