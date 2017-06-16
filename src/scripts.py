# coding: utf-8

#from lastfm_network import LastfmNetwork
#net = LastfmNetwork.instance()

from recommender_system import RecommenderSystem

e = RecommenderSystem(minFreqTag=0)

recommendationLengths = [1,5,20]
maxReferenceArtists = [1,3,5]
kneighborhood = [1, 2, None]
maxSimilarUsers = [1, 5]  #(for k=1, 2, 5) 

for recommendationLength in recommendationLengths:
    for refArtists in maxReferenceArtists:
        for k in kneighborhood:
            for simUsers in maxSimilarUsers:
                e.recommendation_evaluation(maxReferenceArtists=refArtists, kneighborhood=k, maxSimilarUsers=simUsers, recommendationLength=recommendationLength, relevanceLength=None, relevanceAccum=0.95, numUsers=10000)



'''
maxReferenceArtists = [3]
kneighborhood = [1, 2, 5, None]
maxSimilarUsers1 = [1, 5]  # (for k=1, 2, 5)
maxSimilarUsers2 = [1, 5, 10, 50]  # (for k=None)

for refArtists in maxReferenceArtists:
    for k in kneighborhood:
        maxSimilarUsers = maxSimilarUsers1 if k else maxSimilarUsers2
        for simUsers in maxSimilarUsers:
            e.recommendation_evaluation(maxReferenceArtists=refArtists, kneighborhood=k, maxSimilarUsers=simUsers, recommendationLength=10, relevanceLength=None, relevanceAccum=0.95, numUsers=10000)
'''