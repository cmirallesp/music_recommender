from networkx import current_flow_betweenness_centrality_subset

class RandomWalker(object):
    
    def __init__(self, net, sources_, targets_):
        self.network = net
        self.sources = sources_
        self.targets = targets_
        self.centralities = self._walk()
        
    def _walk(self):
        # Random-walk centrality by betweenness is performed over the
        # sources and targets specified in the class.
        # Returns a dictionary {node : centrality value}.
        bets = current_flow_betweenness_centrality_subset(self.network, sources=self.sources, 
                targets=self.targets, weight='walking_weight')
        return bets
    
    
    def centralities(self):
        return self.centralities
    
    
    # Add here functions for processing node centrality and do recommendations