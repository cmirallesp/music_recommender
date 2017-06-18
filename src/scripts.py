# coding: utf-8

from recommender_system import RecommenderSystem

# Example of a recommendation

# parameters
referenceUser = 'u_511'
minFreqTag = 100
recommendationLength = 10
artistSim = 'users' #'tags'
kneighborhood = 1
maxSimilarUsers = 3

#Initialization
recommender = RecommenderSystem(minFreqTag=minFreqTag)

#Recommendation
recommender.recommendation(referenceUser, kneighborhood=kneighborhood, maxSimilarUsers=maxSimilarUsers, recommendationLength=recommendationLength, relevanceAccum=0.95, artistSim=artistSim)
