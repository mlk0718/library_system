import pymysql
import utils


def query(sql,*args):
    conn, cursor = utils.get_conn()
    cursor.execute(sql,args)
    res = cursor.fetchall()
    utils.close_conn(conn,cursor)
    return res


def get_left1_data():
    sql = "select BorrowDate,sum(Lending) from borrow,category,book where(borrow.BookNum=book.BookNum) and (book.Categories=category.Categories)  GROUP BY (BorrowDate) Order by(BorrowDate) ASC"
    res = query(sql)
    return res


def get_right1_data():
    sql = "select Categories,Total from Category"
    res = query(sql)
    return res


def get_right2_data():
    sql = "select sum(Lending) as Lending,sum(total-Lending) as Stock from category"
    res = query(sql)
    return res


if __name__=="__main__":
    print(get_left1_data())
    print(get_right1_data())
    print(get_right2_data())