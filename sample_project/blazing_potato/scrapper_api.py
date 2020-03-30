from flask import request, jsonify
from flask import current_app as app
from flask.views import MethodView
from werkzeug.exceptions import abort
import cache
from errors import *
import json
import misc
import scrapper
import sys
import requests


class ScrapperAPI(MethodView):
    def __init__(self,):
        self.scrapper = scrapper.get_scrapper()

    def push_to_cache_server(self, url: str, value: dict):
        url_to_post = self.retrieve_cache_post_url(url)
        print("posting to", url_to_post, "with", value)
        post_data = {}
        post_data["key"] = url
        post_data["value"] = value
        res = requests.post(url_to_post, json = post_data)
        if res.status_code != 200:
            sys.stderr.write("failed to save to remote cache server" + res.text + "\n")
        print("saved to remote", res)

    def retrieve_cache_post_url(self, url: str) -> str:
        url = "{server_url}/{endpoint}".format(
                server_url = app.config['CACHE_SERVER_URL_FULL'],
                endpoint = "save",
            )
        return url


    def retrieve_cache_get_url(self, url: str) -> str:
        url = "{server_url}/{endpoint}?{param_name}={param_value}".\
            format(
                server_url = app.config['CACHE_SERVER_URL_FULL'],
                endpoint = "get",
                param_name = "url",
                param_value = url
            )
        return url


    def search_cache_server(self, url: str):
        url = self.retrieve_cache_get_url(url)
        res = requests.get(url)
        print("remote responded", res, type(res))
        return res.status_code, res.text


    def get_cache(self, url: str):
        search_return_code, search_result = self.search_cache_server(url)
        if search_return_code != 200:
            return {}
        res_dict = json.loads(search_result)
        return res_dict

    def post(self):
        #try:

        req_data = request.get_json()
        url = req_data.get("url", "")
        ids = req_data.get("ids", "")

        #check if remote has cache
        res = self.get_cache(url)
        if res:
            #has cache, directly serve the cache
            return (misc.format_result("", res), 200)

        dict_res = self.scrapper.scrap(url, ids)

        if not dict_res:
            return (misc.format_result("url not scrappable", None), 400)

        self.push_to_cache_server(url, dict_res)

        return (misc.format_result("", dict_res), 200)

        #except Exception as e:
        #    sys.stderr.write("error:\n")
        #    return (misc.format_result(str(e), None), 500)


