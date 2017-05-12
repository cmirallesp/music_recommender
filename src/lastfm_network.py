import networkx as nx


class LastfmNetwork(object):
    """docstring for LastfmNetwork"""

    def __init__(self, user_friends, user_artists, user_taggedartists):
        super(LastfmNetwork, self).__init__()
        # multilayer graph to hold the entire data
        self._graph = nx.Graph(directed=False)
        self._build_user_friends(user_friends)
        self._build_user_artists(user_artists)
        # self._build_user_taggedartists(user_taggedartists)

    def key_user(self, id):
        return "u_{}".format(id)

    def key_artist(self, id):
        return "l_{}".format(id)

    def _build_user_friends(self, user_friends):
        added = {}
        for uid, fid in user_friends.values:
            k = self.key_user(uid)
            k2 = self.key_user(fid)

            if k in added:
                v1 = added[k]
            else:
                self._graph.add_node(k, type="user")
                v1 = self._graph.node[k]

                added[k] = v1

            if k2 in added:
                v2 = added[k2]
            else:
                self._graph.add_node(k2, type="user")
                v2 = self._graph.node[k2]

                added[k2] = v2

            self._graph.add_edge(k, k2)

    def _build_user_artists(self, user_artists):
        raise False

    def _build_user_taggedartists(self, user_taggedartists):
        raise False

    def friends(self, user_id1, user_id2):
        return self._graph.has_edge(
            self.key_user(user_id1),
            self.key_user(user_id2)
        )

    def times_user_listened_artist(self, user_id, artist_id):
        # returns the weight between user_id and artists id
        raise False
