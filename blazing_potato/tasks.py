from flask import request, jsonify
from flask.views import MethodView
from werkzeug.exceptions import abort
from scrap_cacher import cache
from errors import *
import json


class TasksAPI(MethodView):
    def format_result(self, err, value):
        res = {"errors":err, "result" : value}
        return json.dumps(res)

    def post(self):
        """
        there should be two field called "key" and "value" in json
        """
        req_data = request.get_json()
        try:
            key = req_data.get("key", "")
            value = req_data.get("value", "")
            cacher = cache.get_cacher()
            cacher.save(key, value)

            return (self.format_result("", "saved"), 200)
        except Exception:
            abort("Unknown Error", 501)

    def get(self, key: str):
        try:
            res = cache.get_cacher().get(key)
            return (self.format_result("", res), 200)
        except Exception:
            abort(501)
