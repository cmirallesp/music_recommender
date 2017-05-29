
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
                norm_w = w / N
                self._graph[uid][f_id]['norm_weight'] = norm_w
                self._graph[uid][f_id]['walking_weight'] = norm_w * self.r

    def _normalize_weights_artist_user(self):
        # For each artist in the network normalizes their weights
        # with respect to their listeners
        for aid in self.artists_iter():
            sum_ = self.total_artist_users_weights(aid)
            for user_id in self.artist_users_iter(aid):
                weight = self.artist_user_weight(aid, user_id)
                norm_w = weight / sum_
                self._graph[aid][user_id]['norm_weight'] = norm_w
                self._graph[aid][user_id]['walking_weight'] = norm_w

    def _normalize_weights_user_artist(self):
        # For each user in the network normalizes their weights
        #  with respect to their artists
        for uid in self.users_iter():
            sum_ = self.total_user_artists_weights(uid)
            for artist_id in self.user_artists_iter(uid):
                weight = self.user_artist_weight(uid, artist_id)
                norm_w = weight / sum_
                self._graph[uid][artist_id]['norm_weight'] = norm_w
                self._graph[uid][artist_id]['walking_weight'] = norm_w * (1 - self.r)

    def _normalize_weights_artist_tag(self):
        # set the absoulte weight
        for aid in self.artists_iter():
            sum_ = self.total_artist_tags_weights(aid)
            for tag_id in self.artist_tags_iter(aid):
                weight = self.artist_tag_weight(aid, tag_id)
                norm_w = weight / sum_

                self._graph[aid][tag_id]['norm_weight'] = norm_w
                self._graph[aid][tag_id]['walking_weight'] = norm_w

    def _normalize_weights_tag_artist(self):
        # set the absolute weight
        for tid in self.tags_iter():
            sum_ = self.total_tag_artists_weights(tid)
            for aid in self.tag_artists_iter(tid):
                weight = self.tag_artist_weight(tid, aid)
                norm_w = weight / sum_
                self._graph[tid][aid]['norm_weight'] = norm_w
                self._graph[tid][aid]['walking_weight'] = norm_w

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
        start = time.clock()
        tags_artists = user_taggedartists.groupby(['tagID', 'artistID']).groups

        for (tag, artist) in tags_artists:

            kt = self.key_tag(tag)
            self._graph.add_node(kt)

            if artist not in self.artists_id:
                info("Artist not found:{}".format(artist))
                continue

            weight = len(tags_artists[(tag, artist)])

            ka = self.key_artist(artist)
            self._graph.add_edge(kt, ka, weight=weight, type='ta')
            self._graph.add_edge(ka, kt, weight=weight, type='at')

        info("network processed in t:{}".format(time.clock() - start))
