#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from recommender_system import RecommenderSystem
import json
import pdb
import tornado.ioloop
import tornado.web

import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, recommender_system):
        self.rs = recommender_system

    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        lst = list(self.rs.artists_names_iter())[:10]
        print lst
        self.write(json.dumps(lst))


def make_app():
    return tornado.web.Application([
        (r"/artists", MainHandler, dict(recommender_system=RecommenderSystem.instance())),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8887)
    tornado.ioloop.IOLoop.current().start()
