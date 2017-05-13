import networkx as nx
import pandas as pd
import numpy as np
import pdb
import os.path
import os
import time


class LastfmNetwork(object):
    """docstring for LastfmNetwork"""

    def __init__(self, user_friends, user_artists, user_taggedartists):
        super(LastfmNetwork, self).__init__()
        # multilayer graph to hold the entire data
        self._graph = nx.Graph(directed=False)
        if os.path.isfile("network.net"):
            self._graph = nx.Graph(nx.read_pajek("network.net"))
        else:
            self._build_user_friends(user_friends)
            self._build_user_artists(user_artists)
            self._build_user_taggedartists(user_taggedartists)
            nx.write_pajek(self._graph, "network.net")

        print self._graph.size()

    def key_user(self, id):
        return "u_{}".format(id)

    def key_artist(self, id):
        return "a_{}".format(id)

    def _build_user_friends(self, user_friends):
        processed = {}
        for uid, fid in user_friends.values:
            k = self.key_user(uid)
            k2 = self.key_user(fid)

            if k not in processed:
                self._graph.add_node(k, type="user")
                processed[k] = k

            if k2 not in processed:
                self._graph.add_node(k2, type="user")
                processed[k2] = k2

            self._graph.add_edge(k, k2)

    def _build_user_artists(self, user_artists):
        processed = {}
        for uid, aid, weight in user_artists.values:
            ku = self.key_user(uid)
            ka = self.key_artist(aid)

            if ka not in processed:
                self._graph.add_node(ka, type="artist")
                v2 = self._graph.node[ka]

                processed[ka] = v2

            self._graph.add_edge(ku, ka, weight=weight)

    def _build_user_taggedartists(self, user_taggedartists):
        processed = {}
        tags = user_taggedartists.groupby('tagID').groups
        n_tags = len(tags)
        for tag in tags:
            artists = tags[tag]
            n = len(artists)
            print("processing tag {}/{}"
                  "n_artists {} n_artists^2:{}"
                  ).format(tag, n_tags, n, n**2)
            start = time.clock()
            for i in range(0, len(artists)):
                for j in range(i + 1, len(artists)):
                    k = self.key_artist(artists[i])
                    k2 = self.key_artist(artists[j])
                    both = "{}{}".format(k, k2)
                    if both in processed:
                        # if self._graph.has_edge(k, k2):
                        self._graph[k][k2]['weight'] += 1
                    else:
                        processed[both] = 1
                        self._graph.add_edge(k, k2, weight=1)

            print "processed t: {}".format(time.clock() - start)

    def friends(self, user_id1, user_id2):
        return self._graph.has_edge(
            self.key_user(user_id1),
            self.key_user(user_id2)
        )

    def times_user_listen_artist(self, user_id, artist_id):
        # returns the weight between user_id and artists id
        ku = self.key_user(user_id)
        ka = self.key_artist(artist_id)
        try:
            result = self._graph[ku][ka]

        except Exception:
            result = None

        return result['weight']
