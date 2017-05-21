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

    def test_friendship_weight(self):
        self.assertTrue(self.lastfm_net.are_friends(2, 275))
        self.assertEqual(1. / self.lastfm_net.number_of_friends(2),
                         self.lastfm_net.friendship_weight(2, 275))

    def test_my_artists_weight(self):
        # Ensure that networks normalized weights have been normalized
        # after being created
        self.assertTrue(self.lastfm_net.is_my_artist(2100, 18730))
        self.assertEqual(
            (self.lastfm_net.ua_weight(2100, 18730) /
                self.lastfm_net.total_my_artists_weights(2100)
             ),
            self.lastfm_net.ua_normalized_weight(2100, 18730)
        )

    def test_my_listeners_weight(self):
        # Ensure that networks normalized weights have been normalized
        # after being created
        self.assertTrue(self.lastfm_net.is_my_listener(18730, 2100))
        self.assertEqual(
            (self.lastfm_net.au_weight(18730, 2100) /
                self.lastfm_net.total_my_listeners_weights(18730)
             ),
            self.lastfm_net.au_normalized_weight(18730, 2100)
        )

if __name__ == '__main__':
    unittest.main()
