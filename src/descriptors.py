from pylab import *
from lastfm_network import LastfmNetwork
import time
import pickle
from networkx_to_graphtool import nx2gt
import graph_tool as gt
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
    'sp': "Shortest Path distribution",
    'cd': "Components distribution",
    'at': "Artist > Tag degree distribution",
    'ta': "Tag > Artist degree distribution",
    'au': "Artist > User degree distribution",
    'ua': "User > Artist degree distribution",
    'uu': "User > User degree distribution",
}


def gt_network(nx_network, file_name):
    # returns a network converted to graph_tool
    if os.path.isfile(file_name):
        print "====>"
        gt_net = pickle.load(open(file_name, "rb"))
    else:
        print "<====="
        gt_net = nx2gt(nx_network, nx.is_directed(nx_network))
        pickle.dump(gt_net, open(file_name, "wb"))
    return gt_net


def draw_hist(x, y, title, file_name, loglog=False, bins=15):
    y_ = y[y > 0]
    N = y_.shape[0]
    if loglog:
        x_ = np.logspace(np.log10(1), np.log10(N), N)
    else:
        x_ = np.linspace(1, N, N)

    plt.figure()
    plt.title(title)
    plt.hist(x_, weights=y_, log=loglog, bins=bins)
    # plt.plot(x_, y_)
    plt.savefig('plots/{}.png'.format(file_name))


def shortest_paths(network):
    start = time.clock()
    _net = gt.Graph(network)
    _net.set_directed(False)
    counts, bins = st.distance_histogram(_net)
    print "time: {}".format(time.clock() - start)
    return counts, bins


# def calc_degrees(network):
#     result = {}
#     result['ta'] = []
#     for tag_id in net.tags_iter():
#         result['ta'].append(net.degree_tag_artist(tag_id))

#     result['at'] = []
#     result['au'] = []
#     for artist_id in net.artists_iter():
#         result['at'].append(net.degree_artist_tag(artist_id))
#         result['au'].append(net.degree_artist_user(artist_id))

#     result['uu'] = []
#     result['ua'] = []
#     for user_id in net.users_iter():
#         result['ua'].append(net.degree_user_artist(user_id))
#         result['uu'].append(net.degree_user_user(user_id))
#     return result


def get_descriptors(network, short_name, already_calculated=False):
    filename = "{}.pickle".format(short_name)
    if os.path.isfile(filename):
        result = pickle.load(open(filename, 'rb'))
        return result

    result = {}
    result['name'] = short_name
    result['filename_dd'] = '{}_dd'.format(short_name)  # degree input dist
    result['filename_dd2'] = '{}_dd_log'.format(short_name)  # degree dist (log)
    result['filename_sp'] = '{}_sp'.format(short_name)  # shortest path
    result['filename_cd'] = '{}_cd'.format(short_name)  # components
    result['filename_cd2'] = '{}_cd_log'.format(short_name)  #
    nodes = list(network.vertices())
    edges = list(network.edges())

    result['num_nodes'] = len(nodes)
    result['num_edges'] = len(edges)

    # we use out_ because is undirected graph
    result['degree'] = {}
    result['degree']['max'] = network.get_out_degrees(nodes).max()
    result['degree']['min'] = network.get_out_degrees(nodes).min()
    # avg_out_d, _ = st.vertex_average(network, "total")
    avg_out_d, _ = st.vertex_average(network, "out")
    result['degree']['avg'] = avg_out_d
    result['degree']["counts"], result['degree']["bins"] = st.vertex_hist(network, "out")

    # estimated diamater  and longest path
    d, (v1, v2) = top.pseudo_diameter(network)
    result['diameter'] = d
    d_path = "{}-{}".format(network.vp['id'][v1], network.vp['id'][v2])
    result['diameter_path'] = d_path

    result['clustering'] = clu.global_clustering(network)

    if already_calculated:
        net2 = gt.Graph(network)  # undirected version
        net2.set_directed(False)
        result['sp'] = {}
        result['sp']['counts'], result['sp']['bins'] = shortest_paths(net2)
        # connected components

        _, c2 = top.label_components(net2)
        result['components'] = {}
        result['components']['num'] = len(c2)
        result['components']['bins'] = range(len(c2))
        result['components']['counts'] = c2

    pickle.dump(result, open(filename, "wb"))
    return result


def get_title(network_type, plot_type):
    return "{} ({})".format(PLOT_TITLES[plot_type], NETWORK_TITLES[network_type])


net = LastfmNetwork.instance()

gt_at_net = gt_network(net.get_artists_tags_partition(), "gt_at.pickle")
gt_ta_net = gt_network(net.get_tags_artists_partition(), "gt_ta.pickle")
gt_au_net = gt_network(net.get_artists_users_partition(), "gt_au.pickle")
gt_ua_net = gt_network(net.get_users_artists_partition(), "gt_ua.pickle")
gt_uu_net = gt_network(net.get_users_users_partition(), "gt_uu.pickle")

at_desc = get_descriptors(gt_at_net, 'at')
ta_desc = get_descriptors(gt_ta_net, 'ta', already_calculated=True)
ua_desc = get_descriptors(gt_au_net, 'ua')
au_desc = get_descriptors(gt_au_net, 'au', already_calculated=True)
uu_desc = get_descriptors(gt_uu_net, 'uu')

for desc in [at_desc, ta_desc, au_desc, ua_desc, uu_desc]:
    draw_hist(desc['degree']['bins'], desc["degree"]['counts'],
              title=PLOT_TITLES[desc['name']],
              file_name=desc["filename_dd"])
    draw_hist(desc['degree']['bins'], desc["degree"]['counts'],
              title=PLOT_TITLES[desc['name']],
              file_name=desc["filename_dd2"],
              loglog=True)

    if 'components' in desc.keys():
        draw_hist(desc['components']['bins'], desc['components']['counts'],
                  title=PLOT_TITLES['cd'],
                  file_name=desc["filename_cd"])

    if 'sp' in desc.keys():
        draw_hist(desc['sp']['bins'], desc['sp']['counts'],
                  title=PLOT_TITLES['sp'],
                  file_name=desc['filename_sp'],
                  bins=7)
