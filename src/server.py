#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from recommender_system import RecommenderSystem
import json

import tornado.ioloop
import tornado.web
import tornado.httpserver
import time
from tornado.options import define, options

define("port", default=8887, help="run on the given port", type=int)


def sort(iterator, g):
    r = []
    if id:
        for t in iterator:
            r.append({
                "id": t['id'],
                "full_name": t['full_name'],
                "n": g.degree(t['id'])
            })

    return sorted(r, key=lambda s: s["n"], reverse=True)


class TagsHandler(tornado.web.RequestHandler):

    def initialize(self, recommender_system, ):
        self.rs = recommender_system

    def set_default_headers(self):
        print "setting headers 2222!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header("Content-type", "application/json")

    def get(self):
        tags = sort(self.rs.tags_names_iter(), self.rs._graph)
        self.write(json.dumps(tags))

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


class RecommendationHandler(tornado.web.RequestHandler):

    def initialize(self, recommender_system, ):
        self.rs = recommender_system

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header("Content-type", "application/json")

    def get(self, tag_id):
        artists = self.rs.tag_artists_iter(tag_id)
        artists = sort(self.rs.artists_names_iter(artists), self.rs._graph)
        # artists = list(self.rs.artists_names_iter(artists))
        self.write(json.dumps(artists))

    def post(self):
        # pdb.set_trace()
        data = tornado.escape.json_decode(self.request.body)

        # uid = str(data['user_id'])  # comes in unicode
        uid = self.rs.new_user("")

        self.rs.add_artists_and_friends_to_user(uid, listens=data['selected'])

        # recommendation

        recommendationLst = self.rs.recommendation(uid, artistSim=data['kindOfSim'])

        result = []

        for aid, sim in recommendationLst:
            result.append(
                {'full_name': self.rs.artistID2artist[aid].decode('utf8'), 'score': str(round(sim, 5)).rjust(7)}
            )

        self.write(json.dumps(result))
        # undo changes
        self.rs.remove_artists_and_friends_from_user(uid, data['selected'])

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


def make_app():
    rs = RecommenderSystem()

    return tornado.web.Application([
        (r"/tags", TagsHandler, dict(recommender_system=rs)),
        (r"/artists/(t_\d+)", RecommendationHandler, dict(recommender_system=rs)),
        (r"/recommendation", RecommendationHandler, dict(recommender_system=rs)),
    ], autoreload=True, debug=True)


if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
