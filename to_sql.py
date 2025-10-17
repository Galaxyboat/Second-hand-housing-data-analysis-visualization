from pymysql import *

conn = connect(host='localhost', user='second_house', password='123456', database='qz_test_sql', port=3306)

sql = '''
create table history(
id int primary key auto_increment,
city varchar(255),
price varchar(255),
)
'''
