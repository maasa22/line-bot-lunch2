### csv to database
import psycopg2
import pandas as pd
import config
df = pd.read_csv("./restaurants_neighboring.csv")

user = config.user
password = config.password
host = config.host
port_db = config.port_db
database = config.database
conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS restaurants")
cur.execute('''CREATE TABLE restaurants
                (id text, name text, name_kana text, latitude numeric, longitude numeric, \
                category text, url text, url_mobile text, image_url text, address text, \
                pr text, code text)''')
for index, row in df.reset_index().iterrows():
    print(index)
    cur.execute("INSERT INTO restaurants VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(row["id"], row["name"], row["name_kana"], row["latitude"], row["longitude"], row["category"], row["url"], row["url_mobile"], row["image_url"].replace('\'', '"'), row["address"], row["pr"].replace('\'', '"'), row["code"].replace('\'', '"')))
conn.commit()
conn.close()
