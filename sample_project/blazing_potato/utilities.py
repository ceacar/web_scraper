
from flask import request, jsonify
from flask.views import MethodView
from werkzeug.exceptions import abort
import json


class StatusAPI(MethodView):
    def get(self):
        res = {"errors":"", "result" : "healthy"}
        return (json.dumps(res), 200)


class ShutdownAPI(MethodView):
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def post(self):
        self.shutdown_server()
        return 'Server shutting down...',200

