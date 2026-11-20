import random
from graph import Graph
from order import Order
from courier import Courier


def generate_city_graph(num_nodes=30, num_edges=80, seed=42):
    """Generate a connected random city graph."""
    random.seed(seed)
    g = Graph()

    for i in range(num_nodes):
        g.add_node(i)

    # Ensure connectivity with a spanning tree
    nodes = list(range(num_nodes))
    random.shuffle(nodes)
    for i in range(1, num_nodes):
        weight = random.randint(1, 15)
        g.add_edge(nodes[i - 1], nodes[i], weight)

    # Add extra edges
    edges_added = num_nodes - 1
    while edges_added < num_edges:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        if u != v and v not in g.adj[u]:
            weight = random.randint(1, 20)
            g.add_edge(u, v, weight)
            edges_added += 1

    return g


def generate_orders(num_orders=200, num_nodes=30, time_span=100, seed=42):
    """Generate random orders."""
    random.seed(seed)
    orders_data = []
    for i in range(num_orders):
        src = random.randint(0, num_nodes - 1)
        dst = random.randint(0, num_nodes - 1)
        while dst == src:
            dst = random.randint(0, num_nodes - 1)

        create_time = random.randint(0, time_span)
        amount = round(random.uniform(10, 100), 2)
        urgency = random.randint(1, 5)
        deadline = create_time + random.randint(20, 60)

        orders_data.append({
            "order_id": i,
            "create_time": create_time,
            "src": src,
            "dst": dst,
            "amount": amount,
            "urgency": urgency,
            "deadline": deadline
        })

    return orders_data


def generate_couriers(num_couriers=10, num_nodes=30, seed=42):
    """Generate random couriers."""
    random.seed(seed)
    couriers_data = []
    for i in range(num_couriers):
        pos = random.randint(0, num_nodes - 1)
        couriers_data.append({"id": i, "pos": pos})
    return couriers_data
