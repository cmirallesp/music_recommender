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
import seaborn as sns  # pip install seaborn
sns.set_palette("deep", desat=.6)
sns.set_style("whitegrid")

PLOT_TITLES = {
    'sp': "Shortest Path distribution [{} > {}]",
    'cd': "Components distribution [{} > {}]",
    'wd': "Weight distribution [{} > {}]",
    'at': "{} degree distribution [Artists > Tags]",
    'ta': "{} degree distribution [Tags > Artists]",
    'au': "{} degree distribution [Artists > Users]",
    'ua': "{} degree distribution [Users > Artists]",
    'uu': "{} degree distribution [Users > Users]",
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
    x1 = x.min()
    x2 = x.max()
    if loglog:
        # x_ = np.logspace(np.log10(1), np.log10(N), N)
        x_ = np.logspace(np.log10(max(x1, 1)), np.log10(x2), N)
    else:
        # x_ = np.linspace(1, N, N)
        x_ = np.linspace(x1, x2, N)

    plt.figure()
    plt.title(title)

    plt.hist(x_, weights=y_, log=loglog, bins=bins)
    # plt.plot(x_, y_)
    plt.savefig('plots/desc/{}.png'.format(file_name))


def shortest_paths(network):
    start = time.clock()
    _net = gt.Graph(network)
    _net.set_directed(False)
    counts, bins = st.distance_histogram(_net)
    print "time: {}".format(time.clock() - start)
    return counts, bins


def get_descriptors(network, short_name, nx_network, already_calculated=False):
    def _prefixToTitle(prefix):
        if prefix == 'A':
            return "Artists"
        elif prefix == 'T':
            return "Tags"
        elif prefix == 'U':
            return 'Users'

    filename = "cache/{}.pickle".format(short_name)
    if os.path.isfile(filename):
        result = pickle.load(open(filename, 'rb'))
        return result

    result = {}
    prefix1, prefix2 = short_name[0], short_name[1]
    t1 = _prefixToTitle(prefix1)
    t2 = _prefixToTitle(prefix2)
    result['name'] = short_name
    result['title_dd1'] = PLOT_TITLES[short_name].format(t1)
    result['title_dd2'] = PLOT_TITLES[short_name].format(t2)
    result['title_wd'] = PLOT_TITLES['wd'].format(t1, t2)
    result['title_cd'] = PLOT_TITLES['cd'].format(t1, t2)
    result['title_sp'] = PLOT_TITLES['sp'].format(t1, t2)
    result['filename_dd'] = '{}_dd'.format(short_name)  # degree input dist
    result['filename_ddl'] = '{}_dd_log'.format(short_name)  # degree dist (log)
    result['filename_dd1'] = '{}_{}_dd'.format(short_name[0], short_name)  # degree input dist
    result['filename_dd2'] = '{}_{}_dd'.format(short_name[1], short_name)  # degree input dist
    result['filename_wd'] = '{}_wd'.format(short_name)  # weight distribution
    result['filename_wdl'] = '{}_wd_log'.format(short_name)  # weight distribution
    result['filename_sp'] = '{}_sp'.format(short_name)  # shortest path
    result['filename_cd'] = '{}_cd'.format(short_name)  # components
    result['filename_cdl'] = '{}_cd_log'.format(short_name)  #

    nodes = network.get_vertices()
    edges = network.get_edges()

    result['num_nodes'] = nodes.shape[0]
    result['num_edges'] = edges.shape[0]

    result['degree'] = {"total": {}, "prefix1": {}, "prefix2": {}}
    result['degree']["total"]['max'] = network.get_out_degrees(nodes).max()
    result['degree']["total"]['min'] = network.get_out_degrees(nodes).min()
    result['degree']["total"]['avg'] = network.get_out_degrees(nodes).mean()
    result['degree']["total"]["counts"], result['degree']["total"]["bins"] = st.vertex_hist(network, "out")

    lst1, lst2 = [], []
    for node in nodes:
        if prefix1 in network.vp['id'][node]:
            lst1.append(node)
        elif prefix2 in network.vp['id'][node]:
            lst2.append(node)

    result['degree']["prefix1"]['max'] = network.get_out_degrees(lst1).max()
    result['degree']["prefix1"]['min'] = network.get_out_degrees(lst1).min()
    result['degree']["prefix1"]['avg'] = network.get_out_degrees(lst1).mean()
    result['degree']["prefix1"]["counts"], result['degree']["prefix1"]["bins"] = np.histogram(network.get_out_degrees(lst1), bins=15)  # result['degree']["total"]["bins"].shape[0]
    if prefix1 == prefix2:
        lst2 = lst1
    result['degree']["prefix2"]['max'] = network.get_out_degrees(lst2).max()
    result['degree']["prefix2"]['min'] = network.get_out_degrees(lst2).min()
    result['degree']["prefix2"]['avg'] = network.get_out_degrees(lst2).mean()
    result['degree']["prefix2"]["counts"], result['degree']["prefix2"]["bins"] = np.histogram(network.get_out_degrees(lst2), bins=15)

    result['weights'] = {}
    weights = []

    for v1, v2 in nx_network.edges():
        weight = nx_network.get_edge_data(v1, v2)['weight']
        weights.append(weight)

    result['weights']['counts'], result['weights']['bins'] = np.histogram(weights, bins=8)

    # estimated diamater  and longest path
    d, (v1, v2) = top.pseudo_diameter(network)
    result['diameter'] = d
    d_path = "{}-{}".format(network.vp['id'][v1], network.vp['id'][v2])
    result['diameter_path'] = d_path

    result['clustering'] = clu.global_clustering(network)

    if not already_calculated:
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


def pprint(results):
    components = results['components']['num'] if 'components' in results.keys() else "-"
    return (
        "Name: {}\n"
        "Num nodes: {}\n"
        "Num edges: {}\n"
        "Total Max degree: {}\n"
        "Total Min degree: {}\n"
        "Total Avg degree: {}\n"
        "Prefix1 Max degree: {}\n"
        "Prefix1 Min degree: {}\n"
        "Prefix1 Avg degree: {}\n"
        "Prefix2 Max degree: {}\n"
        "Prefix2 Min degree: {}\n"
        "Prefix2 Avg degree: {}\n"
        "Diameter: {}\n"
        "Path: {}\n"
        "Clustering: {}\n"
        "Num Components: {}\n"
    ).format(
        results['name'],
        results['num_nodes'],
        results['num_edges'],
        results['degree']["total"]['max'],
        results['degree']["total"]['min'],
        results['degree']["total"]['avg'],
        results['degree']["prefix1"]['max'],
        results['degree']["prefix1"]['min'],
        results['degree']["prefix1"]['avg'],
        results['degree']["prefix2"]['max'],
        results['degree']["prefix2"]['min'],
        results['degree']["prefix2"]['avg'],
        results['diameter'],
        results['diameter_path'],  # split i path?
        results['clustering'],
        components
    )


if __name__ == '__main__':
    net = LastfmNetwork.instance()

    gt_at_net = gt_network(net.get_artists_tags_partition(), "cache/gt_at.pickle")
    # gt_ta_net = gt_network(net.get_tags_artists_partition(), "cache/gt_ta.pickle")
    gt_au_net = gt_network(net.get_artists_users_partition(), "cache/gt_au.pickle")
    # gt_ua_net = gt_network(net.get_users_artists_partition(), "cache/gt_ua.pickle")
    gt_uu_net = gt_network(net.get_users_users_partition(), "cache/gt_uu.pickle")

    at_desc = get_descriptors(gt_at_net, 'at', nx_network=net.get_artists_tags_partition())
    # ta_desc = get_descriptors(gt_ta_net, 'ta', already_calculated=True, nx_network=net.get_tags_artists_partition())
    # ua_desc = get_descriptors(gt_ua_net, 'ua', nx_network=net.get_users_artists_partition())
    au_desc = get_descriptors(gt_au_net, 'au', nx_network=net.get_artists_users_partition())
    uu_desc = get_descriptors(gt_uu_net, 'uu', nx_network=net.get_users_users_partition())

    # for desc in [at_desc, ta_desc, au_desc, ua_desc, uu_desc]:
    for desc in [at_desc, au_desc, uu_desc]:
        print pprint(desc)
        # draw_hist(desc['degree']["total"]['bins'], desc["degree"]["total"]['counts'],
        #           title=desc[''],
        #           file_name=desc["filename_dd"])

        draw_hist(desc['degree']["prefix1"]['bins'], desc["degree"]["prefix1"]['counts'],
                  title=desc['title_dd1'],
                  file_name=desc["filename_dd1"])

        draw_hist(desc['degree']["prefix2"]['bins'], desc["degree"]["prefix2"]['counts'],
                  title=desc['title_dd2'],
                  file_name=desc["filename_dd2"])

        draw_hist(desc["weights"]['bins'], desc["weights"]['counts'],
                  title=desc['title_wd'],
                  file_name=desc["filename_wd"])

        draw_hist(desc["weights"]['bins'], desc["weights"]['counts'],
                  title=desc['title_wd'],
                  file_name=desc["filename_wdl"], loglog=True)

        # draw_hist(desc['degree']['bins'], desc["degree"]['counts'],
        #           title=desc['name'],
        #           file_name=desc["filename_ddl"],
        #           loglog=True)

        if 'components' in desc.keys():
            draw_hist(desc['components']['bins'], desc['components']['counts'],
                      title=desc['title_cd'],
                      file_name=desc["filename_cd"])

        if 'sp' in desc.keys():
            draw_hist(desc['sp']['bins'], desc['sp']['counts'],
                      title=desc['title_sp'],
                      file_name=desc['filename_sp'],
                      bins=10)
