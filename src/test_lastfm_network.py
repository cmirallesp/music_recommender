from lastfm_network import *

import unittest
import pprint as pp
import networkx as nx


class TestLastfmNetwork(unittest.TestCase):
    lastfm_net = None

    @classmethod
    def setUpClass(cls):
        cls.lastfm_net = LastfmNetwork()

    def test_friends(self):
        self.assertTrue(self.lastfm_net.are_friends(2, 275))
        self.assertFalse(self.lastfm_net.are_friends(2, 2))

    def test_is_my_artist(self):
        self.assertTrue(self.lastfm_net.is_my_artist(2100, 18730))
        self.assertFalse(self.lastfm_net.is_my_artist(2100, 18732))

    def test_is_my_listener(self):
        self.assertTrue(self.lastfm_net.is_my_listener(18730, 2100))
        self.assertFalse(self.lastfm_net.is_my_listener(18732, 2100))

    def test_friendship_normalized_weights(self):
        # ensure that normalized weights of the user 2 sums 1
        sum_ = sum(list(self.lastfm_net.user_user_normalized_weights_iter(2)))
        self.assertEqual(1.0, round(sum_))

    def test_friendship_weight(self):
        # Ensure that networks normalized weights have been normalized
        # after being created
        self.assertTrue(self.lastfm_net.are_friends(2, 275))
        self.assertEqual(1. / self.lastfm_net.number_of_friends(2),
                         self.lastfm_net.user_user_normalized_weight(2, 275))

    def test_my_artist_normalized_weights(self):
        # ensure that normalized weights of the user 2100 sums 1
        sum_ = sum(list(
            self.lastfm_net.user_artist_normalized_weights_iter(2100)))
        self.assertEqual(1.0, round(sum_))

    def test_my_artists_weight(self):
        # Ensure that networks normalized weights have been normalized
        # after being created
        self.assertTrue(self.lastfm_net.is_my_artist(2100, 18730))
        self.assertEqual(
            (self.lastfm_net.user_artist_weight(2100, 18730) /
                self.lastfm_net.total_user_artists_weights(2100)
             ),
            self.lastfm_net.user_artist_normalized_weight(2100, 18730)
        )

    def test_my_listeners_normalized_weights(self):
        # ensure that normalized weights of the artist 18730 sums 1
        sum_ = sum(list(
            self.lastfm_net.artist_user_normalized_weights_iter(18730)))
        self.assertEqual(1.0, round(sum_))

    def test_my_listeners_weight(self):
        # Ensure that networks normalized weights have been normalized
        # after being created
        self.assertTrue(self.lastfm_net.is_my_listener(18730, 2100))
        self.assertEqual(
            (self.lastfm_net.artist_user_weight(18730, 2100) /
                self.lastfm_net.total_artist_users_weights(18730)
             ),
            self.lastfm_net.artist_user_normalized_weight(18730, 2100)
        )

    def test_my_tags_normalized_weights(self):
        # Ensure that normalized weights of the artist 12648 sums 1
        sum_ = sum(list(
            self.lastfm_net.artist_tags_normalized_weights_iter(12648)
        ))
        self.assertEqual(1.0, round(sum_))

    def test_my_tags_normalized_weight(self):
        self.assertTrue(self.lastfm_net.is_my_tag(16437, 3335))
        self.assertEqual(
            (self.lastfm_net.artist_tag_weight(16437, 3335) /
                self.lastfm_net.total_artist_tags_weights(16437)
             ),
            self.lastfm_net.artist_tag_normalized_weight(16437, 3335)
        )

    def test_tags_artists_normalized_weights(self):
        # Ensure that normalized weights of the tag 3335 sums 1
        sum_ = sum(list(
            self.lastfm_net.tags_artists_normalized_weights_iter(3335)
        ))
        self.assertEqual(1.0, round(sum_))

    def test_tags_normalized_weight(self):
        self.assertTrue(self.lastfm_net.is_my_artist_2(3335, 16437))
        self.assertEqual(
            (self.lastfm_net.tag_artist_weight(3335, 16437) /
                self.lastfm_net.total_tag_artists_weights(3335)
             ),
            self.lastfm_net.tag_artist_normalized_weight(3335, 16437)
        )

    def test_tag_artist_weight(self):
        self.assertTrue(self.lastfm_net.is_my_artist_2(4365, 8322))
        self.assertEqual(3, self.lastfm_net.tag_artist_weight(4365, 8322))

    def test_user_walking_weights(self):
        # Ensure that walking weights of all edges going from user 2
        # sum 1 (both user-artist and user-user)
        sum_friends = sum(
            list(self.lastfm_net.user_user_walking_weights_iter(2))
        )
        sum_artists = sum(
            list(self.lastfm_net.user_artist_walking_weights_iter(2))
        )
        self.assertEqual(1.0, round(sum_friends + sum_artists))

    def test_similarities_created(self):
        n_users = len(self.lastfm_net.users_id)
        self.assertEqual(n_users, self.lastfm_net.user_similarities.shape[0])
        self.assertEqual(n_users, self.lastfm_net.user_similarities.shape[1])

        # n_tags = len(self.lastfm_net.tags_id)
        # self.assertEqual(n_tags, self.lastfm_net.tag_similarities.shape[0])
        # self.assertEqual(n_tags, self.lastfm_net.tag_similarities.shape[1])

        n_artists = len(self.lastfm_net.artists_id)
        # self.assertEqual(n_artists, self.lastfm_net.artist_similarities_users.shape[0])
        # self.assertEqual(n_artists, self.lastfm_net.artist_similarities_users.shape[1])
        self.assertEqual(n_artists, self.lastfm_net.artist_similarities_tags.shape[0])
        self.assertEqual(n_artists, self.lastfm_net.artist_similarities_tags.shape[1])

    def test_similarities_in_01(self):
        self.assertEqual(0, (self.lastfm_net.user_similarities < 0).getnnz())
        self.assertEqual(0, (self.lastfm_net.user_similarities > 1).getnnz())
        # self.assertEqual(0, (self.lastfm_net.tag_similarities<0).getnnz())
        # self.assertEqual(0, (self.lastfm_net.tag_similarities>1).getnnz())
        self.assertEqual(0, (self.lastfm_net.artist_similarities_tags < 0).getnnz())
        self.assertEqual(0, (self.lastfm_net.artist_similarities_tags > 1).getnnz())

    def test_user_added_dynamically(self):
        new_id = max(self.lastfm_net.users_id) + 1
        self.lastfm_net.add_user([2, 5], {10: 12, 20: 31})

        # Network structure checks
        self.assertTrue(new_id in self.lastfm_net.users_id)
        self.assertTrue(self.lastfm_net.are_friends(new_id, 2))
        self.assertTrue(self.lastfm_net.are_friends(new_id, 5))
        self.assertFalse(self.lastfm_net.are_friends(new_id, 10))
        self.assertTrue(self.lastfm_net.is_my_listener(10, new_id))
        self.assertTrue(self.lastfm_net.is_my_artist(new_id, 10))
        self.assertTrue(self.lastfm_net.is_my_listener(20, new_id))
        self.assertTrue(self.lastfm_net.is_my_artist(new_id, 20))

        # Similarity checks
        last = self.lastfm_net.user_similarities.shape[0] - 1
        self.assertEqual(0, self.lastfm_net.user_similarities[last, 100])
        self.assertEqual(1, self.lastfm_net.user_similarities[last, last])

    '''    
    def test_artist_added_dynamically(self):
        old_shape0 = self.lastfm_net.artist_similarities_tags.shape()[0]
        old_shape1 = self.lastfm_net.artist_similarities_tags.shape()[1]
        new_id = max(self.lastfm_net.artists_id) + 1
        self.lastfm_net.add_artist()
        new_shape0 = self.lastfm_net.artist_similarities_tags.shape()[0]
        new_shape1 = self.lastfm_net.artist_similarities_tags.shape()[1]
        self.assertTrue(new_id in self.lastfm_net.artists_id)
        self.assertTrue(old_shape0+1, new_shape0)
        self.assertTrue(old_shape1+1, new_shape1)
        
    def test_tag_added_dynamically(self):
        new_id = max(self.lastfm_net.tags_id) + 1
        self.lastfm_net.add_tag()
        self.assertTrue(new_id in self.lastfm_net.tags_id)
    '''

    def test_num_tags_incremented_dynamically(self):
        ku = 'u_2'
        ka = 'a_17'
        kt = 't_10'

        # Save state previous to update
        old_w = self.lastfm_net._graph[ka][kt]['weight']
        old_sim_0 = -1
        old_sim_1 = -1
        idx = -1
        for i, artist in enumerate(self.lastfm_net.artists_id):
            if ka == self.lastfm_net.key_artist(artist):
                idx = i
                old_sim_0 = self.lastfm_net.artist_similarities_tags[idx, 0]
                old_sim_1 = self.lastfm_net.artist_similarities_tags[idx, idx]
                break

        # Checks in network values
        self.lastfm_net.add_tagged_artist(ku, ka, kt, 1)
        new_w1 = self.lastfm_net._graph[ka][kt]['weight']
        new_w2 = self.lastfm_net._graph[kt][ka]['weight']
        self.assertEqual(old_w + 1, new_w1)
        self.assertEqual(old_w + 1, new_w2)

        # Checks in normalized weights
        self.assertEqual(
            (self.lastfm_net.tag_artist_weight(10, 17) /
                self.lastfm_net.total_tag_artists_weights(10)
             ),
            self.lastfm_net.tag_artist_normalized_weight(10, 17)
        )
        self.assertEqual(
            (self.lastfm_net.artist_tag_weight(17, 10) /
                self.lastfm_net.total_artist_tags_weights(17)
             ),
            self.lastfm_net.artist_tag_normalized_weight(17, 10)
        )

        # Checks in similarity values
        new_sim_0 = self.lastfm_net.artist_similarities_tags[idx, 0]
        new_sim_1 = self.lastfm_net.artist_similarities_tags[idx, idx]

        self.assertEqual(old_sim_0, new_sim_0)
        self.assertEqual(old_sim_1, new_sim_1)

    def test_num_reproductions_incremented_dynamically(self):
        ku = 'u_557'
        ka = 'a_17'
        old_w = self.lastfm_net._graph[ka][ku]['weight']

        self.lastfm_net.add_reproduction(ku, ka, 1)
        new_w = self.lastfm_net._graph[ka][ku]['weight']
        self.assertEqual(old_w + 1, new_w)

        # Checks on normalized weights
        self.assertEqual(
            (self.lastfm_net.user_artist_weight(557, 17) /
                self.lastfm_net.total_user_artists_weights(557)
             ),
            self.lastfm_net.user_artist_normalized_weight(557, 17)
        )
        self.assertEqual(
            (self.lastfm_net.artist_user_weight(17, 557) /
                self.lastfm_net.total_artist_users_weights(17)
             ),
            self.lastfm_net.artist_user_normalized_weight(17, 557)
        )

    def test_get_artists_tags_partition(self):
        lst = self.lastfm_net.get_artists_tags_partition()
        self.assertEqual(27038, len(lst))


if __name__ == '__main__':
    unittest.main()
