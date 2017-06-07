import numpy as np
import scipy as sp
from logging import info
import time
import networkx as nx


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

    def _calculate_user_similarities(self):
        data = []
        rows = []
        cols = []
        for i, u1 in enumerate(self.users_id):
            for j, u2 in enumerate(self.users_id):
                if j > i:
                    break
                elif j == i:
                    data.append(1)
                    rows.append(i)
                    cols.append(j)
                else:
                    s = self._sim(u1, u2, self.user_artists_iter)
                    if s > 0:
                        data.append(s)
                        rows.append(i)
                        cols.append(j)
        data = np.asarray(data)
        rows = np.asarray(rows)
        cols = np.asarray(cols)
        self._user_similarities = sp.sparse.coo_matrix((data, (rows, cols))).tolil()

    def _calculate_tag_similarities(self):
        data = []
        rows = []
        cols = []
        for i, u1 in enumerate(self.tags_id):
            for j, u2 in enumerate(self.tags_id):
                if j > i:
                    break
                elif j == i:
                    data.append(1)
                    rows.append(i)
                    cols.append(j)
                else:
                    s = self._sim(u1, u2, self.tag_artists_iter)
                    if s > 0:
                        data.append(s)
                        rows.append(i)
                        cols.append(j)
        data = np.asarray(data)
        rows = np.asarray(rows)
        cols = np.asarray(cols)
        self._tag_similarities = sp.sparse.coo_matrix((data, (rows, cols))).tolil()

    def _calculate_artist_similarities_over_users(self):
        data = []
        rows = []
        cols = []
        for i, a1 in enumerate(self.artists_id):
            for j, a2 in enumerate(self.artists_id):
                if j > i:
                    break
                elif j == i:
                    data.append(1)
                    rows.append(i)
                    cols.append(j)
                else:
                    s = self._sim(a1, a2, self.artist_users_iter)
                    if s > 0:
                        data.append(s)
                        rows.append(i)
                        cols.append(j)
        data = np.asarray(data)
        rows = np.asarray(rows)
        cols = np.asarray(cols)
        self._artist_similarities_users = sp.sparse.coo_matrix((data, (rows, cols))).tolil()

    def _calculate_artist_similarities_over_tags(self):
        data = []
        rows = []
        cols = []
        for i, a1 in enumerate(self.artists_id):
            for j, a2 in enumerate(self.artists_id):
                if j > i:
                    break
                elif j == i:
                    data.append(1)
                    rows.append(i)
                    cols.append(j)
                else:
                    s = self._sim(a1, a2, self.artist_tags_iter)
                    if s > 0:
                        data.append(s)
                        rows.append(i)
                        cols.append(j)
        data = np.asarray(data)
        rows = np.asarray(rows)
        cols = np.asarray(cols)
        self._artist_similarities_tags = sp.sparse.coo_matrix((data, (rows, cols))).tolil()

    def _sim(self, elem1, elem2, members_iter):
        cluster1 = set(members_iter(elem1))
        cluster2 = set(members_iter(elem2))
        return self._sim_over_clusters(cluster1, cluster2)

    def _sim_over_clusters(self, cluster1, cluster2):
        inter = len(cluster1.intersection(cluster2))
        diff1 = len(cluster1.difference(cluster2))
        diff2 = len(cluster2.difference(cluster1))

        denom = inter + diff1 + diff2
        if denom == 0:
            # Case where one artist being compared has no tags
            return 0
        return inter * 1.0 / denom

    def add_user(self, friends, listens):
        # Update users existing in the system
        new_id = max(self.users_id) + 1
        self.users_id.append(new_id)
        k = self.key_user(new_id)

        # Add friendship connections
        for fid in friends:
            k2 = self.key_user(fid)
            self._graph.add_edge(k, k2, weight=1., type='uu')

        # Add listens connections
        for aid, times in listens.iteritems():
            ka = self.key_artist(aid)
            self._graph.add_edge(k, ka, weight=times, type='ua')
            self._graph.add_edge(ka, k, weight=times, type='au')

        # Update user similarity matrix
        aux_sim = self.user_similarities.copy()
        aux_sim = aux_sim.tocoo()

        aux_sim._shape = (self.user_similarities._shape[0] + 1, self.user_similarities._shape[1] + 1)

        for j, user in enumerate(self.users_id):
            s = self._sim(k, user, self.user_artists_iter)
            if s > 0:
                aux_sim.data = np.append(aux_sim.data, s)
                aux_sim.row = np.append(aux_sim.row, self.user_similarities.shape[0])
                aux_sim.col = np.append(aux_sim.col, j)

        self.user_similarities = aux_sim.tolil()
        
    def add_tagged_artist(self, user, artist, tag):
        # Check user, artist and tag already exist
        ku = self.key_user(user)
        ka = self.key_artist(artist)
        kt = self.key_tag(tag)
        
        if ku in self._graph.nodes() and ka in self._graph.nodes() and kt in self._graph.nodes():
            # Update artist-tag edge and vice versa, or add it if new
            if self._graph.has_edge(ka, kt):
                new_w = self._graph[ka][kt]['weight'] + 1
            else:
                new_w = 1
            
            self._graph.add_edge(ka, kt, weight=new_w, type='at')
            self._graph.add_edge(kt, ka, weight=new_w, type='ta')
            
            # Update row of artist in similarity matrix
            for i, this_artist in enumerate(self.artists_id):
                # Find row of the matrix from our artist being updated
                if ka==self.key_artist(this_artist):
                    for j, art in enumerate(self.artists_id):
                        s = self._sim(ka, self.key_artist(art), self.artist_tags_iter)
                        if s>0:
                            self.artist_similarities_tags[i,j] = s
                    break   # Only need to change this row of the matrix
        else:
            # We should not add relations between not existing elements
            return -1
        
    def add_reproduction(self, user, artist):
        # Check user and artist already exist
        ku = self.key_user(user)
        ka = self.key_artist(artist)
        
        if ku in self._graph.nodes() and ka in self._graph.nodes():
            # Update artist-user edge and vice versa, or add it if new
            if self._graph.has_edge(ka, ku):
                new_w = self._graph[ka][ku]['weight'] + 1
            else:
                new_w = 1
            
            self._graph.add_edge(ka, ku, weight=new_w, type='au')
            self._graph.add_edge(ku, ka, weight=new_w, type='ua')

    def get_artists_tags_partition(self):
        if self._artists_tags is not None:
            return self._artists_tags

        self._artists_tags = nx.Graph()
        for artist_id in self.artists_iter():
            for tag_id in self.artist_tags_iter(artist_id):
                self._artists_tags.add_edge(artist_id, tag_id)
        return self._artists_tags

    def get_artists_users_partition(self):
        if self._artists_users is not None:
            return self._artists_users

        self._artists_users = nx.Graph()
        for artist_id in self.artists_iter():
            for user_id in self.artist_user_iter(artist_id):
                self._artists_users.add_edge(artist_id, user_id)
        return self._artists_users

    def get_users_users_partition(self):
        if self._users_users is not None:
            return self._users_users

        self._users_users = nx.Graph()
        for user_id in self.users_iter():
            for user_id2 in self.user_user_iter(user_id):
                self._users_users.add_edge(user_id, user_id2)

        return self._users_users
