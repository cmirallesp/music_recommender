from pylab import *
from lastfm_network import LastfmNetwork
import logging
from logging import info

# import networkx as nx
# import pdb

logging.basicConfig(filename='logging.log',
                    level=logging.DEBUG,
                    format=('%(asctime)-15s'
                            '%(funcName)s %(message)s'))


def plot(d, name):

    degree = np.array(d)
    print degree
    num_bins = 15
    k_min = max(degree.min(), 1)
    k_max = degree.max()
    plt.figure()
    bins = np.linspace(k_min, k_max + 1, num_bins)
    plt.title("{}:{}".format("PDF", name))
    count, bins, rem = plt.hist(degree, bins=bins,
                                label='Empirical distribution')

    plt.savefig('plots/{}.png'.format(name))

    plt.figure()
    bins = np.logspace(np.log10(k_min), np.log10(k_max), num_bins + 1)
    plt.xscale('log')
    plt.title("{}:{}".format("PDF", title))
    try:
        count, bins, rem = plt.hist(degree, bins=bins, log=True,
                                    label='Empirical distribution')
        info("name:{} k_min: {} k_max: {}".format(name, k_min, k_max))
        plt.savefig('plots/{}_log.png'.format(name))

    except Exception:
        info(("Has not been possible"
              "generate Log plot {}."
              "k_min: {} k_max {}").format(name, k_min, k_max))


net = LastfmNetwork.instance()

d12 = []
for tag_id in net.tags_iter():
    d12.append(net.degree_tag_artist(tag_id))

plot(d12, "tag_artist_dregree")

d21 = []
d22 = []
for artist_id in net.artists_iter():
    d21.append(net.degree_artist_tag(artist_id))
    d22.append(net.degree_artist_user(artist_id))
plot(d21, "artists_tags_degree")
plot(d22, "artists_users_degree")

d31 = []
d32 = []
for user_id in net.users_iter():
    d31.append(net.degree_user_artist(user_id))
    d32.append(net.degree_user_user(user_id))
plot(d31, "user_artist_degree")
plot(d32, "user_user_degree")
