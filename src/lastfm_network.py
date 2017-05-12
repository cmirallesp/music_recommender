import networkx as nx
import pdb


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
        raise False

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
