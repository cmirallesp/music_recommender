#coding: utf-8
#import pandas as pd
#user_taggedartists = pd.read_table('../data/user_taggedartists.dat')
#tags = user_taggedartists.groupby('tagID').groups
#user_artists = pd.read_table('../data/user_artists.dat')
#user_artists = pd.read_table('../data/user_artists.dat')
#artists = pd.read_table('../data/artists.dat')

#g = user_taggedartists[["userID", "artistID", "tagID"]].groupby(["userID", "artistID", "tagID"])
#g.filter(lambda x: len(x) > 1)

#g = user_taggedartists[["artistID", "tagID"]].groupby(["artistID", "tagID"])
#g.filter(lambda x: len(x) > 1)

#from lastfm_network import LastfmNetwork
#net = LastfmNetwork.instance()

from recommender_system import RecommenderSystem

r = RecommenderSystem.instance()
r.recommendation('u_1210')