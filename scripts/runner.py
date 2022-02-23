from prodict import Prodict

class Runner:
    all_actions = Prodict({})
    all_configs = Prodict({})
    last_window_amount_by_bot = Prodict({})
    current_active_window = None
    next_action = None

    def __init__(self):
        self.all_actions = Prodict({})
        self.all_configs = Prodict({})
        self.last_window_amount_by_bot = Prodict({})
        self.current_active_window = None
        self.next_action = None