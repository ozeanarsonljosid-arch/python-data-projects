from priority_queue import PriorityQueue


class Graph:
    """Weighted directed graph using adjacency list."""

    def __init__(self):
        self.adj = {}  # node_id -> {neighbor_id: weight}

    def add_node(self, node_id):
        if node_id not in self.adj:
            self.adj[node_id] = {}

    def remove_node(self, node_id):
        if node_id not in self.adj:
            return False
        del self.adj[node_id]
        for neighbors in self.adj.values():
            if node_id in neighbors:
                del neighbors[node_id]
        return True

    def add_edge(self, u, v, weight):
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = weight
        self.adj[v][u] = weight  # undirected

    def update_edge(self, u, v, weight):
        if u in self.adj and v in self.adj[u]:
            self.adj[u][v] = weight
            self.adj[v][u] = weight
            return True
        return False

    def remove_edge(self, u, v):
        removed = False
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
            removed = True
        if v in self.adj and u in self.adj[v]:
            del self.adj[v][u]
            removed = True
        return removed

    def get_nodes(self):
        return list(self.adj.keys())

    def get_neighbors(self, node_id):
        return self.adj.get(node_id, {})

    def dijkstra(self, src, dst):
        """Returns (path, cost) or (None, float('inf')) if unreachable."""
        if src not in self.adj or dst not in self.adj:
            return None, float('inf')

        dist = {}
        prev = {}
        pq = PriorityQueue()

        dist[src] = 0
        pq.insert(src, 0)

        while not pq.is_empty():
            cost, node, _ = pq.extract_min()

            if cost > dist.get(node, float('inf')):
                continue

            if node == dst:
                break

            for neighbor, weight in self.adj[node].items():
                new_dist = cost + weight
                if new_dist < dist.get(neighbor, float('inf')):
                    dist[neighbor] = new_dist
                    prev[neighbor] = node
                    if pq.contains(neighbor):
                        pq.update_priority(neighbor, new_dist)
                    else:
                        pq.insert(neighbor, new_dist)

        if dst not in dist:
            return None, float('inf')

        path = []
        node = dst
        while node is not None:
            path.append(node)
            node = prev.get(node)
        path.reverse()
        return path, dist[dst]

    def __repr__(self):
        return f"Graph(nodes={len(self.adj)}, edges={sum(len(v) for v in self.adj.values()) // 2})"
