from lastfm_network import *

import unittest


class TestLastfmNetwork(unittest.TestCase):
    lastfm_net = None

    @classmethod
    def setUpClass(cls):
        cls.lastfm_net = LastfmNetwork.instance()

    def test_friends(self):
        self.assertTrue(self.lastfm_net.are_friends(2, 275))
        self.assertFalse(self.lastfm_net.are_friends(2, 2))

    def test_is_my_artist(self):
        self.assertTrue(self.lastfm_net.is_my_artist(2100, 18730))
        self.assertFalse(self.lastfm_net.is_my_artist(2100, 18732))

    def test_is_my_listener(self):
        self.assertTrue(self.lastfm_net.is_my_listener(18730, 2100))
        self.assertFalse(self.lastfm_net.is_my_listener(18732, 2100))

        # def test_artits(self):
        #     weight = 13883
        #     self.assertEqual(
        #         weight,
        #         self.lastfm_net.times_user_listen_artist(2, 51)
        #     )

        # def test_draw(self):
        #     self.lastfm_net.draw()
    def test_check_friendship(self):
        self.assertTrue(self.lastfm_net.check_friendship())

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
        
        n_tags = len(self.lastfm_net.tags_id)
        self.assertEqual(n_tags, self.lastfm_net.tag_similarities.shape[0])
        self.assertEqual(n_tags, self.lastfm_net.tag_similarities.shape[1])
        
    def test_similarities_in_01(self):
        self.assertEqual(0, sum(sum(self.lastfm_net.user_similarities<0)))
        self.assertEqual(0, sum(sum(self.lastfm_net.user_similarities>1)))
        self.assertEqual(0, sum(sum(self.lastfm_net.tag_similarities<0)))
        self.assertEqual(0, sum(sum(self.lastfm_net.tag_similarities>1)))
        
if __name__ == '__main__':
    unittest.main()
