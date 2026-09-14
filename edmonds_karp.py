# Edmonds-Karp algoritam zasnovan na BFS-u
# koristimo strukturu reda (queue) zbog FIFO

# pseudokodovi:
# BFS: https://www.cs.mcgill.ca/~akroit/math/compsci/Cormen%20Introduction%20to%20Algorithms.pdf
# Edmonds-Karp: https://www.cs.cornell.edu/courses/cs4820/2018sp/handouts/edmondskarp.pdf

'''
BFS(G, s)
1 for each vertex u ∈ G.V - {s}
2   u.color = WHITE
3   u.d = ∞
4   u.π NIL
5 s.color = GRAY
6 s.d = 0
7 s.π NIL
8 Q = Ø
9 ENQUEUE(Q, s)
10 while Q ≠ Ø
11   u = DEQUEUE(Q)
12   for each vertex v in G.Adj[u]  // nađi susjede od u
13 	if v.color == WHITE  // je li v pronađen?
14 	  v.color = GRAY
15 	  v.d = u.d + 1
16 	  v.π = u
17 	  ENQUEUE(Q, v)  // v je na granici
18   u.color = BLACK  // u je iza granice



EDMONDS-KARP (G = (V, E, s, t)) 
1 f=0
2 while(true)
3   Gf = residual network of G with flow f
4   if Gf has no s-t augmenting paths
5     break 
6   P = augmenting path for Gf with the minimum number of edges
7   c = minumum edge capacity in path P 
8   augment f by adding c to the flow through each edge of P
9 return f
'''

from collections import deque


def bfs(residual, source, sink):
    n = len(residual)
    visited = [False] * n
    parent = [-1] * n
    queue = deque([source])
    visited[source] = True

    while queue:
        u = queue.popleft()
        if u == sink:
            path = []
            curr = sink
            while curr != -1:
                path.append(curr)
                curr = parent[curr]
            path.reverse()
            return path

        for v in range(n):
            if not visited[v] and residual[u][v] > 0:
                visited[v] = True
                parent[v] = u
                queue.append(v)
    return None


def edmonds_karp(capacity, source, sink):
    n = len(capacity)
    residual = [row[:] for row in capacity]
    flow = [[0] * n for _ in range(n)]
    max_flow = 0
    iterations = 0

    states = [{
        "iteration": 0,
        "flows": [row[:] for row in flow],
        "path": None,
        "c_min": 0,
    }]

    while True:
        path = bfs(residual, source, sink)
        if path is None:
            break

        iterations += 1
        path_edges = list(zip(path[:-1], path[1:]))
        c_min = min(residual[u][v] for u, v in path_edges)

        for u, v in path_edges:
            if capacity[u][v] > 0:
                flow[u][v] += c_min
            else:
                flow[v][u] -= c_min

            residual[u][v] -= c_min
            residual[v][u] += c_min

        max_flow += c_min
        states.append({
            "iteration": iterations,
            "flows": [row[:] for row in flow],
            "path": path,
            "c_min": c_min,
        })

    return max_flow, states