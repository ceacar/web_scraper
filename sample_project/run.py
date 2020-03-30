#!/usr/bin/env python3
from blazing_potato import app as application
import os
ip = os.environ.get("SERVER_IP", "0.0.0.0")
port = os.environ.get("PORT", 8000)

if __name__ == "__main__":
    application.run(host = ip, port = port)
