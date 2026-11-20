"""
City Instant Service Platform - Demo Script
Run: python demo.py
"""
import time
import random
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

from graph import Graph
from priority_queue import PriorityQueue
from bplus_tree import BPlusTree
from order import Order
from courier import Courier
from scheduler import Scheduler
from simulator import Simulator
from data_generator import generate_city_graph, generate_orders, generate_couriers
from visualize import visualize_path, visualize_scheduling, visualize_simulation


def print_header(title):
    print("\n")
    print("=" * 62)
    print(f"  {title}")
    print("=" * 62)


def print_subheader(title):
    print(f"\n  --- {title} ---")


def print_table(headers, rows, col_widths=None):
    if col_widths is None:
        col_widths = [max(len(str(h)), max(len(str(r[i])) for r in rows)) + 2
                      for i, h in enumerate(headers)]
    header_line = "  " + "".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("  " + "-" * sum(col_widths))
    for row in rows:
        print("  " + "".join(str(v).ljust(w) for v, w in zip(row, col_widths)))


# ============================================================
# Part 1: City Network & Shortest Path
# ============================================================
def demo_part1():
    print_header("Part 1: City Network Construction & Shortest Path (Dijkstra)")

    g = generate_city_graph(num_nodes=10, num_edges=18, seed=1)
    print(f"\n  Generated city network: 10 nodes, 18 edges (undirected weighted graph)")
    print(f"  Adjacency list representation, edge weights represent travel time\n")

    print_subheader("1.1 Shortest Path Computation")
    test_pairs = [(0, 5), (2, 9), (1, 7)]
    rows = []
    for src, dst in test_pairs:
        path, cost = g.dijkstra(src, dst)
        path_str = " -> ".join(map(str, path)) if path else "unreachable"
        rows.append([f"{src} -> {dst}", path_str, cost])
    print_table(["Route", "Shortest Path", "Cost"], rows, [12, 30, 8])

    print_subheader("1.2 Dynamic Edge Update")
    src, dst = 0, 5
    path_before, cost_before = g.dijkstra(src, dst)
    print(f"  Before update: {src}->{dst} cost = {cost_before}, path = {path_before}")

    if path_before and len(path_before) >= 2:
        u, v = path_before[0], path_before[1]
        old_weight = g.adj[u][v]
        g.update_edge(u, v, 100)
        path_after, cost_after = g.dijkstra(src, dst)
        print(f"  Update edge ({u},{v}) weight: {old_weight} -> 100")
        print(f"  After update:  {src}->{dst} cost = {cost_after}, path = {path_after}")
        print(f"\n  -> Path changed dynamically, reflecting real-time road condition updates")

    print_subheader("1.3 Path Visualization")
    path_vis, cost_vis = g.dijkstra(0, 5)
    out = visualize_path(g, 0, 5, path_vis, cost_vis)
    print(f"  -> Path visualization saved to: {out}")

    print_subheader("1.4 Key Data Structures")
    print("  - Graph: adjacency list (dict of dict)")
    print("  - Dijkstra: custom min-heap priority queue")
    print("  - Time complexity: O((V+E) log V)")


# ============================================================
# Part 2: B+ Tree Disk Index
# ============================================================
def demo_part2():
    print_header("Part 2: B+ Tree Index for Large-Scale Order Storage")

    print("\n  Scenario: orders stored on disk, cannot fit all in memory")
    print("  Solution: B+ Tree index (order=4), each node read/write = 1 disk IO\n")

    tree = BPlusTree(order=4, storage_dir="demo_bplus_storage")
    random.seed(42)
    n = 500
    data = [(random.randint(1, 1000), f"order_{i}") for i in range(n)]

    print_subheader("2.1 Insert Performance")
    tree.reset_io_count()
    for k, v in data:
        tree.insert(k, v)
    print(f"  Inserted {n} records")
    print(f"  Total disk IO: {tree.io_count}")
    print(f"  Avg IO per insert: {tree.io_count / n:.2f}")

    print_subheader("2.2 Point Search vs Brute Force")
    test_keys = [data[i][0] for i in [10, 50, 100, 200, 400]]
    rows = []
    for k in test_keys:
        tree.reset_io_count()
        result = tree.search(k)
        rows.append([k, result if result else "N/A", tree.io_count, n])
    print_table(["Key", "Value", "B+ Tree IO", "Brute Force IO"], rows, [8, 14, 14, 16])
    print(f"\n  -> B+ Tree search: O(log_m N) IO,  Brute force: O(N) IO")

    print_subheader("2.3 Range Query")
    ranges = [(50, 100), (200, 400), (800, 1000)]
    rows = []
    for low, high in ranges:
        tree.reset_io_count()
        results = tree.range_query(low, high)
        rows.append([f"[{low}, {high}]", len(results), tree.io_count])
    print_table(["Range", "Results", "IO Count"], rows, [14, 10, 10])
    print(f"  -> Range query leverages leaf node linked list for sequential scan")

    print_subheader("2.4 Delete & Rebalance")
    tree.reset_io_count()
    tree.delete(data[0][0])
    print(f"  Delete key {data[0][0]}: IO count = {tree.io_count} (includes rebalance)")

    tree.clear_storage()

    print_subheader("2.5 Key Data Structures")
    print("  - B+ Tree (order=4): internal nodes store keys, leaves store key-value pairs")
    print("  - Leaf nodes linked via next pointer for efficient range scan")
    print("  - Disk IO simulated via JSON file per node")


# ============================================================
# Part 3: Order Scheduling & Priority
# ============================================================
def demo_part3():
    print_header("Part 3: Order Priority Scheduling System")

    g = generate_city_graph(num_nodes=10, num_edges=20, seed=1)
    scheduler = Scheduler(g)

    couriers_data = generate_couriers(num_couriers=4, num_nodes=10, seed=1)
    for c in couriers_data:
        scheduler.add_courier(Courier(c["id"], c["pos"]))

    orders_data = generate_orders(num_orders=12, num_nodes=10, time_span=10, seed=1)
    for o in orders_data:
        scheduler.add_order(Order(**o))

    print("\n  Priority formula (lower = higher priority):")
    print("  P = -(w1*urgency + w2*amount + w3*wait_time - w4*path_cost)")
    print(f"  Weights: urgency={scheduler.weights[0]}, amount={scheduler.weights[1]}, "
          f"wait={scheduler.weights[2]}, path_cost={scheduler.weights[3]}")

    print_subheader("3.1 Current Orders")
    rows = []
    for oid, order in scheduler.orders.items():
        rows.append([oid, order.src, order.dst, f"{order.amount:.0f}",
                     order.urgency, order.path_cost if order.path_cost != float('inf') else "N/A"])
    print_table(["ID", "From", "To", "Amount", "Urgency", "Path Cost"],
                rows, [6, 6, 6, 10, 10, 12])

    print_subheader("3.2 Top Priority Orders (time=5)")
    scheduler.refresh_priorities(5)
    top3 = scheduler.get_top_k_orders(3)
    for i, o in enumerate(top3, 1):
        print(f"  #{i}: Order {o.order_id} (urgency={o.urgency}, amount={o.amount:.0f}, "
              f"path={o.path}, cost={o.path_cost})")

    print_subheader("3.3 Order Assignment (Multi-round Simulation)")
    assigned_list = []
    round_num = 0
    while True:
        order, courier = scheduler.assign_top_order()
        if order is None:
            break
        order.complete_time = order.assigned_time + int(order.path_cost) + 2
        assigned_list.append((order, courier))
        round_num += 1
        if round_num >= 6:
            break
        if not any(c.available for c in scheduler.couriers.values()):
            for c in scheduler.couriers.values():
                c.finish_order()
            scheduler.current_time += 5

    rows = []
    for order, courier in assigned_list:
        rows.append([f"O{order.order_id}", f"C{courier.courier_id}",
                     f"{order.src}->{order.dst}", order.assigned_time,
                     order.complete_time])
    print_table(["Order", "Courier", "Route", "Assign T", "Complete T"],
                rows, [8, 10, 10, 10, 12])

    print_subheader("3.4 Scheduling Visualization")
    out = visualize_scheduling(scheduler, current_time=scheduler.current_time)
    print(f"  -> Scheduling visualization saved to: {out}")


# ============================================================
# Part 4: Simulation & Strategy Comparison
# ============================================================
def demo_part4():
    print_header("Part 4: System Simulation & Strategy Evaluation")

    graph = generate_city_graph(num_nodes=30, num_edges=80, seed=42)
    orders_data = generate_orders(num_orders=200, num_nodes=30, time_span=100, seed=42)
    couriers_data = generate_couriers(num_couriers=10, num_nodes=30, seed=42)

    print(f"\n  Simulation parameters:")
    print(f"    City: 30 nodes, 80 edges")
    print(f"    Orders: 200 (arriving over time span 0~100)")
    print(f"    Couriers: 10")
    print(f"    Simulation: discrete time steps\n")

    print_subheader("4.1 Strategy A: Multi-factor Priority Scheduling")
    print("  Considers: urgency(0.4) + amount(0.2) + wait_time(0.3) - path_cost(0.1)")
    couriers_a = [Courier(c["id"], c["pos"]) for c in couriers_data]
    orders_a = [Order(**o) for o in orders_data]
    sim_a = Simulator(graph, couriers_a, orders_a, strategy="priority")
    sim_a.run()

    print_subheader("4.2 Strategy B: FIFO (First Come First Served)")
    print("  Only considers arrival order, no priority differentiation")
    couriers_b = [Courier(c["id"], c["pos"]) for c in couriers_data]
    orders_b = [Order(**o) for o in orders_data]
    sim_b = Simulator(graph, couriers_b, orders_b, strategy="fifo")
    sim_b.run()

    print_subheader("4.3 Simulation Process Visualization")
    if sim_a.history:
        out = visualize_simulation(graph, sim_a.history)
        print(f"  -> Simulation visualization saved to: {out}")

    print_subheader("4.4 Results Comparison")
    headers = ["Metric", "Priority", "FIFO", "Winner"]
    sa, sb = sim_a.stats, sim_b.stats
    num_c = len(couriers_data)

    def winner(a, b, higher_better=True):
        if higher_better:
            return "Priority" if a > b else ("FIFO" if b > a else "Tie")
        else:
            return "Priority" if a < b else ("FIFO" if b < a else "Tie")

    util_a = sa.completed_orders / max(sa.total_steps * num_c, 1)
    util_b = sb.completed_orders / max(sb.total_steps * num_c, 1)

    rows = [
        ["Completed Orders", sa.completed_orders, sb.completed_orders,
         winner(sa.completed_orders, sb.completed_orders)],
        ["Total Revenue", f"{sa.total_revenue:.1f}", f"{sb.total_revenue:.1f}",
         winner(sa.total_revenue, sb.total_revenue)],
        ["Avg Wait Time", f"{sa.avg_wait_time():.2f}", f"{sb.avg_wait_time():.2f}",
         winner(sa.avg_wait_time(), sb.avg_wait_time(), False)],
        ["Avg Exec Time", f"{sa.avg_exec_time():.2f}", f"{sb.avg_exec_time():.2f}",
         winner(sa.avg_exec_time(), sb.avg_exec_time(), False)],
        ["Timeout Orders", sa.timeout_orders, sb.timeout_orders,
         winner(sa.timeout_orders, sb.timeout_orders, False)],
        ["Courier Utilization", f"{util_a:.2%}", f"{util_b:.2%}",
         winner(util_a, util_b)],
    ]
    print_table(headers, rows, [20, 12, 12, 10])

    print_subheader("4.5 Generating Comparison Chart...")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    metrics_bar = ["Completed\nOrders", "Timeout\nOrders"]
    vals_a = [sa.completed_orders, sa.timeout_orders]
    vals_b = [sb.completed_orders, sb.timeout_orders]
    x = range(len(metrics_bar))
    w = 0.35
    axes[0].bar([i - w/2 for i in x], vals_a, w, label="Priority", color="#4C72B0")
    axes[0].bar([i + w/2 for i in x], vals_b, w, label="FIFO", color="#DD8452")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(metrics_bar)
    axes[0].set_title("Order Completion")
    axes[0].legend()
    axes[0].set_ylabel("Count")

    metrics_time = ["Avg Wait\nTime", "Avg Exec\nTime"]
    vals_a2 = [sa.avg_wait_time(), sa.avg_exec_time()]
    vals_b2 = [sb.avg_wait_time(), sb.avg_exec_time()]
    axes[1].bar([i - w/2 for i in range(2)], vals_a2, w, label="Priority", color="#4C72B0")
    axes[1].bar([i + w/2 for i in range(2)], vals_b2, w, label="FIFO", color="#DD8452")
    axes[1].set_xticks(range(2))
    axes[1].set_xticklabels(metrics_time)
    axes[1].set_title("Time Metrics")
    axes[1].legend()
    axes[1].set_ylabel("Time Steps")

    metrics_other = ["Revenue", "Utilization(%)"]
    vals_a3 = [sa.total_revenue, util_a * 100]
    vals_b3 = [sb.total_revenue, util_b * 100]
    axes[2].bar([i - w/2 for i in range(2)], vals_a3, w, label="Priority", color="#4C72B0")
    axes[2].bar([i + w/2 for i in range(2)], vals_b3, w, label="FIFO", color="#DD8452")
    axes[2].set_xticks(range(2))
    axes[2].set_xticklabels(metrics_other)
    axes[2].set_title("Revenue & Utilization")
    axes[2].legend()

    plt.suptitle("Strategy Comparison: Priority vs FIFO", fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig("strategy_comparison.png", dpi=150, bbox_inches='tight')
    print("  -> Chart saved to: strategy_comparison.png")
    plt.close()

    print("\n  Conclusion:")
    print("  Priority scheduling outperforms FIFO by considering multiple factors,")
    print("  reducing timeouts and improving overall system efficiency.")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("\n" + "#" * 62)
    print("#" + " " * 60 + "#")
    print("#    City Instant Service Platform - System Demo    #")
    print("#" + " " * 60 + "#")
    print("#" * 62)
    print("\n  Modules:")
    print("    1. City network (Graph + Dijkstra)")
    print("    2. B+ Tree disk index (simulated IO)")
    print("    3. Priority scheduling (multi-factor priority queue)")
    print("    4. Simulation engine (strategy comparison)")
    print("\n  All data structures are implemented from scratch.\n")

    input("  Press Enter to start demo...")

    demo_part1()
    input("\n  Press Enter for next module...")

    demo_part3()
    input("\n  Press Enter for next module...")

    demo_part2()
    input("\n  Press Enter for next module...")

    demo_part4()

    print("\n" + "=" * 62)
    print("  Demo Complete!")
    print("=" * 62 + "\n")
