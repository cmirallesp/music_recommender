#coding: utf-8

#from lastfm_network import LastfmNetwork
#net = LastfmNetwork.instance()

from recommender_system import RecommenderSystem
from time import time

t = time()
r = RecommenderSystem.instance()
print 'Everything loaded in '+str(time()-t)

t=time()
r.recommendation('u_1210', recommendationLength=20)
print 'Recommendation performed in '+str(time()-t)

t=time()
e.recommendation_evaluation(numUsers=25, maxSimilarUsers=5, maxReferenceArtists=5, recommendationLength=10, relevanceLength=100)
print 'Evaluation performed in '+str(time()-t)