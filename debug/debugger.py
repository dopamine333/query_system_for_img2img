import base64
import os
import random
import sys
from PIL import Image
from io import BytesIO
import psycopg2
import redis
import requests
config = {
    "api_url":"http://127.0.0.1:5000",
    "img2img_url":"https://ai.jd-chie.store/discord_draw_img2img",

    "app_run_debug_mode":True,

    "raw_images_folder":"./raw_images",

    "dbname":"postgres",
    "dbuser":"postgres",
    "dbpass":"mysecretpassword",
    "dbhost":"localhost",

    "redis_host":"localhost",
    "redis_raw_cache":"raw_cache"

}

def get_redis_connection():
    return redis.Redis(host=config["redis_host"], port=6379, db=0)


def get_postgresql_connection():
    return psycopg2.connect(dbname=config["dbname"], user=config["dbuser"],
                            password=config["dbpass"], host=config["dbhost"])


def see_db():
    conn = get_postgresql_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close()
    conn.close()
    print("select all orders in database")
    print("orders num: ", len(orders))
    # CREATE TABLE orders (order_id VARCHAR PRIMARY KEY, processed VARCHAR, status INTEGER)
    for order in orders:
        print(f"order_id: {order[0]}, processed: {order[1]}, status: {order[2]}")
    
    return orders

def see_redis():
    channel = get_redis_connection().pubsub()
    channel.subscribe("raw_cache")
    print("listen raw_cache pubsub in redis")
    for message in channel.listen():
        print(message)

def utf8len(s):
    return len(s.encode('utf-8'))
# call handle api
# 1. open local image file
# 2. convert image to base64
# 3. send base64 to api
# 4. get response
# 5. get query url from response
# 6. print query url
def call_handle_api():
    # 1. open local image file

    # folder : test_images/
    # random select one image
    # using os.listdir() to get all images
    # using random.choice() to select one image
    # print(os.listdir("test_images"))
    listdir = os.listdir("test_images")
    # remove .DS_Store
    if ".DS_Store" in listdir:
        listdir.remove(".DS_Store")

    if len(listdir) == 0:
        print("no image in test_images folder")
        return

    image_path = f'test_images/{random.choice(listdir)}'
    
    # request entity too large
    # image_path = "/test_images/圖片已上傳至：2023-5-3 14-18.png"
    # len image base64:  2499452
    # image_path="/test_images/8f207c80-56f3-4740-b14c-9a19bf3a928f.png"
    # len image base64:  624288
    

    print("init image: ", image_path)
    with open(image_path, "rb") as f:
        image = f.read()
    # show image
    Image.open(image_path).show()

    # 2. convert image to base64
    image_base64 = base64.b64encode(image).decode("utf-8")

    print("len image base64: ", utf8len(image_base64))
    # 3. send base64 to api
    # api url: http://localhost:5000/handle
    # api method: POST
    # payload:{
    #     "init_image": "knlgnpfp...nsp",(base64)
    # }
    # response: {
    #     "query_url": "api_url/query/order_id"
    # }
    payload = {
        "init_image": image_base64
    }
    # 4. get response
    response = requests.post("http://127.0.0.1:5000/handle", json=payload)
    # print error if response status code is not 200
    if response.status_code != 200:
        print("error handle, response.text: ", response.text)
        return 
    
    # 5. get query url from response
    query_url = response.json()["query_url"]

    # 6. print query url
    print("query_url: ", query_url)

# call query api
# query
# query txt2img result, return processed image url
# route:/query/<order_id>, method:GET
# response:{
#     "processed": "https://s3.amazonaws.com/processed/order_id.png"
# }
def call_query_api(query_url):
    # show processed image,request the url, and show the image

    print("query_url: ", query_url)
    query_response = requests.get(query_url)

    image_url = query_response.json()["processed"]
    if image_url is None:
        print("query fail, the order is not processed")
        return
    print("image_url: ", image_url)
    image_response = requests.get(image_url)
    Image.open(BytesIO(image_response.content)).show()

def clear_db():
    conn = get_postgresql_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders")
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # call sys.argv[1] function
    if len(sys.argv) > 1:
        # string to function
        if sys.argv[1] == "call_query_api":
            call_query_api(sys.argv[2])
        else:
            func = globals()[sys.argv[1]]
            # print("func: ", func)
            func()
    else:
        print("no function call, please input function name")
