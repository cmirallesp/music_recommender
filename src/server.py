#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from recommender_system import RecommenderSystem
import json
import pdb
import tornado.ioloop
import tornado.web
import tornado.httpserver

from tornado.options import define, options

define("port", default=8887, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, recommender_system):
        self.rs = recommender_system

    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header("Content-type", "application/json")

    def get(self):
        lst = list(self.rs.artists_names_iter())[:10]
        print lst
        self.write(json.dumps(lst))

    def post(self):
        # pdb.set_trace()
        data = tornado.escape.json_decode(self.request.body)

        self.write(json.dumps("OK"))

    def options(self):
        # no body
        self.set_status(200)
        self.finish()


def make_app():
    rs = RecommenderSystem(calc_similarities=False)
    return tornado.web.Application([
        (r"/artists", MainHandler, dict(recommender_system=rs)),
        (r"/user", MainHandler, dict(recommender_system=rs))
    ])


if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
