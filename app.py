import re

from flask import Flask, request, render_template, session, redirect
from utils import query
from utils.getHomeData import *
from utils.getSearchData import *
from utils.getTotalPrice_tData import *
from utils.getRate_tData import *

app = Flask(__name__)
app.secret_key = 'this is secrect_key you know ?'


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        request.form = dict(request.form)

        # 过滤函数
        def filter_fn(item):
            return request.form['email'] in item and request.form['password'] in item

        users = query.querys('select * from user', [], 'select')
        filter_user = list(filter(filter_fn, users))

        if len(filter_user):
            session['email'] = request.form['email']
            return redirect('/home')
        else:
            return render_template('error.html', message='用户邮箱或者密码错误')


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        request.form = dict(request.form)
        print(request.form)
        if request.form['password'] != request.form['passwordChecked']:
            return render_template('error.html', message='两次密码不符合')

        # 定义一个filter过滤函数
        def filter_fn(item):
            return request.form['email'] in item

        users = query.querys('select * from user', [], 'select')
        filter_list = list(filter(filter_fn, users))
        if len(filter_list):
            return render_template('error.html', message='该用户已被注册')
        else:
            query.querys('insert into user(email,password) values(%s,%s)',
                         [request.form['email'], request.form['password']])
            return redirect('/login')


# 退出页面
@app.route('/logout')
def logout():
    session.clear()  # 清除 session 数据
    return redirect('/login')  # 返回 login 登录页面


# 在请求之前的生命周期
# 禁止直接通过修改连接进入      路由拦截
@app.before_request
def before_request():
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):  # 如果正则匹配到的是以 static 静态资源的请求路径开头的 就直接跳过 让它去请求
        return
    if request.path == "/login":  # 如果请求路径是 login 让它去请求
        return
    if request.path == "/register":  # 如果请求路径是 register 让它去请求
        return
    email = session.get('email')
    if email:  # 如果 email 它有 我们 return 掉
        return None
    return redirect('/login')




@app.route('/home', methods=['GET', 'POST'])
def home():
    email = session.get('email')
    maxHouseLen, MaxTotal, MaxPrice, maxtransaction, communityList = getHomeDate()
    locationEcharDate = getLocationsEcharDate()
    row,columns = getTowardsEcharDate()
    tableDate = getTableDate()
    return render_template(
        'index.html',
        email=email,
        maxHouseLen=maxHouseLen,
        MaxTotal=MaxTotal,
        MaxPrice=MaxPrice,
        maxtransaction=maxtransaction,
        communityList=communityList,
        locationEcharDate=locationEcharDate,
        row=row,
        columns=columns,
        tableDate=tableDate
    )

@app.route('/search/<int:houseId>',methods=['GET','POST'])
def search(houseId):
    email = session.get('email')
    if request.method == 'GET':
        resultData=getHouseDetailById(houseId)
    else:
        request.form=dict(request.form)
        resultData=getHouseDetailBySearchWord(request.form['searchWord'])
    # print(resultData)
    return render_template('search.html',resultData=resultData,email=email)

@app.route('/totalPrice_t')
def totalPrice_t():
    getPriceAreaData()
    email = session.get('email')
    row,column=getPriceAreaData()
    housenumData = getAvgtotal_priceData()
    return render_template(
        'totalPrice_t.html',
        email=email,
        row=row,
        column=column,
        housenumData=housenumData
    )

@app.route('/rate_t/<type>',methods=['GET','POST'])
def rate_t(type):
    email=session.get('email')
    locationList = getAllLocations()
    row,column=getAllRataDataByType(type)
    # print(locationList)
    return render_template('rate_t.html',email=email,locationList=locationList,type=type,row=row,column=column)





# 重定向方法
@app.route('/')
def allRequest():
    return redirect('/login')


if __name__ == '__main__':
    app.run(host='127.0.0.2',port='8088')
