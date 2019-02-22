from flask import request, jsonify
from flask.views import MethodView
from werkzeug.exceptions import abort
import json


class StatusAPI(MethodView):
    """
    end point for serving status of server such as health
    """
    def get(self):
        res = {"errors":"", "result" : "healthy"}
        return (json.dumps(res), 200)
