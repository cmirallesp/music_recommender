from pylab import *
from lastfm_network import LastfmNetwork
import pandas as pd
import networkx as nx


def plot(d, name):
    degree = np.array(d)
    num_bins = 15
    k_min = degree.min()
    k_max = degree.max()

    bins = np.linspace(k_min, k_max + 1, num_bins)
    plt.title("{}:{}".format("PDF", title))
    count, bins, rem = plt.hist(degree, bins=bins,
                                label='Empirical distribution')

    plt.savefig('{}.png'.format(name))

    plt.figure()
    bins = np.logspace(np.log10(k_min), np.log10(k_max), num_bins + 1)
    plt.xscale('log')
    plt.title("{}:{}".format("PDF", title))
    count, bins, rem = plt.hist(degree, bins=bins, log=True,
                                label='Empirical distribution')
    plt.savefig('{}_log.png'.format(name))


net = LastfmNetwork(
    user_friends=pd.read_table('../data/user_friends.dat'),
    user_artists=pd.read_table('../data/user_artists.dat'),
    user_taggedartists=pd.read_table('../data/user_taggedartists.dat')
)
d1 = []
for tag_id in net.tags_iter():
    d1.append(nx.degree(net.network(), tag_id))
print "max degree:{}".format(max(d1))
plot(d1, "tag_dregree")

# d = []
# for artist_id in net.artists_iter():
#     d.append(nx.degree(net.network(), artist_id))
# plot(d2)
