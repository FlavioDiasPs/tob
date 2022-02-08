from prodict import Prodict

class Runner:
    all_actions = Prodict({})
    all_configs = Prodict({})
    last_window_amount_by_bot = Prodict({})
    current_active_window = None
    next_action = None