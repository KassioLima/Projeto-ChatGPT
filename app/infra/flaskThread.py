from threading import Thread
from flask import Flask

class FlaskThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        Flask(__name__).run(host='0.0.0.0', port=8081)