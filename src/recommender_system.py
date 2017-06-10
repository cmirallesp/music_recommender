from lastfm_network import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns  # pip install seaborn
sns.set_palette("deep", desat=.6)
sns.set_style("whitegrid")


class RecommenderSystem(LastfmNetwork):

    def recommendation(self, referenceUser, kneighborhood=None, maxSimilarUsers=5, relevanceAccum=0.9, showRecommendation=True, recommendationLength=10):
        '''Recommendation script'''

        if self.run == 'offline':
            self.node2indexUserDict = {self.key_user(user): idx for idx, user in enumerate(self.users_id)}
            self.node2indexArtistDict = {self.key_artist(artist): idx for idx, artist in enumerate(self.artists_id)}

        # If requested, we only get the user k-neighborhood. If not, we consider all users.
        if kneighborhood:
            consideredUsers = self.get_kdistant_neighbors_by_type(referenceUser, k=kneighborhood)
            if len(consideredUsers) == 0:
                return 'Impossible to make a recommendation based on the social neighborhood: the user has no friendship relations'
        else:
            consideredUsers = [user for user in self.users_iter()]
            consideredUsers.remove(referenceUser)

        # We get the similarities of all considered users with respect to the reference one in descending order
        similarUsers = self.get_user_similarities(referenceUser, consideredUsers)
        # We only keep up to a maxSimilarUsers number of users for the recommendation
        similarUsers = [similarUser[0] for similarUser in similarUsers[:min(len(similarUsers), maxSimilarUsers)]]

        # We get the artists that the reference user has listened to
        referenceUserArtists = set(self.get_kdistant_neighbors_by_type(referenceUser, type='ua'))
        # We select as relevant those artists with a high number of reproductions by the reference user
        referenceArtists = self.get_relevant_artists_from_user(referenceUser, referenceUserArtists, relevanceAccum)

        # We look for the candidate artist list considering all similar users found
        candidateArtistList = []
        artistsAlreadyConsidered = []
        for similarUser in similarUsers:
            # The candidate artists come from the artists listened by a similar user but not by the reference one
            # We only keep those candidates that we consider relevant for the similar user
            candidateArtists = self.get_candidate_artists_from_similar_user(similarUser, referenceUser, referenceUserArtists, relevanceAccum)

            # We get the maximum similarity score of each candidate with respect to the
            # relevant artists of the reference user (except if the artist had been considered already)
            candidateArtists = [artist for artist in candidateArtists if artist not in artistsAlreadyConsidered]
            candidateArtists = self.get_scores_for_candidate_artists(referenceArtists, candidateArtists)
            artistsAlreadyConsidered += [elem[0] for elem in candidateArtists]

            # We combine these candidates with the previously found ones
            candidateArtistList = self.combine_lists_of_candidate_artists(candidateArtistList, candidateArtists)

        candidateArtistList = sorted(candidateArtistList, key=self.get_ordering_key, reverse=True)

        # Prints the recommendation if requested
        if showRecommendation:
            self.show_recommendation(referenceUser, referenceArtists, candidateArtistList, recommendationLength)

        return candidateArtistList

    def show_recommendation(self, referenceUser, referenceArtists, candidateArtists, recommendationLength):
        '''Shows the recommendation performed for the user, as well as the their relevant artists'''
        recommendedArtists = [elem[0] for elem in candidateArtists[:min(recommendationLength, len(candidateArtists))] if elem[1] > 0]
        print '\nUSER: %s' % (referenceUser)
        print '\nRELEVANT ARTISTS FOR THE USER:', [self.artistID2artist[artistID] for artistID in referenceArtists]
        print '\nRECOMMENDED ARTISTS:', [self.artistID2artist[artistID] for artistID in recommendedArtists]

    def user_recommendation_evaluation(self, referenceUser, maxReferenceArtists=3, recommendationLength=10, relevanceLength=None, kneighborhood=None, maxSimilarUsers=5, relevanceAccum=0.9):
        '''Evaluates the recommendation of a user'''

        # We get the most relevant artists from the reference user apart from the ones chosen for the recommendation
        referenceUserArtists = set(self.get_kdistant_neighbors_by_type(referenceUser, type='ua'))
        referenceArtists = self.get_relevant_artists_from_user(referenceUser, referenceUserArtists, relevanceAccum)
        if maxReferenceArtists >= len(referenceArtists):
            # print 'There are not enough relevant artists to evaluate the recommendation'
            return -1
        maxRelevantArtists = min(maxReferenceArtists + relevanceLength, len(referenceArtists)) if relevanceLength else len(referenceArtists)
        relevantArtists = set(referenceArtists[maxReferenceArtists:maxRelevantArtists])

        # We remove the edges of the reference user not used as a basis for the recommendation
        nodeConnectionsToRemove = referenceArtists[maxReferenceArtists:]
        connections = self.save_edges(referenceUser, nodeConnectionsToRemove)
        self._graph.remove_edges_from(connections)

        # We get the recommendation of the user considering only their 'maxReferenceArtists' most listened artists
        recommendedArtists = self.recommendation(referenceUser, kneighborhood=kneighborhood, maxSimilarUsers=maxSimilarUsers, relevanceAccum=relevanceAccum, showRecommendation=False)
        # We keep the most similar artists found in the recommendation
        recommendedArtists = set([recommendedArtists[i][0] for i in range(min(recommendationLength, len(recommendedArtists)))])

        # We check how many of these relevant artists the recommendation is able to recover
        recoveredArtists = relevantArtists.intersection(recommendedArtists)

        # We recover the removed connections for the evaluation
        self._graph.add_edges_from(connections)

        return len(recoveredArtists)

    def recommendation_evaluation(self, maxReferenceArtists=5, recommendationLength=10, relevanceLength=None, kneighborhood=None, maxSimilarUsers=5, relevanceAccum=0.95, numUsers=10):
        '''Evaluates the recommendation of several users'''
        self.run = 'offline'
        recoveries = []
        noValid = 0
        for user in self.users_id[0:min(numUsers, len(self.users_id))]:
            numberOfRecoveries = self.user_recommendation_evaluation(self.key_user(user), maxReferenceArtists=maxReferenceArtists, recommendationLength=recommendationLength, relevanceLength=relevanceLength, kneighborhood=kneighborhood, maxSimilarUsers=maxSimilarUsers, relevanceAccum=relevanceAccum)
            if numberOfRecoveries >= 0:
                recoveries.append(numberOfRecoveries)
            else:
                noValid += 1
        execution = 'kN=' + str(kneighborhood) + ', SU=' + str(maxSimilarUsers) + ', RA=' + str(maxReferenceArtists)
        print '\n__________________________________________________________\n'
        print execution
        print '\nEvaluation performed over %d users; %d selected users did not have enough relevant artists to be evaluated' % (len(recoveries), noValid)
        self.plot_recovery_distribution(recoveries, execution)
        print 'Median: %f. Mean: %f. Std: %f.' % (np.median(recoveries), np.mean(recoveries), np.std(recoveries))
        return recoveries

    def plot_recovery_distribution(self, recoveries, execution):
        '''Plots the Distribution of Relevant Artist Recoveries of the evaluation'''
        ax = plt.figure().gca()
        plt.xticks(range(np.min(recoveries), np.max(recoveries) + 1))
        #ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.hist(recoveries, weights=len(recoveries)*[1./len(recoveries)], range=(np.min(recoveries) - 0.5, np.max(recoveries) + 0.5), bins=np.max(recoveries) + 1)
        plt.suptitle('Distribution of Relevant Artist Recoveries', fontweight='bold', fontsize=12)
        plt.title(execution, fontsize=9)
        plt.xlabel("Number of Recoveries")
        plt.ylabel("Relative Frequency")
        plt.savefig('plots/' + execution, bbox_inches='tight')
        # plt.show()

    def save_edges(self, referenceNode, listOfNodes):
        'Stores the edges between referenceNode and those in listOfNodes'
        edges = []
        for node in listOfNodes:
            edges.append((referenceNode, node, self._graph.get_edge_data(referenceNode, node)))
        return edges

    def get_kdistant_neighbors_by_type(self, centralNode, type='uu', k=1):
        '''return the neighbors of a node up to a distance k
        specifying the kind of edges to consider'''
        nodesToExplore = [centralNode]
        neighbors = []
        for _ in range(k):
            newNeighbors = []
            for node in nodesToExplore:
                newNeighbors += [x for x in self._graph.neighbors(node)
                                 if (self._graph.get_edge_data(node, x)['type'] == type
                                 and x not in neighbors + [centralNode] + newNeighbors)]
            neighbors += newNeighbors
            nodesToExplore = newNeighbors
        return neighbors

    def get_user_user_similarity(self, node1, node2):
        '''given two userIDs, return the computed similarity between them'''
        ''' #Offline setting
        idx1, idx2 = self.node2indexUserDict[node1], self.node2indexUserDict[node2]
        if idx1 > idx2:
            return self.user_similarities[idx1, idx2]
        else:
            return self.user_similarities[idx2, idx1]
        '''
        cluster1 = set(self.get_kdistant_neighbors_by_type(node1, type='ua'))
        cluster2 = set(self.get_kdistant_neighbors_by_type(node2, type='ua'))
        return self._sim_over_clusters(cluster1, cluster2)

    def get_artist_artist_similarity(self, node1, node2):
        '''given two artistIDs, return the computed similarity between them'''
        if self.run == 'offline':
            idx1, idx2 = self.node2indexArtistDict[node1], self.node2indexArtistDict[node2]
            if idx1 > idx2:
                return self.artist_similarities_tags[idx1, idx2]
            else:
                return self.artist_similarities_tags[idx2, idx1]
        else:
            cluster1 = set(self.get_kdistant_neighbors_by_type(node1, type='at'))
            cluster2 = set(self.get_kdistant_neighbors_by_type(node2, type='at'))
            return self._sim_over_clusters(cluster1, cluster2)

    def get_ordering_key(self, element):
        '''useful function for obtaining the ordering key of lists of tuples'''
        return element[1]

    def get_user_similarities(self, centralNode, listOfNodes):
        '''given a reference user and a list of users, computes the similarity
        of each element of the list with respect to the reference user'''
        userSim = [(node, self.get_user_user_similarity(centralNode, node)) for node in listOfNodes]
        return sorted(userSim, key=self.get_ordering_key, reverse=True)

    def get_artist_similarities(self, centralNode, listOfNodes):
        '''given a reference artist and a list of artists, computes the similarity
        of each element of the list with respect to the reference artist'''
        artistSim = [(node, self.get_artist_artist_similarity(centralNode, node)) for node in listOfNodes]
        return sorted(artistSim, key=self.get_ordering_key, reverse=True)

    def get_relevant_artists_from_user(self, user, userArtists, maxAccum):
        '''Retrieves the most listened artists'''
        weightedUserArtists = [(artist, self._graph.get_edge_data(user, artist)['norm_weight'])
                               for artist in userArtists]
        relevantArtists, accum = [], 0.
        for artist, weight in sorted(weightedUserArtists, key=self.get_ordering_key, reverse=True):
            relevantArtists += [artist]
            accum += weight
            if accum > maxAccum:
                break
        return relevantArtists

    def get_candidate_artists_from_similar_user(self, similarUser, referenceUser, referenceUserArtists, relevanceAccum):
        '''Gets the relevant candidate artists from a similar user'''
        # We get the artists that the similar user has listened to
        similarUserArtists = set(self.get_kdistant_neighbors_by_type(similarUser, type='ua'))
        # The candidate artists come from the difference with respect to the ones that the reference user has listened to
        candidateArtists = similarUserArtists.difference(referenceUserArtists)
        # We return the candidates that we consider relevant for the similar user
        relevantSimilarUserArtists = set(self.get_relevant_artists_from_user(similarUser, similarUserArtists, relevanceAccum))
        return list(candidateArtists.intersection(relevantSimilarUserArtists))

    def get_scores_for_candidate_artists(self, referenceArtists, candidateArtists):
        '''Retrieves for each candidate artist the maximum similarity score with respect to any
        reference artist'''
        return [(artist, self.get_artist_similarities(artist, referenceArtists)[0][1])
                for artist in candidateArtists]

    def combine_lists_of_candidate_artists(self, list1, list2):
        '''Combine lists of candidate artists avoiding repetitions'''
        return list(set(list1 + list2))
