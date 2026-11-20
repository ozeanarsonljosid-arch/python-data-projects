class Courier:
    def __init__(self, courier_id, position):
        self.courier_id = courier_id
        self.position = position
        self.available = True
        self.current_order = None
        self.path_remaining = []
        self.total_delivered = 0

    def assign_order(self, order, path):
        self.available = False
        self.current_order = order
        self.path_remaining = path[1:]  # skip current position

    def step(self):
        if not self.available and self.path_remaining:
            self.position = self.path_remaining.pop(0)
            if not self.path_remaining:
                return True  # arrived at destination
        return False

    def finish_order(self):
        self.available = True
        self.current_order = None
        self.path_remaining = []
        self.total_delivered += 1

    def __repr__(self):
        return (f"Courier(id={self.courier_id}, pos={self.position}, "
                f"available={self.available})")
