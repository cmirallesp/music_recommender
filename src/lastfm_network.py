import logging
from logging import info
from sets import Set
import numpy as np
import networkx as nx
import time
import matplotlib.pyplot as plt
import pandas as pd
import pdb


class LastfmNetwork(object):
    """docstring for LastfmNetwork"""
    @classmethod
    def instance(cls):
        return cls(
            artists=pd.read_table('../data/artists.dat'),
            tags=pd.read_table('../data/tags.dat'),
            user_friends=pd.read_table('../data/user_friends.dat'),
            user_artists=pd.read_table('../data/user_artists.dat'),
            user_taggedartists=pd.read_table('../data/user_taggedartists.dat')
        )

    def __init__(self, artists, tags,
                 user_friends, user_artists, user_taggedartists):
        super(LastfmNetwork, self).__init__()
        logging.basicConfig(filename='logging.log',
                            level=logging.DEBUG,
                            format=('%(asctime)-15s'
                                    '%(funcName)s %(message)s'))

        # multilayer graph to hold the entire data
        self._graph = nx.Graph(directed=False)

        self.artists_id = Set([aid for aid in artists['id']])
        self.users_id = np.unique(user_friends['userID'].as_matrix())
        self.tags_id = Set([tid for tid in tags['tagID']])

        self._build_user_friends(user_friends)
        self._build_user_artists(user_artists)
        self._build_user_tag_artists(user_taggedartists)
        # nx.write_pajek(self._graph, "network.net")

        # print self._graph.size()
    def network(self):
        return self._graph

    def key_user(self, id):
        return "u_{}".format(id)

    def key_artist(self, id):
        return "a_{}".format(id)

    def key_tag(self, id):
        return "t_{}".format(id)

    def _build_user_friends(self, user_friends):
        for uid, fid in user_friends.values:
            if uid not in self.users_id:
                info("User not found: {}".format(uid))
                continue
            if fid not in self.users_id:
                info("User friend not found: {}".format(uid))
                continue

            k = self.key_user(uid)
            k2 = self.key_user(fid)

            self._graph.add_edge(k, k2, type='uu')

    def _build_user_artists(self, user_artists):
        for uid, aid, weight in user_artists.values:
            if uid not in self.users_id:
                info("User not found: {}".format(uid))
                continue

            if aid not in self.artists_id:
                info("Artist not found:{}".format(aid))
                continue

            ku = self.key_user(uid)
            ka = self.key_artist(aid)

            self._graph.add_edge(ku, ka, weight=weight, type='ua')

    # def _build_user_taggedartists(self, user_taggedartists):
    #     tags = user_taggedartists.tagID.unique()

    #     for tag in tags:
    #         print "processing tag:{}/{}".format(tag, len(tags))
    #         # Obtain subtables of artists that share the same tag
    #         subtable = user_taggedartists.loc[user_taggedartists['tagID'] == tag]
    #         for _, aid1, _, _, _, _ in subtable.values:
    #             for _, aid2, _, _, _, _ in subtable.values:
    #                 if aid1 != aid2:
    #                     k = self.key_artist(aid1)
    #                     k2 = self.key_artist(aid2)

    #                     if self._graph.has_edge(k, k2):
    #                         self._graph[k][k2]['weight'] += 1
    #                     else:
    #                         self._graph.add_edge(k, k2, weight=1)

    def _build_user_tag_artists(self, user_taggedartists):
        tags = user_taggedartists.groupby('tagID').groups
        start = time.clock()
        for tag in tags:
            kt = self.key_tag(tag)
            self._graph.add_node(kt)
            uta_rows = tags[tag]

            artists = user_taggedartists.iloc[uta_rows]['artistID']

            for aid in artists:
                if aid not in self.artists_id:
                    info("Artist not found:{}".format(aid))
                    continue

                ka = self.key_artist(aid)
                self._graph.add_edge(kt, ka, type='ta')
        info("network processed in t:{}".format(time.clock() - start))

    def friends(self, user_id1, user_id2):
        info("friends")
        return self._graph.has_edge(
            self.key_user(user_id1),
            self.key_user(user_id2)
        )

    def times_user_listen_artist(self, user_id, artist_id):
        # returns the weight between user_id and artists id
        info("times_user_listen_artist")
        ku = self.key_user(user_id)
        ka = self.key_artist(artist_id)
        try:
            result = self._graph[ku][ka]

        except Exception:
            result = None

        return result['weight']

    def artists_iter(self):
        for id1 in self._graph.nodes_iter():
            if "a_" in id1:
                yield id1

    def tags_iter(self):
        for id1 in self._graph.nodes_iter():
            if "t_" in id1:
                yield id1

    def users_iter(self):
        for id1 in self._graph.nodes_iter():
            if "u_" in id1:
                yield id1

    def degree_artist_tag(self, artist_id):
        return self._degree(artist_id, "t_")

    def degree_artist_user(self, artist_id):
        return self._degree(artist_id, "u_")

    def degree_tag_tag(self, tag_id):
        return self._degree(tag_id, "t_")

    def degree_tag_artist(self, tag_id):
        return self._degree(tag_id, "a_")

    def degree_user_user(self, user_id):
        return self._degree(user_id, "u_")

    def degree_user_artist(self, user_id):
        return self._degree(user_id, "a_")

    def _degree(self, id1, prefix):
        degree = 0
        for id2 in self._graph.edge[id1]:
            if prefix in id2:
                degree += 1
        return degree

    def draw(self):
        print "=====>1"
        nx.draw(self._graph)
        print "=====>2"
        plt.show()
        # plt.save("plots/network.png")

    def artists_sharing_more_tags(self, artist_id):
        raise False
        # ka = self.key_artist(artist_id)
        # while True:
        #     # edges artist_id - user_id | tag_id
        #     for _, _id in self._graph.edges_iter(ka):
        #         ee = self._graph[ka][_id]
        #         if ee['type'] == 'ta':  # tag-artist edge
        #             tag_id = _id
        #             artists_of_tag = self._graph[tag_id].keys

        #             pdb.set_trace()
