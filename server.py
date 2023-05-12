# server img2img api
# server handle order and notify processor to draw image

# api_url: localhost:5000

# api

# handle
# handle img2img order, return query url
# using query url to query result
# route:/handle, method:POST
# payload:{
#     "init_image": "knlgnpfpnsp",(base64)
# }
# response: {
#     "query_url": "api_url/query/order_id"
# }

# query
# query txt2img result, return processed image url
# route:/query/<order_id>, method:GET
# response:{
#     "processed": "https://s3.amazonaws.com/processed/order_id.png"
# }

# handle do
# 1. create order_id (uuid)
# 2. save init_image (base64) as local file (png)
# 3. save order_id to db (postgresql)
# 4. send order_id to raw_cache (redis)
# 5  generate query_qrcode for query_url
# 6. return query_qrcode (base64)

# query do
# 1. get order_id from query_url
# 2. query order_id from db
# 3. get image_url from db, if not exist, return None
# 4. return image_url

# database postgresql
# table: orders
# columns: order_id, processed, status
# order_id is primary key
# processed: url
# status: 0: is raw, 1: processed

# cache redis
# pubsub channel: "raw_cache"
# message: order_id

from io import BytesIO
from flask import Flask, request
import uuid
import base64
import qrcode
from tools import get_redis_connection,get_postgresql_connection, get_image_path, config,from_url_get_host_and_port

app = Flask(__name__)


@app.route('/handle', methods=['POST'])
def handle():
    init_image = request.json['init_image']
    order_id = create_order_id()
    image_path = get_image_path(order_id)
    save_image_from_base64(init_image, image_path)
    save_order_id_to_db(order_id)
    send_order_id_to_raw_cache(order_id)
    query_url = create_query_url(order_id)
    # generate query_qrcode
    # query_qrcode = generate_query_qrcode(query_url)
    # query_qrcode = qrcode_to_base64(query_qrcode)
    # return {'query_url': query_url, 'query_qrcode': query_qrcode}
    return {'query_url': query_url}


@app.route('/query/<order_id>', methods=['GET'])
def query(order_id):
    # query order_id from db
    status = get_status(order_id)
    if status == 0:
        return {'processed': None}
    elif status == 1:
        image_url = get_processed(order_id)
        return {'processed': image_url}


def get_status(order_id):
    conn = get_postgresql_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
    status = cur.fetchone()[0]
    cur.close()
    conn.close()
    return status


def get_processed(order_id):
    conn = get_postgresql_connection()
    cur = conn.cursor()
    cur.execute("SELECT processed FROM orders WHERE order_id = %s", (order_id,))
    processed = cur.fetchone()[0]
    cur.close()
    conn.close()
    return processed


def create_order_id():
    return str(uuid.uuid4())


def save_image_from_base64(image_base64, image_path):
    with open(image_path, 'wb') as f:
        # convert base64 to binary
        f.write(base64.b64decode(image_base64))


def save_order_id_to_db(order_id):
    conn = get_postgresql_connection()
    cur = conn.cursor()
    processed = ""
    # 0: is raw, 1: processed
    status = 0
    cur.execute("INSERT INTO orders (order_id, processed, status) VALUES (%s, %s, %s)",
                (order_id, processed, status))
    conn.commit()
    cur.close()
    conn.close()


def send_order_id_to_raw_cache(order_id):
    r = get_redis_connection()
    r.publish(config["redis_raw_cache"], order_id)


def create_query_url(order_id):
    return f'{config["api_url"]}/query/{order_id}'


def generate_query_qrcode(query_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(query_url)
    image = qr.make_image()
    return image


def qrcode_to_base64(qrcode):
    buffered = BytesIO()
    qrcode.save(buffered, format="PNG")
    image_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return image_str


def run():
    host,port=from_url_get_host_and_port(config['api_url'])
    app.run(host=host,
            port=port,
            debug=config['app_run_debug_mode'])


if __name__ == "__main__":
    run()
