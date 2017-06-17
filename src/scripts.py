# coding: utf-8

from recommender_system import RecommenderSystem

minFreqs = [1,3,5,10]
recommendationLengths = [10]
artistSims = ['tags', 'users']
maxReferenceArtists = [1,3,5]
kneighborhood = [1, 2, None]
maxSimilarUsers = [1, 3]

for minFreq in minFreqs:
    e = RecommenderSystem(minFreqTag=minFreq)
    for recommendationLength in recommendationLengths:
        for artistSim in artistSims:
            for refArtists in maxReferenceArtists:
                for k in kneighborhood:
                    for simUsers in maxSimilarUsers:
                        e.recommendation_evaluation(maxReferenceArtists=refArtists, kneighborhood=k, maxSimilarUsers=simUsers, recommendationLength=recommendationLength, relevanceLength=None, relevanceAccum=0.95, numUsers=10000, artistSim=artistSim)
