class Order:
    def __init__(self, order_id, create_time, src, dst, amount, urgency, deadline):
        self.order_id = order_id
        self.create_time = create_time
        self.src = src
        self.dst = dst
        self.amount = amount
        self.urgency = urgency  # 1-5, 5 is most urgent
        self.deadline = deadline
        self.status = "pending"  # pending / assigned / delivering / completed / timeout
        self.assigned_time = None
        self.complete_time = None
        self.courier_id = None
        self.path = None
        self.path_cost = None

    def __repr__(self):
        return (f"Order(id={self.order_id}, src={self.src}, dst={self.dst}, "
                f"amount={self.amount}, urgency={self.urgency}, status={self.status})")
