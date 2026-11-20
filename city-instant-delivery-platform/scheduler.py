from graph import Graph
from priority_queue import PriorityQueue
from order import Order
from courier import Courier


class Scheduler:
    """Order scheduling system integrating graph, priority queue, and couriers."""

    def __init__(self, graph, priority_weights=None):
        self.graph = graph
        self.order_queue = PriorityQueue()
        self.couriers = {}  # courier_id -> Courier
        self.orders = {}  # order_id -> Order
        self.current_time = 0

        # Priority weights: urgency, amount, wait_time, path_cost
        if priority_weights is None:
            self.weights = (0.4, 0.2, 0.3, 0.1)
        else:
            self.weights = priority_weights

    def add_courier(self, courier):
        self.couriers[courier.courier_id] = courier

    def remove_courier(self, courier_id):
        if courier_id in self.couriers:
            del self.couriers[courier_id]

    def add_order(self, order):
        self.orders[order.order_id] = order
        path, cost = self.graph.dijkstra(order.src, order.dst)
        order.path = path
        order.path_cost = cost
        priority = self._compute_priority(order)
        self.order_queue.insert(order.order_id, priority, order)

    def remove_order(self, order_id):
        self.order_queue.remove(order_id)
        if order_id in self.orders:
            del self.orders[order_id]

    def update_order(self, order_id, **kwargs):
        if order_id not in self.orders:
            return False
        order = self.orders[order_id]
        for k, v in kwargs.items():
            setattr(order, k, v)
        if 'src' in kwargs or 'dst' in kwargs:
            path, cost = self.graph.dijkstra(order.src, order.dst)
            order.path = path
            order.path_cost = cost
        priority = self._compute_priority(order)
        self.order_queue.update_priority(order_id, priority)
        return True

    def _compute_priority(self, order):
        """Lower value = higher priority."""
        w1, w2, w3, w4 = self.weights
        urgency_score = order.urgency / 5.0
        amount_score = min(order.amount / 100.0, 1.0)
        wait_time = max(self.current_time - order.create_time, 0)
        wait_score = min(wait_time / 30.0, 1.0)
        cost_score = min(order.path_cost / 50.0, 1.0) if order.path_cost != float('inf') else 1.0

        priority = -(w1 * urgency_score + w2 * amount_score + w3 * wait_score - w4 * cost_score)
        return priority

    def refresh_priorities(self, current_time):
        """Recompute all priorities (e.g. due to time change)."""
        self.current_time = current_time
        for order_id, order in self.orders.items():
            if order.status == "pending" and self.order_queue.contains(order_id):
                priority = self._compute_priority(order)
                self.order_queue.update_priority(order_id, priority)

    def get_top_order(self):
        """Get highest priority order."""
        result = self.order_queue.peek()
        if result:
            return result[2]  # the Order object
        return None

    def get_top_k_orders(self, k):
        """Get top-k highest priority orders."""
        results = self.order_queue.top_k(k)
        return [item[2] for item in results]

    def get_path(self, order_id):
        """Get execution path for an order."""
        if order_id in self.orders:
            order = self.orders[order_id]
            return order.path, order.path_cost
        return None, float('inf')

    def find_nearest_available_courier(self, order):
        """Find closest available courier to order's source."""
        best_courier = None
        best_cost = float('inf')
        for courier in self.couriers.values():
            if not courier.available:
                continue
            _, cost = self.graph.dijkstra(courier.position, order.src)
            if cost < best_cost:
                best_cost = cost
                best_courier = courier
        return best_courier, best_cost

    def assign_top_order(self):
        """Assign highest priority order to nearest available courier."""
        result = self.order_queue.peek()
        if result is None:
            return None, None

        order = result[2]
        courier, pickup_cost = self.find_nearest_available_courier(order)
        if courier is None:
            return None, None

        self.order_queue.extract_min()
        pickup_path, _ = self.graph.dijkstra(courier.position, order.src)
        full_path = pickup_path[:-1] + order.path if pickup_path and order.path else order.path

        order.status = "assigned"
        order.assigned_time = self.current_time
        order.courier_id = courier.courier_id
        courier.assign_order(order, full_path)

        return order, courier
