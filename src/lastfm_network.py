# coding: utf-8
from network_builder_mixin import NetworkBuilderMixin
from network_iterators_mixin import NetworkIteratorsMixin
import logging
from logging import info

import numpy as np
import networkx as nx

import matplotlib.pyplot as plt
import pandas as pd
import cPickle as pickle

import os.path


class LastfmNetwork(NetworkBuilderMixin, NetworkIteratorsMixin, object):
    """docstring for LastfmNetwork"""
    
    @property
    def user_similarities(self):
        if self._user_similarities is None:
            self._user_similarities = pickle.load(open("user_sim.pickle", "rb"))
        return self._user_similarities

    @property
    def artist_similarities_tags(self):
        if self._artist_similarities_tags is None:
            self._artist_similarities_tags = pickle.load(open("artist_sim_tags.pickle", "rb"))
        return self._artist_similarities_tags

    def load_data(self):
        artists=pd.read_table('../data/artists.dat')
        tags=pd.read_table('../data/tags.dat')
        user_friends=pd.read_table('../data/user_friends.dat')
        user_artists=pd.read_table('../data/user_artists.dat')
        user_taggedartists=pd.read_table('../data/user_taggedartists.dat')
        return artists, tags, user_friends, user_artists, user_taggedartists

    def __init__(self, preprocessing=True, minFreqTag=0):
        super(LastfmNetwork, self).__init__()
        logging.basicConfig(filename='logging.log',
                            level=logging.WARNING,
                            format=('%(asctime)-15s'
                                    '%(funcName)s %(message)s'))
        
        artists, tags, user_friends, user_artists, user_taggedartists = self.load_data()
        if preprocessing:
            artists, tags, user_taggedartists = self.dataPreprocessing(artists, tags, user_taggedartists, minFreqTag)

        self.run = 'online'  # Online by default; when evaluating, it changes to 'offline'
        self.r = 0.1
        
        self._artists_tags = self._tags_artists = None
        self._artists_users = self._users_artists = None
        self._users_users = None

        self.artists_id = [aid for aid in artists['id']]
        self.users_id = list(np.unique(user_friends['userID'].as_matrix()))
        self.tags_id = [tid for tid in tags['tagID']]

        self.artistID2artist = {self.key_artist(self.artists_id[idx]): name for idx, name in enumerate(artists['name'])}

        self._artists_tags = None
        self._user_similarities = None
        self._artist_similarities_tags = None
        if os.path.isfile('network.pickle'):
            self._graph = nx.read_gpickle("network.pickle")

        else:
            # multilayer graph to hold the entire data
            self._graph = nx.DiGraph()

            self._build_user_friends(user_friends)
            self._build_user_artists(user_artists)
            self._build_user_tag_artists(user_taggedartists)

            self._normalize_weights_user_user()
            self._normalize_weights_user_artist()
            self._normalize_weights_artist_user()
            self._normalize_weights_artist_tag()
            self._normalize_weights_tag_artist()

            nx.nx.write_gpickle(self._graph, "network.pickle")
            # nx.write_pajek(self._graph, "network.net")

            self._calculate_user_similarities()
            self._calculate_artist_similarities_over_tags()
            pickle.dump(self._user_similarities, open("user_sim.pickle", "wb"))
            pickle.dump(self._artist_similarities_tags, open("artist_sim_tags.pickle", "wb"))

        # print self._graph.size()
        # nx.write_pajek(self._graph, "network.net")
        # print self._graph.size()

    def dataPreprocessing(self, artists, tags, user_taggedartists, minFreqTag=0):
        # There are artistIDs that appear at user_taggedartists but not in artists;
        # we detect and remove these unknown artistIDs from user_taggedartists
        knownArtists = pd.Series(artists.id.values, index=artists.id).to_dict()
        user_taggedartists['artistID'] = user_taggedartists['artistID'].apply(lambda x: self.detectUnknownArtists(x, knownArtists))
        user_taggedartists = user_taggedartists[user_taggedartists.artistID != -1]

        # remove rows whose tag year is smaller than 2000 (outliers?)
        user_taggedartists = user_taggedartists[user_taggedartists['year'] >= 2000]

        # tag preprocessing, removing whitespaces and symbols
        tags['tagValue'] = tags['tagValue'].map(lambda x: self.tagPreprocessing(x))

        # group the tagIDs of the tags that ended up being the same into a single tagID
        # we create a dictionary that performs this mapping
        dictionaryTagIDs = {}
        for indices in tags.groupby(['tagValue']).groups.values():
            for idx in indices:
                dictionaryTagIDs[tags['tagID'][idx]] = tags['tagID'][indices[0]]
        # apply the dictionary to user_taggedartists
        user_taggedartists['tagID'] = user_taggedartists['tagID'].apply(lambda x: self.applyDictionaryTagIDs(x, dictionaryTagIDs))
        # use the dictionary to avoid redundancy in tags
        tags = tags[tags['tagID'].isin(dictionaryTagIDs.values())]
        
        # As data cleaning, we only keep those tags whose frequency is greater than minFreqTag
        freqTags = user_taggedartists['tagID'].value_counts()
        user_taggedartists = user_taggedartists[user_taggedartists['tagID'].isin(freqTags[freqTags>minFreqTag].keys())]
        tags = tags[tags['tagID'].isin(freqTags[freqTags>minFreqTag].keys())]
        
        return artists, tags, user_taggedartists

    def tagPreprocessing(self, tag):
        # write every tag in lower case
        tag = tag.lower()
        # remove punctuation marks, symbols, whitespaces
        punct_to_remove = list(' #%&\*+/<=>-\\^{|}~()[]:;\'`¡.,¿?!')  # + ['\r', '\n', '\t']
        for ch in punct_to_remove:
            tag = tag.replace(ch, '')
        return tag

    def applyDictionaryTagIDs(self, tagID, dictionarytagIDs):
        try:
            return dictionarytagIDs[tagID]
        except Exception:
            return tagID

    def detectUnknownArtists(self, artistID, knownArtists):
        try:
            return knownArtists[artistID]
        except Exception:
            return -1

    def network(self):
        return self._graph

    def network_as_undirected(self, net=None):
        if net is None:
            return nx.Graph(self._graph, directed=False)
        else:
            return nx.Graph(net, directed=False)

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

    def artist_user_weight(self, artist_id, user_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_user(user_id)
        return self._edge_weight(id1, id2)

    def artist_user_normalized_weight(self, artist_id, user_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_user(user_id)
        return self._edge_normalized_weight(id1, id2)

    def artist_user_walking_weight(self, artist_id, user_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_user(user_id)
        return self._edge_walking_weight(id1, id2)

    def user_artist_weight(self, user_id, artist_id):
        id1 = self.key_user(user_id)
        id2 = self.key_artist(artist_id)
        return self._edge_weight(id1, id2)

    def artist_tag_weight(self, artist_id, tag_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_tag(tag_id)
        return self._edge_weight(id1, id2)

    def tag_artist_weight(self, tag_id, artist_id):
        id1 = self.key_tag(tag_id)
        id2 = self.key_artist(artist_id)
        return self._edge_weight(id1, id2)

    def artist_tag_normalized_weight(self, artist_id, tag_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_tag(tag_id)
        return self._edge_normalized_weight(id1, id2)

    def artist_tag_walking_weight(self, artist_id, tag_id):
        id1 = self.key_artist(artist_id)
        id2 = self.key_tag(tag_id)
        return self._edge_walking_weight(id1, id2)

    def tag_artist_normalized_weight(self, tag_id, artist_id):
        id1 = self.key_tag(tag_id)
        id2 = self.key_artist(artist_id)
        return self._edge_normalized_weight(id1, id2)

    def tag_artist_walking_weight(self, tag_id, artist_id):
        id1 = self.key_tag(tag_id)
        id2 = self.key_artist(artist_id)
        return self._edge_walking_weight(id1, id2)

    def user_artist_normalized_weight(self, user_id, artist_id):
        id1 = self.key_user(user_id)
        id2 = self.key_artist(artist_id)
        return self._edge_normalized_weight(id1, id2)

    def user_artist_walking_weight(self, user_id, artist_id):
        id1 = self.key_user(user_id)
        id2 = self.key_artist(artist_id)
        return self._edge_walking_weight(id1, id2)

    def number_of_listeners(self, artist_id):
        return len(list(self.artist_users_iter(self.key_artist(artist_id))))

    def total_user_artists_weights(self, user_id):
        sum_ = 0
        k_user_id = self.key_user(user_id)
        for artist_id in self.user_artists_iter(user_id):
            sum_ += self._edge_weight(k_user_id, artist_id)

        return sum_

    def total_artist_users_weights(self, artist_id):
        sum_ = 0
        k_artist_id = self.key_artist(artist_id)
        for k_user_id in self.artist_users_iter(artist_id):
            sum_ += self._edge_weight(k_artist_id, k_user_id)

        return sum_

    def total_artist_tags_weights(self, artist_id):
        sum_ = 0
        k_artist_id = self.key_artist(artist_id)
        for tags_id in self.artist_tags_iter(artist_id):
            sum_ += self._edge_weight(k_artist_id, tags_id)

        return sum_

    def total_tag_artists_weights(self, tag_id):
        sum_ = 0
        k_tag_id = self.key_tag(tag_id)
        for artist_id in self.tag_artists_iter(tag_id):
            sum_ += self._edge_weight(k_tag_id, artist_id)

        return sum_

    def user_user_weight(self, u1_id, u2_id):
        id1 = self.key_user(u1_id)
        id2 = self.key_user(u2_id)
        return self._edge_weight(id1, id2)

    def user_user_normalized_weight(self, u1_id, u2_id):
        id1 = self.key_user(u1_id)
        id2 = self.key_user(u2_id)
        return self._edge_normalized_weight(id1, id2)

    def user_user_walking_weight(self, u1_id, u2_id):
        id1 = self.key_user(u1_id)
        id2 = self.key_user(u2_id)
        return self._edge_walking_weight(id1, id2)

    def number_of_friends(self, user_id):
        return len(list(self.user_user_iter(user_id)))

    def are_friends(self, user_id1, user_id2):

        return self._graph.has_edge(
            self.key_user(user_id1),
            self.key_user(user_id2)
        )

    def is_my_listener(self, artist_id, user_id):
        _uid = self.key_user(user_id)
        for uid in self.artist_users_iter(artist_id):
            if _uid == uid:
                return True
        return False

    def is_my_artist(self, user_id, artist_id):
        _aid = self.key_artist(artist_id)
        for aid in self.user_artists_iter(user_id):
            if _aid == aid:
                return True
        return False

    def is_my_tag(self, artist_id, tag_id):
        _tid = self.key_tag(tag_id)

        for tid in self.artist_tags_iter(artist_id):
            if _tid == tid:
                return True
        return False

    def is_my_artist_2(self, tag_id, artist_id):
        _aid = self.key_artist(artist_id)
        for aid in self.tag_artists_iter(tag_id):
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

    def _edge_walking_weight(self, id1, id2):
        if not self._graph.has_edge(id1, id2):
            return None
        else:
            return self._graph[id1][id2]['walking_weight']

    def times_user_listen_artist(self, user_id, artist_id):
        # returns the weight between user_id and artists id
        ku = self.key_user(user_id)
        ka = self.key_artist(artist_id)
        try:
            result = self._graph[ku][ka]

        except Exception:
            result = None

        return result['weight']


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

    def disconnected_tags(self):
        result = []
        for tid in self.tags_iter():
            if nx.degree(self._graph, tid) == 0:
                result.append(tid)
        return result

    def disconnected_artists(self):
        result = []
        for aid in self.artists_iter():
            if nx.degree(self._graph, aid) == 0:
                result.append(aid)
        return result

    def disconnected_users(self):
        result = []
        for uid in self.users_iter():
            if nx.degree(self._graph, uid) == 0:
                result.append(uid)
        return result

    def draw(self):
        print "=====>1"
        nx.draw_random(self._graph)
        print "=====>2"
        # plt.show()
        plt.savefig("plots/network.png")
