from graph import Graph
from priority_queue import PriorityQueue
from order import Order
from courier import Courier
from scheduler import Scheduler


class SimulationStats:
    def __init__(self):
        self.completed_orders = 0
        self.total_revenue = 0.0
        self.total_wait_time = 0
        self.total_exec_time = 0
        self.timeout_orders = 0
        self.total_steps = 0

    def avg_wait_time(self):
        return self.total_wait_time / max(self.completed_orders, 1)

    def avg_exec_time(self):
        return self.total_exec_time / max(self.completed_orders, 1)

    def report(self, num_couriers):
        utilization = self.completed_orders / max(self.total_steps * num_couriers, 1)
        print(f"  Completed orders:    {self.completed_orders}")
        print(f"  Total revenue:       {self.total_revenue:.2f}")
        print(f"  Avg wait time:       {self.avg_wait_time():.2f}")
        print(f"  Avg exec time:       {self.avg_exec_time():.2f}")
        print(f"  Timeout orders:      {self.timeout_orders}")
        print(f"  Courier utilization: {utilization:.2%}")


class Simulator:
    """Discrete-time simulation engine."""

    def __init__(self, graph, couriers, orders, strategy="priority", priority_weights=None):
        """
        strategy: "priority" (weighted multi-factor) or "fifo" (first come first served)
        """
        self.graph = graph
        self.strategy = strategy

        if strategy == "fifo":
            weights = (0.0, 0.0, 1.0, 0.0)  # only wait_time matters = FIFO
        else:
            weights = priority_weights

        self.scheduler = Scheduler(graph, priority_weights=weights)

        for c in couriers:
            self.scheduler.add_courier(Courier(c.courier_id, c.position))

        self.all_orders = sorted(orders, key=lambda o: o.create_time)
        self.order_idx = 0
        self.active_couriers = list(self.scheduler.couriers.values())
        self.stats = SimulationStats()
        self.current_time = 0
        self.history = []

    def run(self, max_time=None):
        """Run simulation until all orders processed or max_time reached."""
        if max_time is None:
            max_time = self.all_orders[-1].create_time + 200 if self.all_orders else 100

        while self.current_time <= max_time:
            self._step()
            self.current_time += 1
            self.stats.total_steps += 1

            # End early if all orders done and no active deliveries
            if self.order_idx >= len(self.all_orders):
                all_free = all(c.available for c in self.active_couriers)
                if all_free and self.scheduler.order_queue.is_empty():
                    break

        # Mark remaining queued orders as timeout
        while not self.scheduler.order_queue.is_empty():
            _, oid, order = self.scheduler.order_queue.extract_min()
            if order.status == "pending":
                order.status = "timeout"
                self.stats.timeout_orders += 1

    def _step(self):
        # 1. Arrive new orders
        while (self.order_idx < len(self.all_orders) and
               self.all_orders[self.order_idx].create_time <= self.current_time):
            order = self.all_orders[self.order_idx]
            self.scheduler.add_order(order)
            self.order_idx += 1

        # 2. Refresh priorities (wait time changes)
        self.scheduler.refresh_priorities(self.current_time)

        # 3. Assign orders to available couriers
        while True:
            order, courier = self.scheduler.assign_top_order()
            if order is None:
                break

        # 4. Advance delivering couriers
        for courier in self.active_couriers:
            if not courier.available:
                arrived = courier.step()
                if arrived:
                    order = courier.current_order
                    order.status = "completed"
                    order.complete_time = self.current_time
                    courier.finish_order()

                    wait_time = order.assigned_time - order.create_time
                    exec_time = order.complete_time - order.assigned_time
                    self.stats.completed_orders += 1
                    self.stats.total_revenue += order.amount
                    self.stats.total_wait_time += wait_time
                    self.stats.total_exec_time += exec_time

        # 5. Check timeouts for pending orders
        for oid, order in list(self.scheduler.orders.items()):
            if order.status == "pending" and self.current_time > order.deadline:
                order.status = "timeout"
                self.stats.timeout_orders += 1
                self.scheduler.order_queue.remove(oid)

        # 6. Record history snapshot
        self._record_snapshot()


    def _record_snapshot(self):
        pending_count = sum(1 for o in self.scheduler.orders.values() if o.status == "pending")
        courier_positions = {c.courier_id: c.position for c in self.active_couriers}
        courier_status = {c.courier_id: ('delivering' if not c.available else 'idle')
                          for c in self.active_couriers}
        active_paths = [(c.courier_id, [c.position] + c.path_remaining)
                        for c in self.active_couriers if not c.available and c.path_remaining]

        self.history.append({
            'time': self.current_time,
            'courier_positions': courier_positions,
            'courier_status': courier_status,
            'pending_count': pending_count,
            'completed_count': self.stats.completed_orders,
            'timeout_count': self.stats.timeout_orders,
            'active_paths': active_paths,
        })


def run_comparison(graph, couriers_data, orders_data):
    """Run both strategies and compare results."""
    print("=" * 60)
    print("Strategy A: Priority-based scheduling")
    print("=" * 60)
    couriers_a = [Courier(c["id"], c["pos"]) for c in couriers_data]
    orders_a = [Order(**o) for o in orders_data]
    sim_a = Simulator(graph, couriers_a, orders_a, strategy="priority")
    sim_a.run()
    sim_a.stats.report(len(couriers_a))

    print()
    print("=" * 60)
    print("Strategy B: FIFO scheduling")
    print("=" * 60)
    couriers_b = [Courier(c["id"], c["pos"]) for c in couriers_data]
    orders_b = [Order(**o) for o in orders_data]
    sim_b = Simulator(graph, couriers_b, orders_b, strategy="fifo")
    sim_b.run()
    sim_b.stats.report(len(couriers_b))

    return sim_a.stats, sim_b.stats
