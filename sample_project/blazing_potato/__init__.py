import os
from flask import Flask
import cache_api
import status
import os
import redis
import errors
import scrapper_api

def test_redis_conn(redis_url, redis_port):
    rs = redis.StrictRedis(host = redis_url, port = redis_port)
    try:
        rs.ping()
    except ConnectionError as e:
        logger.error("Redis isn't running. try `make redis`")
        raise e

def create_app():
    app = Flask(__name__)

    #tasks_api = cache_api.CacheAPI.as_view("TasksAPI")
    #stats_api = status.StatusAPI.as_view("stats")
    scrap_api = scrapper_api.ScrapperAPI.as_view("scrapper")

    #app.add_url_rule("/get/<key>", view_func=tasks_api, methods=["GET"])
    #app.add_url_rule("/save", view_func=tasks_api, methods=["POST"])
    #app.add_url_rule("/health", view_func=stats_api, methods=["GET"])
    app.add_url_rule("/scrap", view_func=scrap_api, methods=["POST"])


    time_out = os.environ.get("TTL_TIMEOUT", "30")
    #redis_url = os.environ.get("redis_url", "0.0.0.0")
    #redis_port = os.environ.get("redis_port", "10000")

    #REDIS_URL = '{redis_url}:{redis_port}/0'.format(redis_url = redis_url, redis_port = redis_port)
    #app.config["REDIS_URL"] = redis_url
    #app.config["REDIS_PORT"] = redis_port
    app.config["TTL_TIMEOUT"] = time_out
    #test_redis_conn(redis_url, redis_port)

    cache_server_url = os.environ.get("CACHE_SERVER_URL", "http://localhost")
    cache_server_port = os.environ.get("CACHE_SERVER_PORT", "35555")
    app.config["CACHE_SERVER_URL_FULL"] = "{0}:{1}".format(cache_server_url, cache_server_port)

    return app

app = create_app()

@app.route("/")
def root():
    return ("Blazing Potato is up and running!",200)
