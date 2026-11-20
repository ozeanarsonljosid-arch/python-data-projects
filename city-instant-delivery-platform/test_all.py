"""
Test cases for City Instant Service Platform.
Run: python test_all.py
"""

from graph import Graph
from priority_queue import PriorityQueue
from bplus_tree import BPlusTree
from order import Order
from courier import Courier
from scheduler import Scheduler
from simulator import Simulator, run_comparison
from data_generator import generate_city_graph, generate_orders, generate_couriers

passed = 0
failed = 0


def check(condition, msg):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {msg}")
    else:
        failed += 1
        print(f"  [FAIL] {msg}")


# ==============================================================
# Test 1: Graph - basic operations
# ==============================================================
def test_graph_basic():
    print("\n[Test] Graph - basic operations")
    g = Graph()
    g.add_node(0)
    g.add_node(1)
    g.add_node(2)
    check(len(g.get_nodes()) == 3, "add 3 nodes")

    g.add_edge(0, 1, 5)
    g.add_edge(1, 2, 3)
    check(g.get_neighbors(0) == {1: 5}, "edge 0->1 weight 5")
    check(g.get_neighbors(1) == {0: 5, 2: 3}, "node 1 has 2 neighbors")

    g.update_edge(0, 1, 10)
    check(g.adj[0][1] == 10 and g.adj[1][0] == 10, "update edge weight to 10")

    g.remove_edge(0, 1)
    check(1 not in g.adj[0], "remove edge 0-1")

    g.remove_node(2)
    check(2 not in g.adj, "remove node 2")
    check(2 not in g.adj.get(1, {}), "node 2 removed from neighbors of 1")


# ==============================================================
# Test 2: Graph - Dijkstra shortest path
# ==============================================================
def test_graph_dijkstra():
    print("\n[Test] Graph - Dijkstra shortest path")
    g = Graph()
    # 0 --1-- 1 --1-- 2
    # |               |
    # 10              1
    # |               |
    # 3 ------1------ 4
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(0, 3, 10)
    g.add_edge(2, 4, 1)
    g.add_edge(3, 4, 1)

    path, cost = g.dijkstra(0, 4)
    check(cost == 3, f"shortest cost 0->4 is 3 (got {cost})")
    check(path == [0, 1, 2, 4], f"shortest path 0->4 is [0,1,2,4] (got {path})")

    path, cost = g.dijkstra(0, 3)
    check(cost == 4, f"shortest cost 0->3 is 4 (got {cost})")
    check(path == [0, 1, 2, 4, 3], f"path 0->3 goes through 4 (got {path})")

    path, cost = g.dijkstra(0, 99)
    check(path is None and cost == float('inf'), "unreachable node returns None/inf")

    g2 = Graph()
    g2.add_node(0)
    path, cost = g2.dijkstra(0, 0)
    check(cost == 0, "same source and destination cost is 0")


# ==============================================================
# Test 3: Priority Queue - basic operations
# ==============================================================
def test_priority_queue_basic():
    print("\n[Test] Priority Queue - basic operations")
    pq = PriorityQueue()
    check(pq.is_empty(), "new queue is empty")

    pq.insert("a", 5)
    pq.insert("b", 2)
    pq.insert("c", 8)
    pq.insert("d", 1)
    check(pq.size() == 4, "inserted 4 items, size=4")

    top = pq.peek()
    check(top[1] == "d" and top[0] == 1, f"peek returns min priority item 'd' (got {top})")

    extracted = pq.extract_min()
    check(extracted[1] == "d", "extract_min returns 'd'")
    check(pq.size() == 3, "size is 3 after extract")

    pq.update_priority("a", 0)
    top = pq.peek()
    check(top[1] == "a" and top[0] == 0, "after update 'a' to 0, it becomes min")

    pq.remove("a")
    check(not pq.contains("a"), "remove 'a' works")
    check(pq.size() == 2, "size is 2 after remove")


# ==============================================================
# Test 4: Priority Queue - top_k
# ==============================================================
def test_priority_queue_topk():
    print("\n[Test] Priority Queue - top_k")
    pq = PriorityQueue()
    for i in range(10):
        pq.insert(f"item_{i}", 10 - i)

    top3 = pq.top_k(3)
    check(len(top3) == 3, "top_k(3) returns 3 items")
    check(top3[0][1] == "item_9", f"1st is item_9 (priority 1), got {top3[0][1]}")
    check(top3[1][1] == "item_8", f"2nd is item_8 (priority 2), got {top3[1][1]}")
    check(top3[2][1] == "item_7", f"3rd is item_7 (priority 3), got {top3[2][1]}")
    check(pq.size() == 10, "top_k does not modify queue size")

    top0 = pq.top_k(0)
    check(len(top0) == 0, "top_k(0) returns empty list")

    top20 = pq.top_k(20)
    check(len(top20) == 10, "top_k(20) on 10 items returns 10")


# ==============================================================
# Test 5: B+ Tree - insert and search
# ==============================================================
def test_bplus_insert_search():
    print("\n[Test] B+ Tree - insert and search")
    tree = BPlusTree(order=4, storage_dir="test_bplus_1")

    keys = [50, 20, 80, 10, 40, 60, 90, 30, 70, 5]
    for k in keys:
        tree.insert(k, f"val_{k}")

    check(tree.search(50) == "val_50", "search 50 found")
    check(tree.search(5) == "val_5", "search 5 (min) found")
    check(tree.search(90) == "val_90", "search 90 (max) found")
    check(tree.search(99) is None, "search 99 (non-existent) returns None")
    check(tree.search(0) is None, "search 0 (non-existent) returns None")

    tree.insert(50, "val_50_updated")
    check(tree.search(50) == "val_50_updated", "insert duplicate key updates value")

    tree.clear_storage()


# ==============================================================
# Test 6: B+ Tree - range query
# ==============================================================
def test_bplus_range_query():
    print("\n[Test] B+ Tree - range query")
    tree = BPlusTree(order=4, storage_dir="test_bplus_2")

    for i in range(1, 51):
        tree.insert(i, f"order_{i}")

    results = tree.range_query(10, 20)
    result_keys = [k for k, v in results]
    check(len(results) == 11, f"range [10,20] has 11 items (got {len(results)})")
    check(result_keys == list(range(10, 21)), "range [10,20] keys correct")

    results = tree.range_query(1, 1)
    check(len(results) == 1 and results[0] == (1, "order_1"), "single-point range [1,1]")

    results = tree.range_query(100, 200)
    check(len(results) == 0, "range [100,200] out of bounds returns empty")

    results = tree.range_query(1, 50)
    check(len(results) == 50, "full range returns all 50 items")

    tree.clear_storage()


# ==============================================================
# Test 7: B+ Tree - delete and update
# ==============================================================
def test_bplus_delete_update():
    print("\n[Test] B+ Tree - delete and update")
    tree = BPlusTree(order=4, storage_dir="test_bplus_3")

    for i in range(1, 21):
        tree.insert(i, f"val_{i}")

    tree.delete(10)
    check(tree.search(10) is None, "delete 10 then search returns None")

    tree.delete(1)
    check(tree.search(1) is None, "delete min key 1")

    tree.delete(20)
    check(tree.search(20) is None, "delete max key 20")

    check(tree.search(5) == "val_5", "undeleted key 5 still exists")

    tree.update(5, "new_val_5")
    check(tree.search(5) == "new_val_5", "update key 5 value")

    check(tree.update(999, "x") is False, "update non-existent key returns False")

    tree.clear_storage()


# ==============================================================
# Test 8: B+ Tree - IO count
# ==============================================================
def test_bplus_io():
    print("\n[Test] B+ Tree - IO count (disk simulation)")
    tree = BPlusTree(order=4, storage_dir="test_bplus_4")

    for i in range(100):
        tree.insert(i, f"v{i}")

    tree.reset_io_count()
    tree.search(50)
    search_io = tree.io_count
    check(search_io > 0, f"search triggers disk IO (count={search_io})")
    check(search_io <= 10, f"search IO is bounded by tree height (count={search_io})")

    tree.reset_io_count()
    tree.range_query(20, 40)
    range_io = tree.io_count
    check(range_io > search_io, f"range query needs more IO ({range_io}) than point search ({search_io})")

    tree.clear_storage()


# ==============================================================
# Test 9: Scheduler - order management and priority
# ==============================================================
def test_scheduler():
    print("\n[Test] Scheduler - order management and priority")
    g = Graph()
    g.add_edge(0, 1, 5)
    g.add_edge(1, 2, 3)
    g.add_edge(0, 2, 10)

    sch = Scheduler(g)
    sch.current_time = 0

    o1 = Order(order_id=1, create_time=0, src=0, dst=2, amount=50, urgency=3, deadline=30)
    o2 = Order(order_id=2, create_time=0, src=0, dst=2, amount=80, urgency=5, deadline=20)
    o3 = Order(order_id=3, create_time=0, src=1, dst=2, amount=30, urgency=1, deadline=50)

    sch.add_order(o1)
    sch.add_order(o2)
    sch.add_order(o3)

    top = sch.get_top_order()
    check(top.order_id == 2, f"highest urgency+amount order 2 is top (got {top.order_id})")

    top3 = sch.get_top_k_orders(3)
    check(len(top3) == 3, "get_top_k_orders(3) returns 3")

    path, cost = sch.get_path(1)
    check(path is not None, "order 1 has computed path")
    check(cost == 8, f"order 1 path cost is 8 (0->1->2) (got {cost})")

    sch.remove_order(3)
    check(3 not in sch.orders, "remove_order(3) works")

    sch.update_order(1, amount=200)
    check(sch.orders[1].amount == 200, "update_order changes amount")


# ==============================================================
# Test 10: Scheduler - courier assignment
# ==============================================================
def test_scheduler_assignment():
    print("\n[Test] Scheduler - courier assignment")
    g = Graph()
    g.add_edge(0, 1, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 1)

    sch = Scheduler(g)
    sch.current_time = 0

    c1 = Courier(courier_id=1, position=0)
    c2 = Courier(courier_id=2, position=3)
    sch.add_courier(c1)
    sch.add_courier(c2)

    o1 = Order(order_id=1, create_time=0, src=1, dst=3, amount=50, urgency=3, deadline=30)
    sch.add_order(o1)

    order, courier = sch.assign_top_order()
    check(order is not None, "order assigned successfully")
    check(courier.courier_id == 1, f"nearest courier 1 (at node 0) assigned (got {courier.courier_id})")
    check(order.status == "assigned", "order status set to assigned")
    check(not courier.available, "courier marked unavailable")


# ==============================================================
# Test 11: Courier - step-by-step delivery
# ==============================================================
def test_courier_delivery():
    print("\n[Test] Courier - step-by-step delivery")
    c = Courier(courier_id=1, position=0)
    o = Order(order_id=1, create_time=0, src=0, dst=3, amount=50, urgency=3, deadline=30)
    o.path = [0, 1, 2, 3]

    c.assign_order(o, [0, 1, 2, 3])
    check(not c.available, "courier not available after assignment")
    check(c.path_remaining == [1, 2, 3], "path_remaining skips start node")

    arrived = c.step()
    check(c.position == 1, "after step 1, position=1")
    check(not arrived, "not arrived yet")

    c.step()
    check(c.position == 2, "after step 2, position=2")

    arrived = c.step()
    check(c.position == 3, "after step 3, position=3")
    check(arrived, "arrived at destination")

    c.finish_order()
    check(c.available, "courier available after finish")
    check(c.total_delivered == 1, "total_delivered incremented")


# ==============================================================
# Test 12: Simulator - basic run
# ==============================================================
def test_simulator_basic():
    print("\n[Test] Simulator - basic run")
    g = Graph()
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(2, 3, 1)

    couriers = [Courier(0, 0)]
    orders = [
        Order(order_id=0, create_time=0, src=0, dst=2, amount=30, urgency=3, deadline=20),
        Order(order_id=1, create_time=5, src=1, dst=3, amount=50, urgency=4, deadline=25),
    ]

    sim = Simulator(g, couriers, orders, strategy="priority")
    sim.run(max_time=50)

    check(sim.stats.completed_orders == 2, f"all 2 orders completed (got {sim.stats.completed_orders})")
    check(sim.stats.timeout_orders == 0, "no timeouts")
    check(sim.stats.total_revenue == 80, f"total revenue 80 (got {sim.stats.total_revenue})")


# ==============================================================
# Test 13: Simulator - timeout scenario
# ==============================================================
def test_simulator_timeout():
    print("\n[Test] Simulator - timeout scenario")
    g = Graph()
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)

    couriers = [Courier(0, 0)]
    orders = [
        Order(order_id=0, create_time=0, src=0, dst=2, amount=30, urgency=3, deadline=1),
    ]

    sim = Simulator(g, couriers, orders, strategy="priority")
    sim.run(max_time=30)

    total = sim.stats.completed_orders + sim.stats.timeout_orders
    check(total == 1, "order either completed or timed out")


# ==============================================================
# Test 14: Simulator - strategy comparison
# ==============================================================
def test_simulator_comparison():
    print("\n[Test] Simulator - strategy comparison (Priority vs FIFO)")
    graph = generate_city_graph(num_nodes=20, num_edges=50, seed=7)
    orders_data = generate_orders(num_orders=50, num_nodes=20, time_span=50, seed=7)
    couriers_data = generate_couriers(num_couriers=5, num_nodes=20, seed=7)

    couriers_a = [Courier(c["id"], c["pos"]) for c in couriers_data]
    orders_a = [Order(**o) for o in orders_data]
    sim_a = Simulator(graph, couriers_a, orders_a, strategy="priority")
    sim_a.run()

    couriers_b = [Courier(c["id"], c["pos"]) for c in couriers_data]
    orders_b = [Order(**o) for o in orders_data]
    sim_b = Simulator(graph, couriers_b, orders_b, strategy="fifo")
    sim_b.run()

    check(sim_a.stats.completed_orders > 0, f"priority strategy completed {sim_a.stats.completed_orders} orders")
    check(sim_b.stats.completed_orders > 0, f"FIFO strategy completed {sim_b.stats.completed_orders} orders")
    print(f"  [INFO] Priority: revenue={sim_a.stats.total_revenue:.1f}, "
          f"avg_wait={sim_a.stats.avg_wait_time():.2f}, timeout={sim_a.stats.timeout_orders}")
    print(f"  [INFO] FIFO:     revenue={sim_b.stats.total_revenue:.1f}, "
          f"avg_wait={sim_b.stats.avg_wait_time():.2f}, timeout={sim_b.stats.timeout_orders}")


# ==============================================================
# Test 15: Data Generator
# ==============================================================
def test_data_generator():
    print("\n[Test] Data Generator")
    g = generate_city_graph(num_nodes=15, num_edges=30, seed=0)
    check(len(g.get_nodes()) == 15, "generated 15 nodes")
    edge_count = sum(len(v) for v in g.adj.values()) // 2
    check(edge_count == 30, f"generated 30 edges (got {edge_count})")

    path, cost = g.dijkstra(0, 14)
    check(path is not None, "generated graph is connected (0 can reach 14)")

    orders = generate_orders(num_orders=100, num_nodes=15, time_span=50, seed=0)
    check(len(orders) == 100, "generated 100 orders")
    check(all(o["src"] != o["dst"] for o in orders), "no order has src == dst")
    check(all(0 <= o["urgency"] <= 5 for o in orders), "urgency in valid range")

    couriers = generate_couriers(num_couriers=5, num_nodes=15, seed=0)
    check(len(couriers) == 5, "generated 5 couriers")


# ==============================================================
# Run all tests
# ==============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Running All Test Cases")
    print("=" * 60)

    test_graph_basic()
    test_graph_dijkstra()
    test_priority_queue_basic()
    test_priority_queue_topk()
    test_bplus_insert_search()
    test_bplus_range_query()
    test_bplus_delete_update()
    test_bplus_io()
    test_scheduler()
    test_scheduler_assignment()
    test_courier_delivery()
    test_simulator_basic()
    test_simulator_timeout()
    test_simulator_comparison()
    test_data_generator()

    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 60)

    if failed > 0:
        exit(1)
