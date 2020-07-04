# coding: utf-8
from flask import Flask, request, abort
import numpy as np
import pandas as pd
# import sqlite3
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FollowEvent,UnfollowEvent,CarouselTemplate, CarouselColumn,URIAction,PostbackAction,MessageAction,TemplateSendMessage,ConfirmTemplate,PostbackEvent,StickerMessage, StickerSendMessage, LocationMessage,LocationSendMessage,ImageMessage, VideoMessage, AudioMessage, FileMessage, QuickReply, QuickReplyButton,DatetimePickerAction, LocationAction, ButtonsTemplate, CameraAction, CameraRollAction
)
import os
import random
import csv
import json
import sys
from json.decoder import JSONDecodeError
import psycopg2

class Restaurant:
    def __init__(self,id,name,name_kana,latitude,longitude,category,url,url_mobile,image_url,address,pr,code,user_distance,category2):
        self.id = id
        self.name = name
        self.name_kana = name_kana
        self.latitude = latitude
        self.longitude = longitude
        self.category = category
        self.url = url
        self.url_mobile = url_mobile
        self.image_url = image_url
        self.address = address
        self.pr = pr
        self.code = code
        self.user_distance=user_distance
        self.category2 = category2


# 東京周辺では緯度1度で110kmくらい、経度1度で90kmくらいなので、そう仮定して簡略的に計算する。
def calc_distance(x, latitude_base, longitude_base):
    return np.sqrt(((x.latitude - latitude_base)*110*1000)**2 + ((x.longitude - longitude_base)*90*1000)**2)

# 和、韓国、中華、イタリアン、カフェ、居酒屋（、他）に分類する。
def add_category2(x):
    if "韓国" in x: #韓国料理
        return "Korean"
    elif "中華" in x:
        return "Chinese"
    elif "イタリアン" in x:
        return "Italian"
    elif "カフェ" in x:
        return "Cafe"
    elif ("居酒屋" in x ) or ("バー" in x):
        return "Izakaya"
    elif "和" in x: #和食
        return "Japanese"
    else: #ほか
        return "others"

restaurant_categories = ["和食", "韓国料理", "中華", "イタリアン", "カフェ", "居酒屋", "ほか"]
img_restaurant_default = "https://curry-jinbo-linebot.an.r.appspot.com/static/restaurants_default" #何もurlなかった時用のデフォルト画像。
# img_restaurant_default = "https://portfolio-masaki.appspot.com/_nuxt/img/bdede36.png"


# set environment variables
# variables about python
port_flask = int(os.getenv("PORT")) #ここでエラーがでたらlocalと判定するw
# variables about line bot
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
# variables about db
TEST_USER_ID_AOS = os.environ["TEST_UESR_ID_AOS"]
user = os.environ["user"]
password = os.environ["password"]
host = os.environ["host"]
port_db = os.environ["port_db"]
database = os.environ["database"]
# https://developers.line.biz/の設定, https://curry-jinbo-linebot.an.r.appspot.com/callback

conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
cur = conn.cursor()
df_restaurant = pd.read_sql("SELECT * FROM restaurants", con=conn)
conn.commit()
cur.close()
conn.close()

# get restaurants data from csv
df_restaurant["user_distance"]=1000 #デフォルト値を設定して、user_distanceカラムを追加。
df_restaurant["category2"] = df_restaurant["category"].apply(add_category2) # category2カラムを追加。

# get a list of Restaurant objects
restaurants = []
for record in json.loads(df_restaurant.to_json(orient="records")):
    restaurants.append(Restaurant(**record))

# get a list of restaurant names
restaurant_names = []
restaurant_names = df_restaurant["name"].values.tolist()

# ----- main -----
app = Flask(__name__)
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
insert_initial_data(conn, TEST_USER_ID_AOS)
conn.close()
# ----- main -----

@app.route("/")
def hello_world():
    return "hello world!"

from flask import send_from_directory
@app.route("/static/<filename>")
def default_image(filename):
    # filename = "restaurants_default.png"をアップロードするためのもの。
    return send_from_directory("./static", filename)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# テキストメッセージを処理するもの。
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_msg = event.message.text
    # ランダム : ランダムに1店舗紹介する。
    # テキストで返して、その後に2通目のメッセージで詳細を見ますか？でyesならリッチメッセージを送る仕掛け欲しい。postbackactionじゃな。
    # if input_msg in ["ランダム", "random"]:
    #     output_msg = random.choice(restaurant_names)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=output_msg))
    # ちかく：近くのおすすめ店舗を紹介する。
    if input_msg in ["近くのお店", "ちかく", "近く", "near"]:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='位置情報から近くの店を検索する',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=LocationAction(label="位置情報の画面へ")
                        ),
                    ])))
    elif input_msg in ["お気に入りからランダム", "ランダム"]:
        conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
        cur = conn.cursor()
        df = pd.read_sql("SELECT favorite_restaurant_name FROM favorite_restaurants WHERE user_id = '{}'".format(event.source.user_id), con=conn)
        favorite_restaurant_names = list(df.favorite_restaurant_name.values)
        conn.commit()
        cur.close()
        conn.close()
        num_lists = range(len(favorite_restaurant_names))
        if len(num_lists) > 10:
            favorite_restaurant_nums = random.sample(num_lists, k=6) #仕様上10個まで。
        else:
            favorite_restaurant_nums = random.sample(num_lists, k=len(num_lists))

        favorite_restaurants = []
        for favorite_restaurant_num in favorite_restaurant_nums:
            for restaurant in restaurants:
                if favorite_restaurant_names[favorite_restaurant_num] == restaurant.name:
                    favorite_restaurants.append(restaurant)

        favorite_carousel_columns=[]
        for favorite_restaurant in favorite_restaurants:
            if json.loads(favorite_restaurant.image_url.replace('\'', '"'))["shop_image1"] != "":
                        image_url = json.loads(favorite_restaurant.image_url.replace('\'', '"'))["shop_image1"]
            else:
                image_url = img_restaurant_default
            try :
                if json.loads(favorite_restaurant.pr.replace('\'', '"'))["pr_short"] != "":
                    pr = json.loads(favorite_restaurant.pr.replace('\'', '"'))["pr_short"][:60]
                else:
                    pr = "おすすめのお店です"
            except JSONDecodeError:
                    pr = "おすすめのお店です"

            favorite_carousel_column = CarouselColumn(
                                thumbnail_image_url=image_url,
                                title=favorite_restaurant.name,
                                text=pr,
                                actions=[
                                    URIAction(
                                        label='ぐるなびへ',
                                        uri=favorite_restaurant.url_mobile
                                    ),
                                    MessageAction(
                                        label='位置情報をみる',
                                        text='位置情報 '+favorite_restaurant.name
                                    ),
                                    MessageAction(
                                        label="お気に入りから削除する",
                                        text="お気に入り削除"+' '+favorite_restaurant.name
                                    ) # event.source.user_id
                                ]
                            )
            favorite_carousel_columns.append(favorite_carousel_column)
        if len(favorite_carousel_columns) > 0:
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns=favorite_carousel_columns
                    )
                )
            )
        else:
            output_msg = "まだお気に入りがありません。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=output_msg))

    elif input_msg in ["お気に入り一覧", "一覧"]:
        conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
        cur = conn.cursor()
        df = pd.read_sql("SELECT favorite_restaurant_name FROM favorite_restaurants WHERE user_id = '{}'".format(event.source.user_id), con=conn)
        print(df)
        favorite_restaurant_names = list(df.favorite_restaurant_name.values)
        conn.commit()
        cur.close()
        conn.close()
        if len(favorite_restaurant_names) > 0:
            output_msg = ""
            for favorite_restaurant_name in favorite_restaurant_names:
                output_msg += "•" + favorite_restaurant_name + "\n"
            output_msg = output_msg[:-1]
        else:
            output_msg = "まだお気に入りがありません。"
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=output_msg))

    elif input_msg in ["ランキング"]:
        conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
        cur = conn.cursor()
        df = pd.read_sql("SELECT count(*) as favorites, favorite_restaurant_name FROM favorite_restaurants GROUP BY favorite_restaurant_name", con=conn)
        df = df.sort_values('favorites', ascending=False)
        restaurant_names = df["favorite_restaurant_name"].values.tolist()
        conn.commit()
        cur.close()
        conn.close()

        if len(restaurant_names) > 10:
            restaurant_names = restaurant_names[:10]

        ranking_restaurants = []
        for restaurant_name in restaurant_names:
            for restaurant in restaurants:
                if restaurant.name == restaurant_name:
                    ranking_restaurants.append(restaurant)

        ranking_carousel_columns=[]
        for i in range(len(ranking_restaurants)):
        # for ranking_restaurant in ranking_restaurants:
            if json.loads(ranking_restaurants[i].image_url.replace('\'', '"'))["shop_image1"] != "":
                image_url = json.loads(ranking_restaurants[i].image_url.replace('\'', '"'))["shop_image1"]
            else:
                image_url = img_restaurant_default
            try :
                if json.loads(ranking_restaurants[i].pr.replace('\'', '"'))["pr_short"] != "":
                    pr = str(i+1) + "位: " + json.loads(ranking_restaurants[i].pr.replace('\'', '"'))["pr_short"][:50]
                else:
                    pr = str(i+1) + "位: " + "おすすめのお店です"
            except JSONDecodeError:
                    pr = str(i+1) + "位: " + "おすすめのお店です"

            conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
            cur = conn.cursor()
            cur.execute("SELECT FROM favorite_restaurants WHERE user_id = '{}' and favorite_restaurant_name = '{}';".format(event.source.user_id, ranking_restaurants[i].name))
            if cur.fetchone() is None:
                label_favorite = "お気に入りに追加する"
                text_favorite = "お気に入り追加"
            else: # もうお気に入りされている。
                label_favorite = "お気に入りから削除する"
                text_favorite = "お気に入り削除"
            conn.commit()
            cur.close()
            conn.close()

            ranking_carousel_column = CarouselColumn(
                                thumbnail_image_url=image_url,
                                title=ranking_restaurants[i].name,
                                text=pr,
                                actions=[
                                    URIAction(
                                        label='ぐるなびへ',
                                        uri=ranking_restaurants[i].url_mobile
                                    ),
                                    MessageAction(
                                        label='位置情報をみる',
                                        text='位置情報 '+ranking_restaurants[i].name
                                    ),
                                    MessageAction(
                                        label=label_favorite,
                                        text=text_favorite+' '+ranking_restaurants[i].name
                                    ) # event.source.user_id
                                ]
                            )
            ranking_carousel_columns.append(ranking_carousel_column)
        if len(ranking_carousel_columns) > 0:
            line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns=ranking_carousel_columns
                    )
                )
            )

    elif input_msg in ["ジャンル別"]:
        quickreply_items = []
        for category in restaurant_categories:
            item = QuickReplyButton(
                action=MessageAction(label=category, text=category+"のランキング")
            )
            quickreply_items.append(item)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='ジャンルを選んで下さい。',
                quick_reply=QuickReply(
                    items=quickreply_items)))
    elif "ランキング" in input_msg: # ジャンル別ランキング
        for category in restaurant_categories:
            if category in input_msg:
                # DBからそのジャンルのfavoritesランキングを抽出する。
                conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
                cur = conn.cursor()
                df_favorites = pd.read_sql("SELECT count(*) as favorites, favorite_restaurant_name FROM favorite_restaurants GROUP BY favorite_restaurant_name", con=conn)
                df_favorites = df_favorites.rename(columns={'favorite_restaurant_name': 'name'})
                df_restaurant2 = df_restaurant.copy(deep=False)
                df_favorites_ranking = pd.merge(df_restaurant2, df_favorites, on='name', how='outer')
                df_favorites_ranking = df_favorites_ranking[["name", "favorites", "category2", "image_url", "url", "url_mobile", "pr"]]
                dict_category = {"和食": "Japanese", "韓国料理": "Korean", "中華": "Chinese", "イタリアン":"Italian", "カフェ":"Cafe", "居酒屋":"Izakaya", "ほか":"others"}
                df_favorites_ranking = df_favorites_ranking[df_favorites_ranking["category2"] == dict_category[category]]
                df_favorites_ranking = df_favorites_ranking.sort_values("favorites", ascending = False)
                if len(df_favorites_ranking) > 10:
                    df_favorites_ranking = df_favorites_ranking[:9]
                recommend_carousel_columns = []
                for index, row in df_favorites_ranking.reset_index().iterrows():
                    print(index, row["name"], row.favorites)
                    if json.loads(row.image_url.replace('\'', '"'))["shop_image1"] != "":
                        image_url = json.loads(row.image_url.replace('\'', '"'))["shop_image1"]
                    else:
                        # image_url = "https://i.picsum.photos/id/10/200/300.jpg"
                        image_url = img_restaurant_default
                    try :
                        if json.loads(row.pr.replace('\'', '"'))["pr_short"] != "":
                            pr = str(index+1) + "位: " + json.loads(row.pr.replace('\'', '"'))["pr_short"][:40] # 60文字までという制限がある。オーバーの時は"..."を表示する。
                        else:
                            pr = str(index+1) + "位: " + "おすすめのお店です" # もう少し、良いメッセージにする。
                    except JSONDecodeError:
                            pr = str(index+1) + "位: " + "おすすめのお店です"

                    cur.execute("SELECT FROM favorite_restaurants WHERE user_id = '{}' and favorite_restaurant_name = '{}';".format(event.source.user_id, row["name"]))
                    if cur.fetchone() is None:
                        label_favorite = "お気に入りに追加する"
                        text_favorite = "お気に入り追加"
                    else: # もうお気に入りされている。 # is not None
                        label_favorite = "お気に入りから削除する"
                        text_favorite = "お気に入り削除"
                    recommend_carousel_column = CarouselColumn(
                                thumbnail_image_url=image_url,
                                title=row["name"],
                                text=pr,
                                actions=[
                                    URIAction(
                                        label='ぐるなびへ',
                                        uri=row.url_mobile
                                    ),
                                    MessageAction(
                                        label='位置情報をみる',
                                        text='位置情報 '+row["name"]
                                    ),
                                    MessageAction(
                                        label=label_favorite,
                                        text=text_favorite+' '+row["name"]
                                    ) # event.source.user_id
                                ]
                            )
                    recommend_carousel_columns.append(recommend_carousel_column)
                conn.commit()
                cur.close()
                conn.close()
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text='Carousel template',
                        template=CarouselTemplate(
                            columns=recommend_carousel_columns
                            )
                        )
                    )


    # おすすめ : カルーセルで数店舗紹介する。仕様上10店舗まで。
    elif input_msg in ["あなたへのおすすめ", "おすすめのお店", "おすすめ", "オススメ", "recommendation", "r", "re"]: #一旦動く。

        # recommend logic（ランダム）
        recommend_carousel_columns = []
        # recommend_restaurant_nums = [10,0,11,12]
        recommend_restaurant_nums = [14,15,16,17,18,19]

        # num_lists = range(0, len(restaurant_names))
        # recommend_restaurant_nums = random.choices(num_lists, k=6) #仕様上10個まで。それ以上は、moreにすると良さそう。
        conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
        # conn = sqlite3.connect('restaurants.db')
        cur = conn.cursor()
        for i in recommend_restaurant_nums:
            if json.loads(restaurants[i].image_url.replace('\'', '"'))["shop_image1"] != "":
                image_url = json.loads(restaurants[i].image_url.replace('\'', '"'))["shop_image1"]
            else:
                # image_url = "https://i.picsum.photos/id/10/200/300.jpg"
                image_url = img_restaurant_default
            try :
                if json.loads(restaurants[i].pr.replace('\'', '"'))["pr_short"] != "":
                    pr = json.loads(restaurants[i].pr.replace('\'', '"'))["pr_short"][:60] # 60文字までという制限がある。オーバーの時は"..."を表示する。
                else:
                    pr = "おすすめのお店です" # もう少し、良いメッセージにする。
            except JSONDecodeError:
                    pr = "おすすめのお店です"

            cur.execute("SELECT FROM favorite_restaurants WHERE user_id = '{}' and favorite_restaurant_name = '{}';".format(event.source.user_id, restaurants[i].name))
            if cur.fetchone() is None:
                label_favorite = "お気に入りに追加する"
                text_favorite = "お気に入り追加"
            else: # もうお気に入りされている。 # is not None
                label_favorite = "お気に入りから削除する"
                text_favorite = "お気に入り削除"

            recommend_carousel_column = CarouselColumn(
                                thumbnail_image_url=image_url,
                                title=restaurants[i].name,
                                text=pr,
                                actions=[
                                    URIAction(
                                        label='ぐるなびへ',
                                        uri=restaurants[i].url_mobile
                                    ),
                                    MessageAction(
                                        label='位置情報をみる',
                                        text='位置情報 '+restaurants[i].name
                                    ),
                                    MessageAction(
                                        label=label_favorite,
                                        text=text_favorite+' '+restaurants[i].name
                                    ) # event.source.user_id
                                ]
                            )
            recommend_carousel_columns.append(recommend_carousel_column)
        conn.commit()
        cur.close()
        conn.close()
        line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=recommend_carousel_columns
                )
            )
        )
    # 位置情報へを押された場合、"位置情報 (レストラン名)"とメッセージをトーク画面に返して、同時にそれをinputとして読み取って位置情報を返す。
    elif "位置情報" in input_msg:
        for restaurant in restaurants:
            if restaurant.name in input_msg:
                line_bot_api.reply_message(
                event.reply_token,
                LocationSendMessage(
                title=restaurant.name,
                address=restaurant.address,
                latitude=restaurant.latitude,
                longitude=restaurant.longitude
            )
        )
    # お気に入りに追加するを押された場合、"お気に入り追加 (レストラン名)"とメッセージをトーク画面に返して、同時にそれをinputとして読み取って位置情報を返す。
    elif "お気に入り追加" in input_msg:
        for restaurant in restaurants: # splitして、[command, name]もあり。
            if restaurant.name in input_msg:
                conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
                cur = conn.cursor()
                cur.execute("INSERT INTO favorite_restaurants(user_id,favorite_restaurant_name) \
                SELECT '{}', '{}' \
                WHERE NOT EXISTS(SELECT 1 FROM favorite_restaurants WHERE user_id = '{}' AND favorite_restaurant_name = '{}')".format(event.source.user_id, restaurant.name,event.source.user_id, restaurant.name))
                conn.commit()
                cur.close()
                conn.close()
    elif "お気に入り削除" in input_msg:
        for restaurant in restaurants:
            if restaurant.name in input_msg:
                conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
                cur = conn.cursor()
                cur.execute("DELETE FROM favorite_restaurants \
                WHERE user_id = '{}' AND favorite_restaurant_name = '{}'" \
                .format(event.source.user_id, restaurant.name))
                conn.commit()
                cur.close()
                conn.close()
    else:
        output_msg = "知ってる言葉は\nちかく、ランダム、一覧、ランキング、ジャンル別、おすすめ。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=output_msg))

# 位置情報メッセージを処理するもの。
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 近くの店を検索して返信する。
    latitude_user = event.message.latitude
    longitude_user = event.message.longitude
    df_restaurant_with_distance = df_restaurant.copy(deep=False)
    df_restaurant_with_distance["user_distance"] = df_restaurant_with_distance.apply(calc_distance, axis=1, latitude_base=latitude_user, longitude_base=longitude_user)
    df_restaurant_with_distance = df_restaurant_with_distance.sort_values('user_distance', ascending=True)[:10] #上位10件もあれば十分。

    restaurants_user = []
    for record in json.loads(df_restaurant_with_distance.to_json(orient="records")):
        restaurants_user.append(Restaurant(**record))

    neighborhood_carousel_columns = []
    for i in range(5):
        if json.loads(restaurants_user[i].image_url.replace('\'', '"'))["shop_image1"] != "":
            image_url = json.loads(restaurants_user[i].image_url.replace('\'', '"'))["shop_image1"]
        else:
            image_url = img_restaurant_default
        try :
            if json.loads(restaurants_user[i].pr.replace('\'', '"'))["pr_short"] != "":
                pr = json.loads(restaurants_user[i].pr.replace('\'', '"'))["pr_short"][:40] + "..." +  str('{:.0f}'.format(restaurants_user[i].user_distance)) + "m"
            else:
                pr = "おすすめのお店です" + "..." +  str('{:.0f}'.format(restaurants_user[i].user_distance)) + "m"
        except JSONDecodeError:
                pr = "おすすめのお店です" + str('{:.0f}'.format(restaurants_user[i].user_distance)) + "m"

        conn = psycopg2.connect("postgresql://{}:{}@{}:{}/{}".format(user, password, host, port_db, database))
        cur = conn.cursor()
        cur.execute("SELECT FROM favorite_restaurants WHERE user_id = '{}' and favorite_restaurant_name = '{}';".format(event.source.user_id, restaurants_user[i].name))
        if cur.fetchone() is None:
            label_favorite = "お気に入りに追加する"
            text_favorite = "お気に入り追加"
        else: # もうお気に入りされている。
            label_favorite = "お気に入りから削除する"
            text_favorite = "お気に入り削除"
        conn.commit()
        cur.close()
        conn.close()

        neighborhood_carousel_column = CarouselColumn(
                            thumbnail_image_url=image_url,
                            title=restaurants_user[i].name,
                            text=pr,
                            actions=[
                                URIAction(
                                    label='ぐるなびへ',
                                    uri=restaurants_user[i].url_mobile
                                ),
                                MessageAction(
                                    label='位置情報をみる',
                                    text='位置情報 '+restaurants_user[i].name
                                ),
                                MessageAction(
                                        label=label_favorite,
                                        text=text_favorite+' '+restaurants_user[i].name
                                    )
                            ]
                        )
        neighborhood_carousel_columns.append(neighborhood_carousel_column)

    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=neighborhood_carousel_columns
            )
        )
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_flask)
