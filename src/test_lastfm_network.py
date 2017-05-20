from lastfm_network import *

import unittest


class TestLastfmNetwork(unittest.TestCase):
    lastfm_net = None

    @classmethod
    def setUpClass(cls):
        cls.lastfm_net = LastfmNetwork.instance()

    def test_friends(self):
        self.assertTrue(self.lastfm_net.friends(2, 275))
        self.assertFalse(self.lastfm_net.friends(2, 2))

    def test_artits(self):
        weight = 13883
        self.assertEqual(
            weight,
            self.lastfm_net.times_user_listen_artist(2, 51)
        )

    def test_artits_sharing_more_tags(self):
        self.lastfm_net.artists_sharing_more_tags(53)

    # def test_draw(self):
    #     self.lastfm_net.draw()


if __name__ == '__main__':
    unittest.main()
