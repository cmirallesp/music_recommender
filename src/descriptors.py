from pylab import *
from lastfm_network import LastfmNetwork
import time
import pickle
from networkx_to_graphtool import nx2gt
import graph_tool.stats as st
import graph_tool.topology as top
import graph_tool.clustering as clu
import os
import networkx as nx
import pdb


NETWORK_TITLES = {
    'at': "Artists-Tags"
}
PLOT_TITLES = {
    'dd': "Degree distribution",
    'sp': "Shortest Path distribution",
    'cd': "Components distribution"
}


def gt_network(nx_network, file_name):
    # returns a network converted to graph_tool
    if os.path.isfile(file_name):
        print "====>"
        gt_net = pickle.load(open(file_name, "rb"))
    else:
        print "<====="
        gt_net = nx2gt(nx_network)
        pickle.dump(gt_net, open(file_name, "wb"))
    return gt_net


def plot_hist(x, y, title, file_name, loglog=False):
    plt.figure()
    plt.title(title)

    N = y[y > 0].shape[0]
    if loglog:
        x_ = np.logspace(np.log10(1), np.log10(N), N)
    else:
        x_ = np.linspace(1, N, N)

    plt.hist(x_, weights=y[y > 0], log=loglog, bins=15)

    plt.savefig('plots/{}.png'.format(file_name))


def shortest_paths(network):
    start = time.clock()
    counts, bins = st.distance_histogram(gt_net)
    print "time: {}".format(time.clock() - start)
    return counts, bins


def get_descriptors(network, short_name, net2):
    filename = "{}.pickle".format(short_name)
    if os.path.isfile(filename):
        result = pickle.load(open(filename, 'rb'))
        return result

    result = {}
    result['filename_dd'] = '{}_dd'.format(short_name)  # degree dist
    result['filename_dd2'] = '{}_dd_log'.format(short_name)  # degree dist
    result['filename_sp'] = '{}_sp'.format(short_name)  # shortest path
    result['filename_cd'] = '{}_cd'.format(short_name)  # shortest path
    result['filename_cd2'] = '{}_cd_log'.format(short_name)  # shortest path
    nodes = list(network.vertices())
    edges = list(network.edges())

    result['num_nodes'] = len(nodes)
    result['num_edges'] = len(edges)
    # we use out_ because is undirected graph a
    result['degree'] = {}
    result['degree']['max'] = network.get_out_degrees(nodes).max()
    result['degree']['min'] = network.get_out_degrees(nodes).min()
    avg_out_d, _ = st.vertex_average(network, "total")
    result['degree']['avg'] = avg_out_d
    result['degree']["counts"], result['degree']["bins"] = st.vertex_hist(network, "total")
    result['sp'] = {}

    # stimated diamater  and lingest path
    d, (v1, v2) = top.pseudo_diameter(network)
    result['diameter'] = d
    d_path = "{}-{}".format(network.vp['id'][v1], network.vp['id'][v2])
    result['diameter_path'] = d_path

    result['clustering'] = clu.global_clustering(network)
    # connected components
    _, c2 = top.label_components(network)
    result['components'] = {}
    result['components']['num'] = len(c2)
    result['components']['bins'] = range(len(c2))
    result['components']['counts'] = c2

    pickle.dump(result, open(filename, "wb"))
    return result


def get_title(network_type, plot_type):
    return "{} ({})".format(PLOT_TITLES[plot_type], NETWORK_TITLES[network_type])


net = LastfmNetwork.instance()
gt_net = gt_network(net.get_artists_tags_partition(), "gt_at.pickle")
at_desc = get_descriptors(gt_net, 'at', net.network_as_undirected(net.get_artists_tags_partition()))

plot_hist(at_desc['degree']['bins'], at_desc["degree"]['counts'],
          title=get_title('at', 'dd'),
          file_name=at_desc["filename_dd"])
plot_hist(at_desc['degree']['bins'], at_desc["degree"]['counts'],
          title=get_title('at', 'dd'),
          file_name=at_desc["filename_dd2"], loglog=True)
plot_hist(at_desc['components']['bins'], at_desc['components']['counts'],
          title=get_title('at', 'cd'),
          file_name=at_desc["filename_cd"])

plot_hist(at_desc['components']['bins'], at_desc['components']['counts'],
          title=get_title('at', 'cd'),
          file_name=at_desc["filename_cd2"], loglog=True)
# plot_hist(at_desc['sp']['bins'], at_desc['sp']['counts'], title=get_title('at', 'sp'),
#           file_name=at_desc['filename_sp'])
