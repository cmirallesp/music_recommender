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

    def initialize(self, recommender_system, ds):
        print "====>{}".format(ds)
        self.rs = recommender_system
        self.ds = ds

    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header("Content-type", "application/json")

    def get(self):
        m = {"user_id": "##u_{}##".format(self.ds['user_id']), "artists": list(self.rs.artists_names_iter())[:10]}
        self.ds['user_id'] += 1
        print m
        self.write(json.dumps(m))

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
    data = {"user_id": 1}
    return tornado.web.Application([
        (r"/artists", MainHandler, dict(recommender_system=rs, ds=data)),
        (r"/user", MainHandler, dict(recommender_system=rs, ds=data))
    ])


if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
