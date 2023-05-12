# processor
# processor handle txt2img order, return query url

# run do
# 1. listen to raw_cache (redis)
# 2. call process

# process do
# 1. get all raw ids from db (postgresql)
# 3. get all raw images from local file (png)
# 3. send raw images to txt2img api (convert to base64)
# 4. save processed image url and update status to db (postgresql)
# 5. delete raw images from local file (png)
# 6. check if there is any raw ids left, if yes, go to step 1, if no, stop

import os
import base64
import requests
from tools import get_redis_connection, get_postgresql_connection, get_image_path, config


def run():
    raw_cache = get_redis_connection().pubsub()
    raw_cache.subscribe(config["redis_raw_cache"])
    print("listen to raw_cache")
    for _ in raw_cache.listen():
        print("start proccess, get message from raw_cache")
        proccess()
        print("end proccess, continue listen to raw_cache")
        print()


def proccess():
    raw_ids = get_raw_ids()
    for raw_id in raw_ids:
        print("proccess raw_id: ", raw_id)
        raw_image = get_raw_image(raw_id)
        raw_image_base64 = image_to_base64(raw_image)
        processed_image_url,error = img2img(raw_image_base64)
        print("processed_image_url: ", processed_image_url, "error: ", error)
        if error:
            print("fail to call img2img api error: ", error)
            print("continue without update db and delete raw image")
            continue
        update_processed_image_url_and_status(raw_id, processed_image_url)
        delete_raw_image(raw_id)


    if len(get_raw_ids()) > 0:
        proccess()

def get_raw_ids():
    conn = get_postgresql_connection()
    cur = conn.cursor()
    cur.execute("SELECT order_id FROM orders WHERE status = 0")
    raw_ids = cur.fetchall()
    cur.close()
    conn.close()
    # raw_ids = [
    #   ('ef8b0928-c57b-4b19-b2cc-935a9d33275b',),
    #   ('64f0b762-263d-4c31-879e-a058a315210d',)
    # ]
    # need to get the raw_id from the tuple
    raw_ids = [raw_id[0] for raw_id in raw_ids]
    return raw_ids


def get_raw_image(raw_id):
    # load image from local file
    image_path = get_image_path(raw_id)
    with open(image_path, 'rb') as f:
        raw_image = f.read()
    return raw_image


def image_to_base64(image):
    return base64.b64encode(image).decode('utf-8')


def img2img(raw_image_base64):
    payload = {
        'prompt':"",
        'init_images': [raw_image_base64]
    }
    response = requests.post(config["img2img_url"], json=payload)
    processed_image_url = response.text
    return processed_image_url, response.status_code!=200


def update_processed_image_url_and_status(raw_id, processed_image_url):
    conn = get_postgresql_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET processed = %s, status = 1 WHERE order_id = %s",
                (processed_image_url, raw_id))
    conn.commit()
    cur.close()
    conn.close()


def delete_raw_image(raw_id):
    image_path = get_image_path(raw_id)
    os.remove(image_path)

if __name__ == "__main__":
    run()