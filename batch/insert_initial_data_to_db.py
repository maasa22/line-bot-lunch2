import config
import psycopg2

user = config.user
password = config.password
host = config.host
port_db = config.port_db
database = config.database

TEST_USER_ID_AOS = config.TEST_USER_ID_AOS
TEST_USER_ID1 = "sample1"
TEST_USER_ID2 = "sample2"
TEST_USER_ID3 = "sample3"
TEST_USER_ID4 = "sample4"
TEST_USER_ID5 = "sample5"

conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS favorite_restaurants")
cur.execute('''CREATE TABLE favorite_restaurants
            (user_id text, favorite_restaurant_name text)''')

cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '韓花')".format(TEST_USER_ID_AOS))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ぱいかじ 新宿新南口店')".format(TEST_USER_ID_AOS))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ベーカリー＆レストラン 沢村')".format(TEST_USER_ID_AOS))

cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '韓花')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '韓花')".format(TEST_USER_ID2))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '韓花')".format(TEST_USER_ID3))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '韓花')".format(TEST_USER_ID4))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '韓花')".format(TEST_USER_ID5))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ぱいかじ 新宿新南口店')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ぱいかじ 新宿新南口店')".format(TEST_USER_ID2))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ぱいかじ 新宿新南口店')".format(TEST_USER_ID3))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ぱいかじ 新宿新南口店')".format(TEST_USER_ID4))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'GARDEN HOUSE SHINJUKU')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'GARDEN HOUSE SHINJUKU')".format(TEST_USER_ID2))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'GARDEN HOUSE SHINJUKU')".format(TEST_USER_ID3))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'サンマルクカフェ 新宿新南口店')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'サンマルクカフェ 新宿新南口店')".format(TEST_USER_ID2))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ROSEMARY’S TOKYO')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'COBI COFFEE box')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ブルーボトルコーヒー 新宿')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'ＯＴＴＩＭＯ Ｓｅａｆｏｏｄ ｇａｒｄｅｎ')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'GARDEN HOUSE SHINJUKU')".format(TEST_USER_ID1))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'サンマルクカフェ 新宿新南口店')".format(TEST_USER_ID2))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', 'サンマルクカフェ 新宿新南口店')".format(TEST_USER_ID3))
conn.commit() # Save (commit) the changes
cur.close()
conn.close()
