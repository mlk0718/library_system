import time
import pymysql

Table1 = "Book"
Table2 = "Borrow"
Table3 = "Category"
Table4 = "Card"
Table5 = "Type"

def get_time():
    time_str = time.strftime("%Y{}%m{}%d{} %X")
    return time_str.format("年","月","日")

def get_conn():
    """
    :return:连接，游标
    """
    #创建连接
    conn = pymysql.connect(host="127.0.0.1",
                       user="root",
                       password="123456",
                       db="library_sys"
                      )
    cursor = conn.cursor()
    return conn, cursor

def close_conn(conn,cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def execu(sql,*args):
    """
    封装通用执行
    :param sql:
    :param args:
    :return:
    """
    conn, cursor = get_conn()
    cursor.execute(sql, args)
    conn.commit()
    close_conn(conn,cursor)
    return 0

def query(sql,table,*args):
    """
    封装通用查询
    :param sql:
    :param args:
    :return: 返回查询到的结果，((),())的形式
    """
    conn, cursor = get_conn()
    cursor.execute(sql)
    content = cursor.fetchall()

    Insql = "SHOW FIELDS FROM %s" %table
    cursor.execute(Insql, args)
    labels = cursor.fetchall()
    labels = [l[0] for l in labels]
    close_conn(conn,cursor)
    return content, labels

def delete(sql,*args):
    """
    封装通用取消外键约束删除
    :param sql:
    :param args:
    :return:
    """
    conn, cursor = get_conn()

    sql1 = "SET FOREIGN_KEY_CHECKS = 0"
    cursor.execute(sql1, args)

    cursor.execute(sql, args)
    conn.commit()

    sql2 = "SET FOREIGN_KEY_CHECKS = 1"
    cursor.execute(sql2, args)

    close_conn(conn,cursor)
    return 0

def getData(sql,*args):
    """
    封装通用查询
    :param sql:
    :param args:
    :return: 返回查询到的结果，((),())的形式
    """
    conn, cursor = get_conn()
    cursor.execute(sql,args)
    res = cursor.fetchall()
    close_conn(conn,cursor)
    return res

if __name__ == '__main__':
    sql = "select categories from category"
    result = getData(sql)
    for i in result:
        print(i)