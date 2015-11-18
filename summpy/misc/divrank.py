#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import not_implemented_for


@not_implemented_for('multigraph')
def divrank(G, alpha=0.25, d=0.85, personalization=None,
            max_iter=100, tol=1.0e-6, nstart=None, weight='weight',
            dangling=None):
    '''
    Returns the DivRank (Diverse Rank) of the nodes in the graph.
    This code is based on networkx.pagerank.

    Args: (diff from pagerank)
      alpha: controls strength of self-link [0.0-1.0]
      d: the damping factor

    Reference:
      Qiaozhu Mei and Jian Guo and Dragomir Radev,
      DivRank: the Interplay of Prestige and Diversity in Information Networks,
      http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.174.7982
    '''

    if len(G) == 0:
        return {}

    if not G.is_directed():
        D = G.to_directed()
    else:
        D = G

    # Create a copy in (right) stochastic form
    W = nx.stochastic_graph(D, weight=weight)
    N = W.number_of_nodes()

    # self-link (DivRank)
    for n in W.nodes_iter():
        for n_ in W.nodes_iter():
            if n != n_ :
                if n_ in W[n]:
                    W[n][n_][weight] *= alpha
            else:
                if n_ not in W[n]:
                    W.add_edge(n, n_)
                W[n][n_][weight] = 1.0 - alpha

    # Choose fixed starting vector if not given
    if nstart is None:
        x = dict.fromkeys(W, 1.0 / N)
    else:
        # Normalized nstart vector
        s = float(sum(nstart.values()))
        x = dict((k, v / s) for k, v in nstart.items())

    if personalization is None:
        # Assign uniform personalization vector if not given
        p = dict.fromkeys(W, 1.0 / N)
    else:
        missing = set(G) - set(personalization)
        if missing:
            raise NetworkXError('Personalization dictionary '
                                'must have a value for every node. '
                                'Missing nodes %s' % missing)
        s = float(sum(personalization.values()))
        p = dict((k, v / s) for k, v in personalization.items())

    if dangling is None:
        # Use personalization vector if dangling vector not specified
        dangling_weights = p
    else:
        missing = set(G) - set(dangling)
        if missing:
            raise NetworkXError('Dangling node dictionary '
                                'must have a value for every node. '
                                'Missing nodes %s' % missing)
        s = float(sum(dangling.values()))
        dangling_weights = dict((k, v/s) for k, v in dangling.items())
    dangling_nodes = [n for n in W if W.out_degree(n, weight=weight) == 0.0]

    # power iteration: make up to max_iter iterations
    for _ in range(max_iter):
        xlast = x
        x = dict.fromkeys(xlast.keys(), 0)
        danglesum = d * sum(xlast[n] for n in dangling_nodes)
        for n in x:
            D_t = sum(W[n][nbr][weight] * xlast[nbr] for nbr in W[n])
            for nbr in W[n]:
                #x[nbr] += d * xlast[n] * W[n][nbr][weight]
                x[nbr] += (
                    d * (W[n][nbr][weight] * xlast[nbr] / D_t) * xlast[n]
                )
            x[n] += danglesum * dangling_weights[n] + (1.0 - d) * p[n]

        # check convergence, l1 norm
        err = sum([abs(x[n] - xlast[n]) for n in x])
        if err < N*tol:
            return x
    raise NetworkXError('divrank: power iteration failed to converge '
                        'in %d iterations.' % max_iter)


def divrank_scipy(G, alpha=0.25, d=0.85, personalization=None,
                  max_iter=100, tol=1.0e-6, nstart=None, weight='weight',
                  dangling=None):
    '''
    Returns the DivRank (Diverse Rank) of the nodes in the graph.
    This code is based on networkx.pagerank_scipy
    '''
    import scipy.sparse

    N = len(G)
    if N == 0:
        return {}

    nodelist = G.nodes()
    M = nx.to_scipy_sparse_matrix(G, nodelist=nodelist, weight=weight,
                                  dtype=float)
    S = scipy.array(M.sum(axis=1)).flatten()
    S[S != 0] = 1.0 / S[S != 0]
    Q = scipy.sparse.spdiags(S.T, 0, *M.shape, format='csr')
    M = Q * M

    # self-link (DivRank)
    M = scipy.sparse.lil_matrix(M)
    M.setdiag(0.0)
    M = alpha * M
    M.setdiag(1.0 - alpha)
    #print M.sum(axis=1)

    # initial vector
    x = scipy.repeat(1.0 / N, N)

    # Personalization vector
    if personalization is None:
        p = scipy.repeat(1.0 / N, N)
    else:
        missing = set(nodelist) - set(personalization)
        if missing:
            raise NetworkXError('Personalization vector dictionary '
                                'must have a value for every node. '
                                'Missing nodes %s' % missing)
        p = scipy.array([personalization[n] for n in nodelist],
                        dtype=float)
        p = p / p.sum()

    # Dangling nodes
    if dangling is None:
        dangling_weights = p
    else:
        missing = set(nodelist) - set(dangling)


        if missing:
            raise NetworkXError('Dangling node dictionary '
                                'must have a value for every node. '
                                'Missing nodes %s' % missing)
        # Convert the dangling dictionary into an array in nodelist order
        dangling_weights = scipy.array([dangling[n] for n in nodelist],
                                       dtype=float)
        dangling_weights /= dangling_weights.sum()
    is_dangling = scipy.where(S == 0)[0]

    # power iteration: make up to max_iter iterations
    for _ in range(max_iter):
        xlast = x
        D_t =  M * x
        x = (
            d * (x / D_t * M * x + sum(x[is_dangling]) * dangling_weights)
            + (1.0 - d) * p
        )
        # check convergence, l1 norm
        err = scipy.absolute(x - xlast).sum()
        if err < N * tol:
            return dict(zip(nodelist, map(float, x)))

    raise NetworkXError('divrank_scipy: power iteration failed to converge '
                        'in %d iterations.' % max_iter)


if __name__ == '__main__':

    g = nx.Graph()

    # this network appears in the reference.
    edges = {
        1: [2, 3, 6, 7, 8, 9],
        2: [1, 3, 10, 11, 12],
        3: [1, 2, 15, 16, 17],
        4: [11, 13, 14],
        5: [17, 18, 19, 20],
        6: [1],
        7: [1],
        8: [1],
        9: [1],
        10: [2],
        11: [4],
        12: [2],
        13: [4],
        14: [4],
        15: [3],
        16: [3],
        17: [3, 5],
        18: [5],
        19: [5],
        20: [5]
    }

    for u, vs in edges.iteritems():
        for v in vs:
            g.add_edge(u, v)

    scores = nx.pagerank(g)
    print '# PageRank'
    print '# rank: node score'
    #print sum(scores.values())
    for i, n in enumerate(sorted(scores, key=lambda n: scores[n], reverse=True)):
        print '# {}: {} {}'.format(i+1, n, scores[n])

    scores = divrank(g)
    print '\n# DivRank'
    #print sum(scores.values())
    print '# rank: node score'
    for i, n in enumerate(sorted(scores, key=lambda n: scores[n], reverse=True)):
        print '# {}: {} {}'.format(i+1, n, scores[n])

    scores = divrank_scipy(g)
    print '\n# DivRank (scipy)'
    #print sum(scores.values())
    print '# rank: node score'
    for i, n in enumerate(sorted(scores, key=lambda n: scores[n], reverse=True)):
        print '# {}: {} {}'.format(i+1, n, scores[n])
