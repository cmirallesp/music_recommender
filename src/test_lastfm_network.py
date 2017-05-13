from lastfm_network import *
import pandas as pd
import unittest


class TestLastfmNetwork(unittest.TestCase):

    def setUp(self):
        self.lastfm_net = LastfmNetwork(
            user_friends=pd.read_table('../data/user_friends.dat'),
            user_artists=pd.read_table('../data/user_artists.dat'),
            user_taggedartists=pd.read_table('../data/user_taggedartists.dat')
        )

    def test_friends(self):
        self.assertTrue(self.lastfm_net.friends(2, 275))
        self.assertFalse(self.lastfm_net.friends(2, 2))

    def test_artits(self):
        weight = 13883
        self.assertEqual(
            weight,
            self.lastfm_net.times_user_listen_artist(2, 51)
        )


if __name__ == '__main__':
    unittest.main()