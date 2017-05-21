import pandas as pd
user_taggedartists = pd.read_table('../data/user_taggedartists.dat')
tags = user_taggedartists.groupby('tagID').groups
user_artists = pd.read_table('../data/user_artists.dat')
user_artists = pd.read_table('../data/user_artists.dat')
artists = pd.read_table('../data/artists.dat')

g = user_taggedartists[["userID", "artistID", "tagID"]].groupby(["userID", "artistID", "tagID"])
g.filter(lambda x: len(x) > 1)
