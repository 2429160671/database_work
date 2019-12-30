import pymysql

# 打开数据库连接
try:
    db = pymysql.connect("212.64.72.66", "root", "xaut111", "ennio_csdn")
except Exception as err:
    print('2222', str(err))



# import pymysql
#
# # 打开数据库连接
# try:
#     db = pymysql.connect("123.56.123.53", "root", "Xaut--123", "xaut")
# except Exception as err:
#     print('2222', str(err))