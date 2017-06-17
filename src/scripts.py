# coding: utf-8

from recommender_system import RecommenderSystem

minFreqs = [0,10]
recommendationLengths = [1,5,20]
artistSims = ['tags', 'users']
maxReferenceArtists = [1,3]
kneighborhood = [1]
maxSimilarUsers = [1,3]

for minFreq in minFreqs:
    e = RecommenderSystem(minFreqTag=minFreq)
    for recommendationLength in recommendationLengths:
        for artistSim in artistSims:
            if artistSim=='users' and minFreq != minFreqs[0]:
                break;
            for refArtists in maxReferenceArtists:
                for k in kneighborhood:
                    for simUsers in maxSimilarUsers:
                        e.recommendation_evaluation(maxReferenceArtists=refArtists, kneighborhood=k, maxSimilarUsers=simUsers, recommendationLength=recommendationLength, relevanceLength=None, relevanceAccum=0.95, numUsers=10000, artistSim=artistSim)
