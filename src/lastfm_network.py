import networkx as nx

import os.path
import os


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
            # Sort user_taggedartists by tagID to accelerate edges creation
            user_taggedartists = user_taggedartists.sort_values('tagID')
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
        tags = user_taggedartists.tagID.unique()

        for tag in tags:
            print "processing tag:{}/{}".format(tag, len(tags))
            # Obtain subtables of artists that share the same tag
            subtable = user_taggedartists.loc[user_taggedartists['tagID'] == tag]
            for _, aid1, _, _, _, _ in subtable.values:
                for _, aid2, _, _, _, _ in subtable.values:
                    if aid1 != aid2:
                        k = self.key_artist(aid1)
                        k2 = self.key_artist(aid2)

                        if self._graph.has_edge(k, k2):
                            self._graph[k][k2]['weight'] += 1
                        else:
                            self._graph.add_edge(k, k2, weight=1)

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
