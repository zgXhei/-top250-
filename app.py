from flask import Flask, render_template
import pymysql

app = Flask(__name__)


def getDB():
    db = pymysql.connect(user='root', host='127.0.0.1', port=3306, password='123456', database='douban')
    return db


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/index')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/movies')
@app.route('/movies/<int:page>')
def movies(page=1):  # put application's code here
    db = getDB()
    cursor = db.cursor()
    sql = 'select ranks,film_url,film_name,film_name_en,rating_num,rating_people,summary,director from movies limit {},{}'.format(
        (page - 1) * 25, page * 25)
    cursor.execute(sql)
    data = cursor.fetchall()
    datalist = []
    for i in data:
        datalist.append(i)

    sql1 = 'select count(*) from movies'
    cursor.execute(sql1)
    total = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template('movies.html', page=page, movies=datalist, countnum=int(int(total[0]) / 25))


@app.route('/tj')
def tj():  # put application's code here
    db = getDB()
    cursor = db.cursor()
    # 计算评分
    rating = []  # 评分
    num = []  # 计算每个评分的数量
    sql = 'select rating_num,count(*) from movies GROUP BY rating_num'
    cursor.execute(sql)
    rating_num = cursor.fetchall()
    for i in rating_num:
        rating.append(float(i[0]))
        num.append(int(i[1]))
    # 计算评分
    filmtypes_list = []  # 类型
    filmtypes_num = []  # 计算每个类型的数量
    sql1 = 'SELECT filmType,count(filmType) FROM movietype GROUP BY filmType'
    cursor.execute(sql1)
    filmtype = cursor.fetchall()
    for j in filmtype:
        filmtypes_list.append(j[0])
        filmtypes_num.append(j[1])
    years = []  # 年份
    years_num = []  # 计算每个年份的数量
    sql2 = 'SELECT YEAR(STR_TO_DATE(initialReleaseData,"%Y-%m-%d")) as years,count(*) FROM movies where STR_TO_DATE(initialReleaseData,"%Y-%m-%d")>DATE_SUB(CURRENT_DATE,INTERVAL 20 YEAR) GROUP BY YEAR(STR_TO_DATE(initialReleaseData,"%Y-%m-%d")) ORDER BY YEAR(STR_TO_DATE(initialReleaseData,"%Y-%m-%d"))'
    cursor.execute(sql2)
    years_list = cursor.fetchall()
    for y in years_list:
        years.append(y[0])
        years_num.append(y[1])
    top10 = []  # 年份
    top10_num = []  # 计算每个年份的数量
    sql3 = 'SELECT YEAR(STR_TO_DATE(initialReleaseData,"%Y-%m-%d")) as years,count(*) FROM movies GROUP BY YEAR(STR_TO_DATE(initialReleaseData,"%Y-%m-%d")) ORDER BY count(*) desc limit 10'
    cursor.execute(sql3)
    top10_list = cursor.fetchall()
    for y in top10_list:
        top10.append(y[0])
        top10_num.append(y[1])
    cursor.close()
    db.close()
    print(filmtypes_list)
    print(years)
    return render_template('tj.html', rating=rating, num=num, filmtypes_list=filmtypes_list,
                           filmtypes_num=filmtypes_num, years=years, years_num=years_num, top10=top10,
                           top10_num=top10_num)


@app.route('/rp')
@app.route('/rp/<int:page>')
def pj(page=1):  # put application's code here
    db = getDB()
    cursor = db.cursor()
    sql = 'select ranks,film_url,film_name,film_name_en,rating_num,rating_people from movies limit {},{}'.format(
        (page - 1) * 25, page * 25)
    cursor.execute(sql)
    data = cursor.fetchall()
    datalist = []
    for i in data:
        datalist.append(i)

    sql1 = 'select count(*) from movies'
    cursor.execute(sql1)
    total = cursor.fetchone()


    sql2 = 'select film_url from movies'
    cursor.execute(sql2)
    url_list = cursor.fetchone()
    urls = []
    for u in url_list:
        dp = (u+'comments?sort=new_score&status=P')
        rp = (u+'reviews')
        urls.append([rp,dp])
    cursor.close()
    db.close()

    return render_template('rp.html', page=page, movies=datalist, countnum=int(int(total[0]) / 25), urls=urls)


if __name__ == '__main__':
    app.run()
