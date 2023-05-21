import json
import psycopg2
import redis

with open('config.json') as f:
    config = json.load(f)


def get_redis_connection():
    return redis.Redis(host=config["redis_host"], port=6379, db=0)


def get_postgresql_connection():
    return psycopg2.connect(dbname=config["dbname"], user=config["dbuser"],
                            password=config["dbpass"], host=config["dbhost"],port=config["dbport"])


def get_image_path(raw_id):
    return f'{config["raw_images_folder"]}/{raw_id}.png'


def from_url_get_host_and_port(url):
    url = url.split('//')[1]
    host = url.split(':')[0]
    port = url.split(':')[1]
    return host, port
