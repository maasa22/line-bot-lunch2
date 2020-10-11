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
TEST_USER_ID_LIST = [TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID3, TEST_USER_ID4, TEST_USER_ID5]

conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
cur = conn.cursor()


def insert_votes(num, restaurant_name):
    for i in range(max(num, 5)):
        cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '{}')".format(TEST_USER_ID_LIST[i], restaurant_name))

cur.execute("DROP TABLE IF EXISTS favorite_restaurants")
cur.execute('''CREATE TABLE favorite_restaurants
            (user_id text, favorite_restaurant_name text)''')

cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '鼎泰豐')".format(TEST_USER_ID_AOS))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '華菜樓 ルミネ新宿店')".format(TEST_USER_ID_AOS))
cur.execute("INSERT INTO favorite_restaurants VALUES ('{}', '石の家')".format(TEST_USER_ID_AOS))

print("中華")
insert_votes(5, '鼎泰豐')
insert_votes(4, '華菜樓 ルミネ新宿店')
insert_votes(2, '隨園別館 新宿タカシマヤ タイムズスクエア店')

print("韓国")
insert_votes(2, '韓国料理スランジェ 新宿')
insert_votes(1, '韓花')
insert_votes(1, '焼肉・韓国料理 KollaBo 新宿南口店')

print("イタリアン")
insert_votes(4, 'PIZZERIA CAPOLI')
insert_votes(2, 'ビラビアンキ 新宿店')
insert_votes(2, '太陽のトマト麺NEXT 新宿ミロード店')
insert_votes(2, 'Pizzeria＆Bar イタリアン チェルト！ 新宿南口店')

print("和食")
insert_votes(3, '隠れ房 御庭')
insert_votes(2, 'KICHIRI 新宿')
insert_votes(2, '黒毛和牛 腰塚')
insert_votes(2, '大かまど飯　寅福 ルミネ新宿店')
insert_votes(2, '個室風流 七色てまりうた 新宿')

print("カフェ")
insert_votes(2, 'マンゴツリーカフェ ルミネ新宿')
insert_votes(2, 'アマティ ルミネ１ルミネ新宿店')
insert_votes(2, 'サラベス ルミネ新宿店')
insert_votes(2, 'ラ・メゾン アンソレイユターブル ルミネ新宿店')
insert_votes(2, 'HAND BAKES ルミネ新宿店')
insert_votes(2, '京はやしや')
insert_votes(2, 'アフタヌーンティー・ラブアンドテーブル ルミネ新宿店')
insert_votes(2, 'モアナキッチンカフェ 新宿タカシマヤタイムズスクエア店')

print("居酒屋")
insert_votes(2, '地酒と創作和食 九平次 新宿店')
insert_votes(2, '居酒屋かあさん 新宿南口店')
insert_votes(2, 'KICHIRI 新宿')
insert_votes(2, '地産地鶏専門店 茂松 新宿南口店')
insert_votes(2, '三代目 鳥メロ 新宿南口店')

print("その他")
insert_votes(2, 'J．S． BURGERS CAFE／ J．S． BEER GARDEN')
insert_votes(2, '九州料理と完全個室 美味か 新宿店')
insert_votes(2, 'とんかつ とん匠')
insert_votes(2, '名代とんかつ かつくら 新宿高島屋店')
insert_votes(2, '築地玉寿司 新宿高島屋店')

conn.commit() # Save (commit) the changes
cur.close()
conn.close()
