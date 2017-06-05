from lastfm_network import *
import matplotlib.pyplot as plt

class RecommenderSystem(LastfmNetwork):
    
    def recommendation(self, referenceUser, maxReferenceArtists=None, kneighborhood=None, maxSimilarUsers=5):
        '''recommender script: given a userID, retrieves the recommended artists'''
        
        # We create dictionaries to move between node IDs and indices of similarity matrices
        self.node2indexUserDict = {self.key_user(user): idx for idx,user in enumerate(self.users_id)}
        self.node2indexArtistDict = {self.key_artist(artist): idx for idx,artist in enumerate(self.artists_id)}
        
        # If requested, we only get the user k-neighborhood. If not, we consider all users.
        if kneighborhood:
            consideredUsers = self.get_kdistant_neighbors_by_type(referenceUser, k=kneighborhood)
            if len(consideredUsers)==0:
                return 'Impossible to make a recommendation based on the social neighborhood: the user has no friendship relations'
        else: 
            consideredUsers = [user for user in self.users_iter()]
            consideredUsers.remove(referenceUser)
        
        # We get the similarities of all considered users with respect to the reference one in descending order
        similarUsers = self.get_user_similarities(referenceUser, consideredUsers)
        # We only keep up to a maxSimilarUsers number of users for the recommendation
        similarUsers = [similarUser[0] for similarUser in similarUsers[:min(len(similarUsers),maxSimilarUsers)]]
        
        # We get the artists that the reference user has listened to
        referenceUserArtists = set(self.get_kdistant_neighbors_by_type(referenceUser, type='ua'))
        # We select as relevant those artists with a high number of reproductions by the reference user
        referenceArtists = self.get_relevant_artists_from_user(referenceUser, referenceUserArtists)
        
        # We look for the candidate artist list considering all similar users found
        candidateArtistList = []
        for similarUser in similarUsers:
            # The candidate artists come from the artists listened by a similar user but not by the reference one
            # We only keep those candidates that we consider relevant for the similar user
            candidateArtists = self.get_candidate_artists_from_similar_user(similarUser, referenceUser, referenceUserArtists)
            
            # We get the maximum similarity score of each candidate with respect to the 
            # relevant artists of the reference user
            candidateArtists = self.get_scores_for_candidate_artists(referenceArtists, candidateArtists)
            
            # We combine these candidates with the previously found ones
            candidateArtistList = self.combine_lists_of_candidate_artists(candidateArtistList, candidateArtists)
            
        candidateArtistList = sorted(candidateArtistList, key=self.get_ordering_key, reverse=True)
        return candidateArtistList
    
    def user_recommendation_evaluation(self, referenceUser, maxReferenceArtists=3, recommendationLength=10, relevanceLength=10, kneighborhood=None, maxSimilarUsers=5):
        '''Evaluates the recommendation of a user'''
        
        # We get the most relevant artists from the reference user apart from the ones chosen for the recommendation
        referenceUserArtists = set(self.get_kdistant_neighbors_by_type(referenceUser, type='ua'))
        referenceArtists = self.get_relevant_artists_from_user(referenceUser, referenceUserArtists)
        if maxReferenceArtists >= len(referenceArtists):
            print 'There are not enough relevant artists to evaluate the recommendation'
            return -1
        relevantArtists = set(referenceArtists[maxReferenceArtists:min(maxReferenceArtists+relevanceLength,len(referenceArtists)-1)])
        
        # We remove the edges of the reference user not used as a basis for the recommendation
        nodeConnectionsToRemove = referenceArtists[min(maxReferenceArtists,len(referenceArtists)-1):]
        connections = self.save_edges(referenceUser, nodeConnectionsToRemove)
        self._graph.remove_edges_from(connections)
        
        # We get the recommendation of the user considering only their 'maxReferenceArtists' most listened artists
        recommendedArtists = self.recommendation(referenceUser, maxReferenceArtists=maxReferenceArtists, kneighborhood=kneighborhood, maxSimilarUsers=maxSimilarUsers)
        # We keep the most similar artists found in the recommendation
        recommendedArtists = set([recommendedArtists[i][0] for i in range(min(recommendationLength, len(recommendedArtists)))]) 
        
        # We check how many of these relevant artists the recommendation is able to recover
        recoveredArtists = relevantArtists.intersection(recommendedArtists)
        
        #print len(recoveredArtists)
        #print recommendedArtists
        #print relevantArtists
        
        # We recover the removed connections for the evaluation
        self._graph.add_edges_from(connections)
        
        return len(recoveredArtists)
    
    def recommendation_evaluation(self, maxReferenceArtists=3, recommendationLength=10, relevanceLength=10, kneighborhood=None, maxSimilarUsers=5, numUsers=100):
        '''Evaluates the recommendation of several users'''
        recoveries = []
        for user in self.users_id[0:min(numUsers,len(self.users_id))]:
            recoveries.append(self.user_recommendation_evaluation(self.key_user(user), maxReferenceArtists=maxReferenceArtists, recommendationLength=recommendationLength, relevanceLength=relevanceLength, kneighborhood=kneighborhood, maxSimilarUsers=maxSimilarUsers))
        plt.plot(recoveries)
        plt.title('Relevant artists recovered')
        plt.show()
        return recoveries
    
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
                                 if self._graph.get_edge_data(node,x)['type']==type 
                                 and x not in neighbors+[centralNode]]
            neighbors += newNeighbors
            nodesToExplore = newNeighbors
        return neighbors
    
    def get_user_user_similarity(self, node1, node2):
        '''given two userIDs, return the computed similarity between them'''
        '''
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
        idx1, idx2 = self.node2indexArtistDict[node1], self.node2indexArtistDict[node2]
        if idx1 > idx2:
            return self.artist_similarities_tags[idx1, idx2]
        else:
            return self.artist_similarities_tags[idx2, idx1]
        '''
        cluster1 = set(self.get_kdistant_neighbors_by_type(node1, type='at'))
        cluster2 = set(self.get_kdistant_neighbors_by_type(node2, type='at'))
        return self._sim_over_clusters(cluster1, cluster2)
        '''

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

    def get_relevant_artists_from_user(self, user, userArtists, maxAccum=0.9):
        '''Retrieves the most listened artists'''
        weightedUserArtists = [(artist, self._graph.get_edge_data(user,artist)['norm_weight']) 
                               for artist in userArtists]
        relevantArtists, accum = [], 0.
        for artist, weight in sorted(weightedUserArtists, key=self.get_ordering_key, reverse=True):
            relevantArtists += [artist]
            accum += weight
            if accum > maxAccum:
                break;
        return relevantArtists

    def get_candidate_artists_from_similar_user(self, similarUser, referenceUser, referenceUserArtists):
        '''Gets the relevant candidate artists from a similar user'''
        # We get the artists that the similar user has listened to
        similarUserArtists = set(self.get_kdistant_neighbors_by_type(similarUser, type='ua'))
        # The candidate artists come from the difference with respect to the ones that the reference user has listened to
        candidateArtists = similarUserArtists.difference(referenceUserArtists)
        # We return the candidates that we consider relevant for the similar user
        relevantSimilarUserArtists = set(self.get_relevant_artists_from_user(similarUser, similarUserArtists))
        return list(candidateArtists.intersection(relevantSimilarUserArtists))
    
    def get_scores_for_candidate_artists(self, referenceArtists, candidateArtists):
        '''Retrieves for each candidate artist the maximum similarity score with respect to any 
        reference artist'''
        return [(artist, self.get_artist_similarities(artist, referenceArtists)[0][1]) 
                for artist in candidateArtists]

    def combine_lists_of_candidate_artists(self, list1, list2):
        '''Combine lists of candidate artists avoiding repetitions'''
        return list(set(list1+list2))
    