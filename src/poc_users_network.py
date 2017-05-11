import pandas as pd
import graph_tool.all as gt
import igraph as ig
import time
import pdb
# user_artists = pd.read_table('user_artists.dat')


def graph_gt(user_friends):
    _graph = gt.Graph(directed=False)
    # double|bool|object(dict or whatever)
    vprop = _graph.new_vertex_property("int")
    _graph.vp.id = vprop
    vprop2 = _graph.new_vertex_property("string")
    _graph.vp.type = vprop2
    added = {}
    for uid, fid in user_friends.values:

        if uid in added:
            v1 = added[uid]
        else:
            v1 = _graph.add_vertex()
            _graph.vp.id[v1] = uid
            _graph.vp.type[v1] = "user"
            added[uid] = v1

        if fid in added:
            v2 = added[fid]
        else:
            v2 = _graph.add_vertex()
            _graph.vp.id[v2] = fid
            _graph.vp.type[v2] = "user"
            added[fid] = v2

        _graph.add_edge(v1, v2)
    return _graph


def graph_igraph(user_friends):
    _graph = ig.Graph(directed=False)
    # double|bool|object(dict or whatever)

    added = {}
    for uid, fid in user_friends.values:

        if uid in added:
            v1 = added[uid]
        else:
            v1 = _graph.add_vertex(id=fid, type="user")
            added[uid] = v1

        if fid in added:
            v2 = added[fid]
        else:
            v2 = _graph.add_vertex(id=fid, type="user")
            added[fid] = v2

        _graph.add_edge(v1, v2)
    return _graph

user_friends = pd.read_table('../data/user_friends.dat')

start = time.time()
g = graph_gt(user_friends)
end = time.time()

for v in g.get_vertices()[:10]:
    if g.vp.id[v] == 0:
        pdb.set_trace()
    # access to properties
    print "{}-{}".format(g.vp.id[v], g.vp.type[v])
print "time graphtool: {}".format(end - start)

start = time.time()
g = graph_igraph(user_friends)
end = time.time()
for vtx in g.vs[:10]:
    print "{}-{}".format(vtx["id"], vtx["type"])
print "time igraph: {}".format(end - start)
