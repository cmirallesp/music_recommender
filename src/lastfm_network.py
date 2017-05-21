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
        self._graph = nx.DiGraph()

        self.artists_id = Set([aid for aid in artists['id']])
        self.users_id = Set(np.unique(user_friends['userID'].as_matrix()))
        self.tags_id = Set([tid for tid in tags['tagID']])

        self._build_user_friends(user_friends)
        self._build_user_artists(user_artists)
        # self._build_user_tag_artists(user_taggedartists)
        self._normalize_weights_friendship()
        self._normalize_weights_my_artists()
        self._normalize_weights_my_listeners()
        # nx.write_pajek(self._graph, "network.net")

        # print self._graph.size()
    def network(self):
        return self._graph

    def key_user(self, _id):
        if isinstance(_id, str) and "u_" in _id:
            return _id
        else:
            return "u_{}".format(_id)

    def key_artist(self, _id):
        if isinstance(_id, str) and "a_" in _id:
            return _id
        else:
            return "a_{}".format(_id)

    def key_tag(self, _id):
        if isinstance(_id, str) and "t_" in str(_id):
            return _id
        else:
            return "t_{}".format(_id)

    def _normalize_weights_friendship(self):
        for uid in self.users_iter():
            friend_ids = list(self.my_friends_iter(uid))
            N = len(friend_ids) * 1.
            for f_id in friend_ids:
                self._graph[uid][f_id]['weight'] /= N

    def _normalize_weights_my_listeners(self):
        # For each artist in the network normlizes their weights
        # with respect to their listeners
        for aid in self.artists_iter():
            sum_ = self.total_my_listeners_weights(aid)
            for user_id in self.my_listeners_iter(aid):
                weight = self.au_weight(aid, user_id)
                self._graph[aid][user_id]['norm_weight'] = weight / sum_

    def _normalize_weights_my_artists(self):
        # For each user in the network normalizes their weights
        #  with respect to their artists
        for uid in self.users_iter():
            sum_ = self.total_my_artists_weights(uid)
            for artist_id in self.my_artists_iter(uid):
                weight = self.ua_weight(uid, artist_id)
                self._graph[uid][artist_id]['norm_weight'] = weight / sum_

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

            self._graph.add_edge(k, k2, weight=1., type='uu')

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
            self._graph.add_edge(ka, ku, weight=weight, type='au')

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

    def au_weight(self, artist_id, user_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_user(user_id)
        return self._edge_weight(id1, id2)

    def au_normalized_weight(self, artist_id, user_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_user(user_id)
        return self._edge_normalized_weight(id1, id2)

    def ua_weight(self, user_id, artist_id):
        id1 = self.key_user(user_id)
        id2 = self.key_artist(artist_id)
        return self._edge_weight(id1, id2)

    def ua_normalized_weight(self, user_id, artist_id):
        id1 = self.key_user(user_id)
        id2 = self.key_artist(artist_id)
        return self._edge_normalized_weight(id1, id2)

    def number_of_listeners(self, artist_id):
        return len(list(self.my_listeners_iter(self.key_artist(artist_id))))

    def total_my_artists_weights(self, user_id):
        sum_ = 0
        k_user_id = self.key_user(user_id)
        for artist_id in self.my_artists_iter(user_id):
            sum_ += self._edge_weight(k_user_id, artist_id)

        return sum_

    def total_my_listeners_weights(self, artist_id):
        sum_ = 0
        k_artist_id = self.key_artist(artist_id)
        for k_user_id in self.my_listeners_iter(artist_id):
            sum_ += self._edge_weight(k_artist_id, k_user_id)

        return sum_

    def friendship_weight(self, u1_id, u2_id):
        id1 = self.key_user(u1_id)
        id2 = self.key_user(u2_id)
        return self._edge_weight(id1, id2)

    def number_of_friends(self, user_id):
        return len(list(self.my_friends_iter(user_id)))

    def are_friends(self, user_id1, user_id2):

        return self._graph.has_edge(
            self.key_user(user_id1),
            self.key_user(user_id2)
        )

    def is_my_listener(self, artist_id, user_id):
        _uid = self.key_user(user_id)
        for uid in self.my_listeners_iter(artist_id):
            if _uid == uid:
                return True
        return False

    def is_my_artist(self, user_id, artist_id):

        _aid = self.key_artist(artist_id)
        for aid in self.my_artists_iter(user_id):
            if _aid == aid:
                return True
        return False

    def _edge_weight(self, id1, id2):
        if not self._graph.has_edge(id1, id2):
            return None
        else:
            return 1. * self._graph[id1][id2]['weight']

    def _edge_normalized_weight(self, id1, id2):
        if not self._graph.has_edge(id1, id2):
            return None
        else:
            return self._graph[id1][id2]['norm_weight']

    def _my_edges(self, node_id, prefix):
        # given a node_id in the network returns an iterator
        # of nodes connected to me with the passed prefix (=u_|a_|t_)

        if self._graph.has_node(node_id):
            for _id in self._graph.edge[node_id]:
                if prefix in _id:
                    yield _id

    def my_friends_iter(self, user_id):
        for friend_id in self._my_edges(self.key_user(user_id), "u_"):
            yield friend_id

        def artists_weight(self, user_id, artist_id):
            id1 = self.key_user(user_id)
            id2 = self.key_artist(artist_id)
            return self._edge_weight(id1, id2)

    def my_listeners_iter(self, artist_id):
        for user_id in self._my_edges(self.key_artist(artist_id), "u_"):
            yield user_id

    def my_artists_iter(self, user_id):
        for artist_id in self._my_edges(self.key_user(user_id), "a_"):
            yield artist_id

    def check_friendship(self):
        ok = True
        for uid_1 in self.users_iter():
            for uid_2 in self.my_friends_iter(uid_1):
                if not self._graph.has_edge(uid_2, uid_1):
                    info("{}-{} but not {}-{}".format(uid_1, uid_2,
                                                      uid_2, uid_1))
                    ok = False
        return ok

    def times_user_listen_artist(self, user_id, artist_id):
        # returns the weight between user_id and artists id
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

# DEGREES PER TYPE
    def degree_artist_tag(self, artist_id):
        return self._degree(artist_id, "t_")

    def degree_artist_user(self, artist_id):
        return self._degree(artist_id, "u_")

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
        nx.draw_random(self._graph)
        print "=====>2"
        # plt.show()
        plt.savefig("plots/network.png")
