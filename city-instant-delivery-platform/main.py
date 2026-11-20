from graph import Graph
from priority_queue import PriorityQueue
from bplus_tree import BPlusTree
from order import Order
from courier import Courier
from scheduler import Scheduler
from simulator import Simulator, run_comparison
from data_generator import generate_city_graph, generate_orders, generate_couriers


def demo_graph():
    print("\n" + "=" * 60)
    print("Module 1: City Network & Shortest Path")
    print("=" * 60)
    g = generate_city_graph(num_nodes=10, num_edges=20, seed=1)
    print(f"Generated graph: {g}")
    print(f"Nodes: {g.get_nodes()}")

    src, dst = 0, 5
    path, cost = g.dijkstra(src, dst)
    print(f"\nShortest path from {src} to {dst}: {path}")
    print(f"Cost: {cost}")

    print("\nUpdate edge (0,1) weight to 100:")
    if 1 in g.adj[0]:
        g.update_edge(0, 1, 100)
        path2, cost2 = g.dijkstra(src, dst)
        print(f"New shortest path from {src} to {dst}: {path2}")
        print(f"New cost: {cost2}")


def demo_priority_queue():
    print("\n" + "=" * 60)
    print("Module 1: Priority Queue & Order Scheduling")
    print("=" * 60)
    g = generate_city_graph(num_nodes=10, num_edges=20, seed=1)
    scheduler = Scheduler(g)

    courier_data = generate_couriers(num_couriers=3, num_nodes=10, seed=1)
    for c in courier_data:
        scheduler.add_courier(Courier(c["id"], c["pos"]))

    orders_data = generate_orders(num_orders=8, num_nodes=10, time_span=10, seed=1)
    for o in orders_data:
        scheduler.add_order(Order(**o))

    scheduler.current_time = 5
    scheduler.refresh_priorities(5)

    print("\nTop priority order:")
    top = scheduler.get_top_order()
    print(f"  {top}")

    print(f"\nTop 3 orders:")
    top3 = scheduler.get_top_k_orders(3)
    for i, o in enumerate(top3, 1):
        print(f"  {i}. {o}")

    print(f"\nPath for order {top.order_id}: {top.path}, cost={top.path_cost}")


def demo_bplus_tree():
    print("\n" + "=" * 60)
    print("Module 2: B+ Tree Disk Index")
    print("=" * 60)
    tree = BPlusTree(order=4, storage_dir="bplus_demo_storage")

    print("Inserting 20 orders indexed by amount...")
    import random
    random.seed(42)
    test_data = [(random.randint(10, 200), f"order_{i}") for i in range(20)]
    for key, val in test_data:
        tree.insert(key, val)
    print(f"  IO count after inserts: {tree.io_count}")

    tree.reset_io_count()
    key = test_data[5][0]
    result = tree.search(key)
    print(f"\nSearch for key {key}: {result}")
    print(f"  IO count for search: {tree.io_count}")

    tree.reset_io_count()
    low, high = 50, 100
    results = tree.range_query(low, high)
    print(f"\nRange query [{low}, {high}]: {len(results)} results")
    for k, v in results[:5]:
        print(f"  key={k}, value={v}")
    if len(results) > 5:
        print(f"  ... ({len(results) - 5} more)")
    print(f"  IO count for range query: {tree.io_count}")

    tree.reset_io_count()
    tree.delete(key)
    print(f"\nDeleted key {key}, IO count: {tree.io_count}")
    print(f"Search after delete: {tree.search(key)}")

    tree.clear_storage()


def demo_simulation():
    print("\n" + "=" * 60)
    print("Module 3: Simulation & Strategy Comparison")
    print("=" * 60)
    graph = generate_city_graph(num_nodes=30, num_edges=80, seed=42)
    orders_data = generate_orders(num_orders=200, num_nodes=30, time_span=100, seed=42)
    couriers_data = generate_couriers(num_couriers=10, num_nodes=30, seed=42)

    print(f"\nSimulation setup:")
    print(f"  City nodes: 30, edges: 80")
    print(f"  Orders: 200, Couriers: 10")
    print(f"  Time span: 0-100\n")

    run_comparison(graph, couriers_data, orders_data)


def interactive_menu():
    print("\n" + "=" * 60)
    print("  City Instant Service Platform")
    print("=" * 60)
    print("\n1. Demo: City Network & Shortest Path")
    print("2. Demo: Priority Queue & Order Scheduling")
    print("3. Demo: B+ Tree Disk Index")
    print("4. Demo: Simulation & Strategy Comparison")
    print("5. Run All Demos")
    print("0. Exit")

    while True:
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            demo_graph()
        elif choice == "2":
            demo_priority_queue()
        elif choice == "3":
            demo_bplus_tree()
        elif choice == "4":
            demo_simulation()
        elif choice == "5":
            demo_graph()
            demo_priority_queue()
            demo_bplus_tree()
            demo_simulation()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    interactive_menu()
