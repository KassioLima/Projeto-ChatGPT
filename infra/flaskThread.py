from threading import Thread
from flask import Flask

class FlaskThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        app = Flask(__name__)

        @app.route('/')
        def hello_world():
            return 'CHatGPT Telegram Bot is running!!'

        app.run(host='0.0.0.0', port=8081)