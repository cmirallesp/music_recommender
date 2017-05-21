
from logging import info
import time


class NetworkBuilderMixin(object):
    # This Mixin class contains all the methods to build
    # the multilayer network:
    #  tag, artists and user nodes
    #  tag-artist, artist-tag, artist-user, user-artist and user-user edges
    #  weights in edges

    def _normalize_weights_user_user(self):
        for uid in self.users_iter():
            friend_ids = list(self.user_user_iter(uid))
            N = len(friend_ids)
            for f_id in friend_ids:
                w = self.user_user_weight(uid, f_id)
                self._graph[uid][f_id]['norm_weight'] = w / N

    def _normalize_weights_artist_user(self):
        # For each artist in the network normlizes their weights
        # with respect to their listeners
        for aid in self.artists_iter():
            sum_ = self.total_artist_users_weights(aid)
            for user_id in self.artist_users_iter(aid):
                weight = self.artist_user_weight(aid, user_id)
                self._graph[aid][user_id]['norm_weight'] = weight / sum_

    def _normalize_weights_user_artist(self):
        # For each user in the network normalizes their weights
        #  with respect to their artists
        for uid in self.users_iter():
            sum_ = self.total_user_artists_weights(uid)
            for artist_id in self.user_artists_iter(uid):
                weight = self.user_artist_weight(uid, artist_id)
                self._graph[uid][artist_id]['norm_weight'] = weight / sum_

    def _normalize_weights_artist_tag(self):
        # set the absoulte weight
        for aid in self.artists_iter():
            for tag_id in self.artist_tags_iter(aid):
                n_artists = len(list(self.tag_artists_iter(tag_id)))
                # the weight of an edge artist-tag is the
                #  number of artists associated to the tag
                self._graph[aid][tag_id]['weight'] = n_artists
        # normalized weight
        for aid in self.artists_iter():
            sum_ = self.total_artist_tags_weights(aid)
            for tag_id in self.artist_tags_iter(aid):
                self._graph[aid][tag_id]['norm_weight'] = (
                    self._graph[aid][tag_id]['weight'] / sum_
                )

    def _normalize_weights_tag_artist(self):
        # set the absoulte weight
        for tid in self.tags_iter():
            for aid in self.tag_artists_iter(tid):
                listened = self.total_artist_users_weights(aid)
                self._graph[tid][aid]['weight'] = listened
        for tid in self.tags_iter():
            sum_ = self.total_tag_artists_weights(tid)
            for aid in self.tag_artists_iter(tid):
                self._graph[tid][aid]['norm_weight'] = (
                    self._graph[tid][aid]['weight'] / sum_
                )

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
                self._graph.add_edge(ka, kt, type='at')
        info("network processed in t:{}".format(time.clock() - start))
