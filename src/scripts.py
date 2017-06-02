#coding: utf-8

#from lastfm_network import LastfmNetwork
#net = LastfmNetwork.instance()

from recommender_system import RecommenderSystem
from time import time

t = time()
r = RecommenderSystem.instance()
print 'Everything loaded in '+str(time()-t)

t=time()
print r.recommendation('u_1210')
print 'Recommendation performed in '+str(time()-t)