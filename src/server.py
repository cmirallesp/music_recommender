#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from recommender_system import RecommenderSystem
import json
import pdb
import tornado.ioloop
import tornado.web
import tornado.httpserver
import time
from tornado.options import define, options

define("port", default=8887, help="run on the given port", type=int)


class NewUserHandler(tornado.web.RequestHandler):

    def initialize(self, recommender_system, ):
        print "NewUserHandler"
        self.rs = recommender_system

    def set_default_headers(self):
        print "setting headers 2222!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header("Content-type", "application/json")

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        uid = self.rs.new_user(data['user_name'])
        m = {"user_id": uid, "artists": list(self.rs.artists_names_iter())[:10]}
        self.write(json.dumps(m))

    def options(self):
        # no body
        print "optionsss1"
        self.set_status(204)
        print "optionsss2"
        self.finish()
        print "optionsss3"


class SaveArtistsHandler(tornado.web.RequestHandler):

    def initialize(self, recommender_system, ):
        print "SaveArtist"
        self.rs = recommender_system

    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header("Content-type", "application/json")

    def post(self):
        # pdb.set_trace()
        data = tornado.escape.json_decode(self.request.body)
        print "=======>{}".format(data)
        print "adding user, recalculating similarities"
        st = time.clock()
        self.rs.add_artists_and_friends_to_user(data['user_id'], listens=data['selected'], friends={})
        print "user added ({})".format(time.clock() - st)
        self.write(json.dumps("OK"))

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


def make_app():
    rs = RecommenderSystem()
    data = {"user_id": 1}
    return tornado.web.Application([
        (r"/user", NewUserHandler, dict(recommender_system=rs)),
        (r"/user_artists", SaveArtistsHandler, dict(recommender_system=rs))
    ])


if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
