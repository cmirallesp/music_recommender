import os
recommendationLengths = [1, 5, 20]
maxReferenceArtists = [3]
kneighborhood = [1, 2, 5, None]
maxSimilarUsers1 = [1, 5]  # (for k=1, 2, 5)
maxSimilarUsers2 = [1, 5, 10, 50]  # (for k=None)
for recommendationLength in recommendationLengths:
    for refArtists in maxReferenceArtists:
        for k in kneighborhood:
            maxSimilarUsers = maxSimilarUsers1 if k else maxSimilarUsers2
            for simUsers in maxSimilarUsers:
                old_name = 'kN=' + str(kneighborhood) + ', SU=' + str(maxSimilarUsers) + ', RA=' + str(maxReferenceArtists) + ', RL=' + str(recommendationLength) + ".png"
                new_name = 'kN=' + str(kneighborhood) + '_SU=' + str(maxSimilarUsers) + '_RA=' + str(maxReferenceArtists) + '_RL=' + str(recommendationLength) + ".png"
                os.rename(old_name, new_name)
