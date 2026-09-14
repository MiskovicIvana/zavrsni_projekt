# Ford-Fulkerson algoritam zasnovan na DFS-u
# koristimo strukturu stacka zbog LIFO (last in, first out) principa

# pseudokodovi:
# DFS, Ford-Fulkerson: https://www.cs.mcgill.ca/~akroit/math/compsci/Cormen%20Introduction%20to%20Algorithms.pdf

'''
DFS (G)
1 for each vertex u in G.V
2  u.color = WHITE
3  u.pi = NIL
4 time = 0
5 for each vertex u in G.V
6   if u.color == WHITE
7     DFS_VISIT (G, u)


DFS_VISIT (G, U)
1 time = time + 1
2 u.d = time
3 u.color = GRAY
4 for each v in G.Adj[u]
5   if v.color == WHITE
6     v.pi = u
7     DFS_VISIT (G, v)
8 u.color = BLACK
9 time = time + 1
10 u.f = time



FORD-FULKERSON (G, s, t)
1 for each edge (u, v) ∈ G.E
2   (u, v).f = 0
3 while there exists a path p from s to t in the residual network Gf
4   cf(p) = min {cf(u, v) : (u, v) is in p}
5   for each edge (u, v) in p
6     if (u, v) ∈ G.E
7 	(u, v).f = (u, v).f + cf(p)
8     else (v, u).f = (v, u).f − cf(p)
9 return f
'''

def dfs(residual, source, sink):
    n = len(residual)
    visited = [False] * n
    stack = [(source, [source])]

    while stack:
        u, path = stack.pop()
        if u == sink:
            return path
        if not visited[u]:
            visited[u] = True
            for v in range(n):
            # for v in reversed(range(n)):
            # redoslijed biranja čvorova može utjecati na broj iteracija
                if not visited[v] and residual[u][v] > 0:
                    stack.append((v, path + [v]))
    return None


def ford_fulkerson(capacity, source, sink):
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
        path = dfs(residual, source, sink)
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