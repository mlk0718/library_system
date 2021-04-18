from werkzeug.security import generate_password_hash, check_password_hash  # 密码保护，使用hash方法
from flask.json import JSONEncoder as _JSONEncoder, JSONEncoder
from flask import Flask, render_template,redirect, url_for,request,session,jsonify
from flask import Flask as _Flask
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import pymysql
import datetime
import string
import time
import utils
import traceback
import Collect
import config

app = Flask(__name__)
app.config.from_object(config)
db=SQLAlchemy(app)


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
            return float(o)

        super(JSONEncoder, self).default(o)


class Flask(_Flask):
    json_encoder = JSONEncoder


@app.route("/")
def login():
    return render_template("Login.html")


@app.route('/register')
def register():
    return render_template("register.html")


# 获取注册请求及处理
@app.route('/registuser')
def getRigistRequest():
    # 把用户名和密码注册到数据库中

    # 连接数据库,此前在数据库中创建数据库Course
    db = pymysql.connect("localhost", "root", "123456", "library_sys")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO user(user, password) VALUES (" + request.args.get('user') + ", " + request.args.get('password') + ")"
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        # 注册成功之后跳转到登录页面
        return render_template('login.html')
    except:
        # 抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
        return '注册失败'
    # 关闭数据库连接
    db.close()


@app.route('/login')
def getLoginRequest():
#查询用户名及密码是否匹配及存在
    #连接数据库,此前在数据库中创建数据库TESTDB
    db = pymysql.connect("localhost","root","123456","library_sys" )
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from user where user="+request.args.get('user')+" and password="+request.args.get('password')+""
    try:
        # 执行sql语句
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results)==1:
            return render_template("Home.html")
        else:
            return '用户名或密码不正确'
        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        traceback.print_exc()
        db.rollback()
    # 关闭数据库连接
    db.close()


@app.route('/Home')
def Home():
    return render_template("Home.html")


@app.route("/value1")
def get_l1_data():
    data = Collect.get_left1_data()
    Total,Lending,BorrowDate=[],[],[]
    total=0
    for a,b in data[0:]:
        BorrowDate.append(a.strftime("%m-%d"))
        Lending.append(b)
        total=total+b
        Total.append(total)
    return jsonify({"BorrowDate":BorrowDate,"Total":Total,"Lend":Lending})


@app.route("/value2")
def get_l2_data():
    data = Collect.get_right1_data()
    Categories=[]
    cate={}
    for a,b in data[0:]:
        cate={"name":a,"y":b}
        Categories.append(cate)
    return jsonify({"categories":Categories})


@app.route("/value3")
def get_r2_data():
    data = Collect.get_right2_data()
    Word=['借出','库存']
    Situation=[]
    t=0
    situation={}
    for i in data[0:]:
        for j in i:
            j=int(j)
            situation={"name":Word[t],"y":j}
            t=t+1
            Situation.append(situation)
    return jsonify({"Situation":Situation})


@app.route('/BookIfo')
def BooIfo():
    sql = "select * from %s" %(utils.Table1)
    content,labels = utils.query(sql,utils.Table1)
    return render_template('BookIfo.html', labels=labels, content=content)


@app.route('/CardIfo')
def CardIfo():
    sql = "select * from %s" %(utils.Table4)
    content,labels = utils.query(sql,utils.Table4)
    return render_template('CardIfo.html', labels=labels, content=content)


@app.route('/BorrowIfo')
def BorIfo():
    sql = "select * from %s" %(utils.Table2)
    content,labels = utils.query(sql,utils.Table2)
    return render_template('BorrowIfo.html', labels=labels, content=content)


@app.route('/sqlborrow',methods=['GET','POST'])
def temporary():
    # 获取url中传过来的uid,yid
    yid = request.args.get('yid')
    uid = request.args.get('uid')
    if yid=='N':
        return render_template('Borrow.html',uid=uid)
    else:
        return redirect(url_for('BooIfo'))


@app.route('/sqlborrow2',methods=['GET','POST'])
def sqlborrow1():
    if request.method == 'POST':
        data = request.form
        today = str(datetime.date.today())
        sql = "update Book set Islend='Y' where BookNum=%s" %data['uid']
        utils.execu(sql)
        sql = "INSERT INTO Borrow (CardNum,BookNum,BorrowDate,ValidTerm) VALUES ('%s','%s','%s','%s')" %(data['CardNum'],data['uid'],today,'30')
        utils.execu(sql)
        return redirect(url_for('BorIfo'))


@app.route('/Boomodify',methods=['GET','POST'])
def sqlmodify1():
    if request.method == 'POST':
        data = request.form
        sql = "update %s set BookNum='%s',BookName='%s',Categories='%s',Author='%s',Press='%s',PublicateDate='%s',Price='%s',IsLend='%s' where BookNum=%s" \
              % (utils.Table1, data['BookNum'], data['BookName'], data['Categories'], data['Author'], data['Press'], data['PublicateDate'], data['Price'], data['IsLend'], data['uid'])
        utils.execu(sql)
        return redirect(url_for('BooIfo'))
    else:
        uid = int(request.args.get('uid'))
        sql = "select * from %s" %(utils.Table1)
        content, labels = utils.query(sql,utils.Table1)
        sql = "select categories from %s" % (utils.Table3)
        categories = utils.getData(sql)
        return render_template('BooModify.html', labels=labels, content=content, uid=uid, categories=categories)


@app.route('/Boodelete',methods=['GET','POST'])
def sqldelete1():
    uid = request.args.get('uid')
    sql = "delete from %s where BookNum = %s" %(utils.Table1,uid)
    utils.delete(sql)
    return redirect(url_for('BooIfo'))


@app.route('/Booadd',methods=['GET','POST'])
def add1():
    if request.method == 'POST':
        data = request.form
        sql = "INSERT INTO Book (BookNum,BookName,Categories,Author,Press,PublicateDate,Price,IsLend) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" \
              % (data['BookNum'], data['BookName'], data['Categories'], data['Author'],\
                 data['Press'], data['PublicateDate'], data['Price'], data['IsLend'])
        utils.execu(sql)
        sql = "update Category set total=total+1 where Categories=%s" %data['Categories']
        utils.execu(sql)
        return redirect(url_for('BooIfo'))
    else:
        sql = "select * from %s" %(utils.Table1)
        content, labels = utils.query(sql,utils.Table1)
        sql = "select categories from %s" %(utils.Table3)
        categories = utils.getData(sql)
        return render_template('BooAdd.html', labels=labels, content=content, categories=categories)


@app.route('/Boosearch',methods=['GET','POST'])
def search1():
    sql = "select * from %s" % (utils.Table1)
    Unu, La = utils.query(sql, utils.Table1)  # Unu为无用数据,La为表字段
    if request.method == 'POST':
        content = request.form
        data = []
        if content['Search']:
            if not data:
                sql1 = "select * from %s where concat(%s,%s,%s,%s,%s,%s,%s) like " \
                      %(utils.Table1, La[0], La[1], La[2], La[3], La[4], La[6], La[7])
                sql2 = "'%"
                sql3 = "%s" %(content['Search']) +"%'"
                sql = sql1 + sql2 + sql3
                data, labels = utils.query(sql, utils.Table1)
            return render_template('BooSearch.html', labels=labels, data=data)
        else:
            return redirect(url_for('BooIfo'))
    else:
        return redirect(url_for('BooIfo'))


@app.route('/Borreturn')
def sqlreturn():
    zid = request.args.get('zid')
    if not zid:
        uid = request.args.get('uid')
        yid = request.args.get('yid')
        today = str(datetime.date.today())
        sql = "update %s set ReturnDate='%s' where BorrowNum = %s"%(utils.Table2,today,uid)
        utils.execu(sql)
        sql = "update %s set IsLend='N' where BookNum = %s" %(utils.Table1, yid)
        utils.execu(sql)
        return redirect(url_for('BorIfo'))
    else:
        return redirect(url_for('BorIfo'))


@app.route('/Bordelay')
def sqldelay():
    zid = request.args.get('zid')
    if zid is None:      #zid类型为NoneType,值为None
        uid = request.args.get('uid')
        sql = "update %s set ValidTerm=ValidTerm+30 where BorrowNum = %s" % (utils.Table2, uid)
        utils.execu(sql)
        return redirect(url_for('BorIfo'))
    else:
        return redirect(url_for('BorIfo'))


@app.route('/Bordelete',methods=['GET','POST'])
def sqldelete2():
    uid = request.args.get('uid')
    sql = "delete from %s where BorrowNum = %s" %(utils.Table2,uid)
    utils.delete(sql)
    return redirect(url_for('BorIfo'))


@app.route('/Borsearch',methods=['GET','POST'])
def search2():
    sql = "select * from %s" % (utils.Table2)
    Unu, La = utils.query(sql, utils.Table2)  # Unu为无用数据,La为表字段
    if request.method == 'POST':
        content = request.form
        data = []
        if content['Search']:
            if not data:
                sql1 = "select * from %s where concat(%s,%s,%s) like " %(utils.Table2, La[0], La[1], La[2])
                sql2 = "'%"
                sql3 = "%s" %(content['Search']) +"%'"
                sql = sql1 + sql2 + sql3
                data, labels = utils.query(sql, utils.Table2)
            return render_template('BorSearch.html', labels=labels, data=data)
        else:
            return redirect(url_for('BorIfo'))
    else:
        return redirect(url_for('BorIfo'))

@app.route('/Cardmodify',methods=['GET','POST'])
def sqlmodify3():
    if request.method == 'POST':
        data = request.form
        sql = "update %s set CardNum='%s',CardName='%s',TypeName='%s',Sex='%s',WorkUnit='%s',Address='%s',Telephone='%s',Email='%s',RegisterDate='%s' where CardNum=%s" \
              % (utils.Table4, data['CardNum'], data['CardName'], data['TypeName'], data['Sex'], data['WorkUnit'], data['Address'], data['Telephone'], data['Email'],data['RegisterDate'], data['uid'])
        utils.execu(sql)
        return redirect(url_for('CardIfo'))
    else:
        uid = int(request.args.get('uid'))
        sql = "select * from %s" %(utils.Table4)
        content, labels = utils.query(sql,utils.Table4)
        sql = "select TypeName from %s" % (utils.Table5)
        TypeName = utils.getData(sql)
        return render_template('CardModify.html', labels=labels, content=content, uid=uid, TypeName=TypeName)

@app.route('/Carddelete',methods=['GET','POST'])
def sqldelete3():
    uid = request.args.get('uid')
    sql = "delete from %s where CardNum = %s" %(utils.Table4,uid)
    utils.delete(sql)
    return redirect(url_for('CardIfo'))


@app.route('/Cardadd',methods=['GET','POST'])
def add3():
    if request.method == 'POST':
        data = request.form
        print(data)
        sql = "INSERT INTO Card (CardNum,CardName,Type,Sex,Workunit,Address,Telephone,Email,RegisterDate) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" \
              % (data['CardNum'], data['CardName'], data['Type'], data['Sex'],\
                 data['WorkUnit'], data['Address'], data['Telephone'], data['Email'],data['RegisterDate'])
        utils.execu(sql)
        return redirect(url_for('CardIfo'))
    else:
        sql = "select * from %s" %(utils.Table4)
        content, labels = utils.query(sql,utils.Table4)
        sql = "select TypeName from %s" %(utils.Table5)
        TypeName = utils.getData(sql)
        return render_template('CardAdd.html', labels=labels, content=content, TypeName=TypeName)

@app.route('/CardSearch',methods=['GET','POST'])
def search3():
    sql = "select * from %s" % (utils.Table4)
    Unu, La = utils.query(sql, utils.Table4)  # Unu为无用数据,La为表字段
    if request.method == 'POST':
        content = request.form
        data = []
        if content['Search']:
            if not data:
                sql1 = "select * from %s where concat(%s,%s,%s,%s) like " \
                      %(utils.Table4, La[0], La[1], La[2], La[3])
                print( La[0], La[1], La[2], La[3])
                sql2 = "'%"
                sql3 = "%s" %(content['Search']) +"%'"
                sql = sql1 + sql2 + sql3
                data, labels = utils.query(sql, utils.Table4)
            return render_template('CardSearch.html', labels=labels, data=data)
        else:
            return redirect(url_for('CardIfo'))
    else:
        return redirect(url_for('CardIfo'))


if __name__ == '__main__':
    app.run()
