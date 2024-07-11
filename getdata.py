# 获取豆瓣top50
import requests
from bs4 import BeautifulSoup
import pymysql
import re


def getDB():
    db = pymysql.connect(user='root', host='127.0.0.1', port=3306, password='123456', database='douban')
    return db


def Agent_info():
    '''保存请求头消息'''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': 'bid=TSSLQX5oulk; ll="118204"; _pk_id.100001.4cf6=30f9d31308ebbb66.1717309728.; _vwo_uuid_v2=D2DBEB7790F4BC49C26C59B6A122C0CFA|750d0744a2a79be72decd29610fbe8fe; __yadk_uid=IAzg1i8RSeFuHG0exLqdmIF0TPs5IBjk; douban-fav-remind=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1719388526%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DCvHw6uUkxCuWRCSvb3ajTdqsB9FrAwYqKWjyBYsV-BldqB4Fe21oqNAIznfBuDP4%26wd%3D%26eqid%3Deed0ce2600016c4600000005667bc96a%22%5D; _pk_ses.100001.4cf6=1; ap_v=0,6.0; __utma=30149280.1343524992.1717309729.1717309729.1719388526.2; __utmb=30149280.0.10.1719388526; __utmc=30149280; __utmz=30149280.1719388526.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.1089445569.1717309729.1717309729.1719388526.2; __utmb=223695111.0.10.1719388526; __utmc=223695111; __utmz=223695111.1719388526.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
        'priority': 'u=0, i',
        'referer': 'https://movie.douban.com/chart',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }
    return headers


def get_url(url):
    print(f'开始抓取网站{url}')
    headers = Agent_info()
    response = requests.get(url=url, headers=headers).text
    bs_text = BeautifulSoup(response, 'lxml')
    pic = bs_text.findAll(attrs={'class': "pic"})
    film_urls = []  # 电影详情地址列表
    for x in pic:
        href = x.a.get('href')
        film_urls.append(href)
    hd = bs_text.findAll(attrs={'class': "hd"})
    film_name_en = []
    for name in hd:
        title = name.a.contents[3].text.strip()
        title = title[2:]
        film_name_en.append(title)
    return film_urls, film_name_en


def get_url_info(film_url, film_name_en, id):
    print(f'开始抓取网站{film_url}')
    headers = Agent_info()
    response = requests.get(url=film_url, headers=headers).text
    bs_text = BeautifulSoup(response, 'lxml')
    # 解析页面内容进行爬取
    ranks = bs_text.find(attrs={'class': "top250-no"}).text.split('.')[1]
    film_name = bs_text.find(attrs={'property': "v:itemreviewed"}).text.split(' ')[0]
    director = bs_text.find(attrs={'id': "info"}).text.split('\n')[1].split(':')[1].strip()
    scriptwriter = bs_text.find(attrs={'id': "info"}).text.split('\n')[2].split(':')[1].strip()
    actor = bs_text.find(attrs={'id': "info"}).text.split('\n')[3].split(':')[1].strip()
    filmType = bs_text.find(attrs={'id': "info"}).text.split('\n')[4].split(':')[1].strip()
    # 做判断，因为页面不一样，类型内容有差别
    types = filmType.split('/')
    if bs_text.find(attrs={'id': "info"}).text.split('\n')[5].split(':')[0] == '官方网站':
        area = bs_text.find(attrs={'id': "info"}).text.split('\n')[6].split(':')[1].strip()
        language = bs_text.find(attrs={'id': "info"}).text.split('\n')[7].split(':')[1].strip()
        initialReleaseData = bs_text.find(attrs={'id': "info"}).text.split('\n')[8].split(':')[1].strip().split('(')[
            0].strip()
        runtime = bs_text.find(attrs={'id': "info"}).text.split('\n')[9].split(':')[1].strip()
    else:
        area = bs_text.find(attrs={'id': "info"}).text.split('\n')[5].split(':')[1].strip()
        language = bs_text.find(attrs={'id': "info"}).text.split('\n')[6].split(':')[1].strip()
        initialReleaseData = bs_text.find(attrs={'id': "info"}).text.split('\n')[7].split(':')[1].strip().split('(')[
            0].strip()
        runtime = bs_text.find(attrs={'id': "info"}).text.split('\n')[8].split(':')[1].strip()
    rating_num = bs_text.find(attrs={'property': "v:average"}).text
    start5_rating_per = bs_text.find(attrs={'class': "rating_per"}).text
    rating_people = bs_text.find(attrs={'property': "v:votes"}).text
    summary = bs_text.find(attrs={'property': "v:summary"}).text
    # 将summary变量中的字符串进行转义处理，然后将转义后的字符串重新赋值给summary变量。这样，summary变量中就存储了一个安全的、可以安全地用于SQL查询的字符串。
    summary = pymysql.converters.escape_str(summary)
    sql = 'insert into movies(film_name,director,scriptwriter,actor,filmType,area,language,initialReleaseData,ranks,runtime,rating_num,start5_rating_per,rating_people,summary,film_name_en,film_url) values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
        film_name, director, scriptwriter, actor, filmType, area, language, initialReleaseData, ranks, runtime,rating_num, start5_rating_per, rating_people, summary, film_name_en, film_url)

    db = getDB()
    cursor = db.cursor()
    cursor.execute(sql)
    cursor.execute('insert into moviehash(movieid) values ("{}")'.format(id))
    for j in range(len(types)):
        cursor.execute('insert into movieType(movieid,filmType) values ("{}","{}")'.format(id, types[j].strip()))
    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':
    db = getDB()
    cursor = db.cursor()
    # 循环遍历，自动化爬取
    for i in range(0, 250, 25):
        film_url, film_name_en = get_url('https://movie.douban.com/top250' + f'?start={str(i)}&filter=')
        for index in range(len(film_url)):
            id = re.search(r'\d\d+', film_url[index]).group()
            sql = 'select movieid from moviehash where movieid="{}";'.format(id)
            cursor.execute(sql)
            data = cursor.fetchall()
            if not data:
                get_url_info(film_url[index], film_name_en[index], id)
