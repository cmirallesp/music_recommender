class NetworkIteratorsMixin(object):
    """docstring for NetworkIteratorsMixin"""

    def user_user_iter(self, user_id):
        for friend_id in self._my_edges(self.key_user(user_id), "u_"):
            yield friend_id

    def artist_users_iter(self, artist_id):
        for user_id in self._my_edges(self.key_artist(artist_id), "u_"):
            yield user_id

    def user_artists_iter(self, user_id):
        for artist_id in self._my_edges(self.key_user(user_id), "a_"):
            yield artist_id

    def tag_artists_iter(self, tag_id):
        for artist_id in self._my_edges(self.key_tag(tag_id), 'a_'):
            yield artist_id

    def artist_tags_iter(self, artist_id):
        for tag_id in self._my_edges(self.key_artist(artist_id), 't_'):
            yield tag_id

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

    def artist_user_normalized_weights_iter(self, artist_id):
        for uid in self.artist_users_iter(artist_id):
            yield self.artist_user_normalized_weight(artist_id, uid)

    def user_artist_normalized_weights_iter(self, user_id):
        for aid in self.user_artists_iter(user_id):
            yield self.user_artist_normalized_weight(user_id, aid)

    def artist_tags_normalized_weights_iter(self, tag_id):
        for aid in self.artist_tags_iter(tag_id):
            yield self.artist_tag_normalized_weight(tag_id, aid)

    def tags_artists_normalized_weights_iter(self, tag_id):
        for aid in self.tag_artists_iter(tag_id):
            yield self.tag_artist_normalized_weight(tag_id, aid)

    def user_user_normalized_weights_iter(self, user_id):
        for fid in self.user_user_iter(user_id):
            yield self.user_user_normalized_weight(user_id, fid)

    def artist_user_walking_weights_iter(self, artist_id):
        for uid in self.artist_users_iter(artist_id):
            yield self.artist_user_walking_weight(artist_id, uid)

    def user_artist_walking_weights_iter(self, user_id):
        for aid in self.user_artists_iter(user_id):
            yield self.user_artist_walking_weight(user_id, aid)

    def artist_tags_walking_weights_iter(self, tag_id):
        for aid in self.artist_tags_iter(tag_id):
            yield self.artist_tag_walking_weight(tag_id, aid)

    def tags_artists_walking_weights_iter(self, tag_id):
        for aid in self.tag_artists_iter(tag_id):
            yield self.tag_artist_walking_weight(tag_id, aid)

    def user_user_walking_weights_iter(self, user_id):
        for fid in self.user_user_iter(user_id):
            yield self.user_user_walking_weight(user_id, fid)

    def _my_edges(self, node_id, prefix):
        # given a node_id in the network returns an iterator
        # of nodes connected to me with the passed prefix (=u_|a_|t_)
        if self._graph.has_node(node_id):
            for _id in self._graph.edge[node_id]:
                if prefix in _id:
                    yield _id
