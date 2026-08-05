from enum import Enum, auto

class OrderState(Enum):
    IDLE = auto()
    ORDER_SENT = auto()
    WAITING_TRAIN = auto()
    TRAIN_PASSED = auto()
    WAITING_CLIENT_RETRIEVAL = auto()
    BARRIER_OPEN = auto()
    DONE = auto()

class OrderCycle:
    def __init__(self, rpi_id):
        self.state = OrderState.IDLE
        self.current_order = None
        self.rpi_id = rpi_id

    def on_order_created(self, order_data):
        self.current_order = order_data
        self.state = OrderState.ORDER_SENT

    def on_order_ready(self, payload):
        """Appelé quand on reçoit smartcheers/orders/ready"""
        if payload.get("rpiId") != self.rpi_id:
            return
        self.state = OrderState.WAITING_TRAIN
        # → activer servo bifurcation
        # → appeler le train (radio)

    def on_train_detected(self):
        if self.state == OrderState.WAITING_TRAIN:
            self.state = OrderState.TRAIN_PASSED
            self.state = OrderState.WAITING_CLIENT_RETRIEVAL

    def on_client_retrieved(self):
        if self.state == OrderState.WAITING_CLIENT_RETRIEVAL:
            self.state = OrderState.BARRIER_OPEN
            # → ouvrir barrière
            # → fermer bifurcation
            # → après un délai → DONE → reset

    def reset(self):
        self.state = OrderState.IDLE
        self.current_order = None