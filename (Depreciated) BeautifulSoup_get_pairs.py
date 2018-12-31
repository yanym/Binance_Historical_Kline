from bs4 import BeautifulSoup
import requests

# 本地的
htmlfile_BNB = open('./BNB.html', 'r', encoding='utf-8')
htmlhandle_BNB = htmlfile_BNB.read()
soup_BNB = BeautifulSoup(htmlhandle_BNB, 'lxml')

htmlfile_USD = open('./USD.html', 'r', encoding='utf-8')
htmlhandle_USD = htmlfile_USD.read()
soup_USD = BeautifulSoup(htmlhandle_USD, 'lxml')

htmlfile_ALTS = open('./ALTS.html', 'r', encoding='utf-8')
htmlhandle_ALTS = htmlfile_ALTS.read()
soup_ALTS = BeautifulSoup(htmlhandle_ALTS, 'lxml')

# 外地的
r = requests.get('https://www.binance.com/en')
soup_BTC = BeautifulSoup(r.text, features='lxml')


get_raw_tag_content_BTC = soup_BTC.find_all("div", class_="ReactVirtualized__Table__rowColumn")
get_raw_tag_content_BNB = soup_BNB.find_all("div", class_="ReactVirtualized__Table__rowColumn")
get_raw_tag_content_ALTS = soup_ALTS.find_all("div", class_="ReactVirtualized__Table__rowColumn")
get_raw_tag_content_USD = soup_USD.find_all("div", class_="ReactVirtualized__Table__rowColumn")

pair_list = []

for tag in get_raw_tag_content_BTC:
	temp_str = tag.get_text()
	if (temp_str.find("/") >= 0):
		pair_list.append(temp_str.replace("/", ""))

for tag in get_raw_tag_content_BNB:
	temp_str = tag.get_text()
	if (temp_str.find("/") >= 0):
		pair_list.append(temp_str.replace("/", ""))

for tag in get_raw_tag_content_ALTS:
	temp_str = tag.get_text()
	if (temp_str.find("/") >= 0):
		pair_list.append(temp_str.replace("/", ""))

for tag in get_raw_tag_content_USD:
	temp_str = tag.get_text()
	if (temp_str.find("/") >= 0):
		pair_list.append(temp_str.replace("/", ""))

for x in pair_list:
	print(x)
