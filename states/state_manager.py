from states.state import State
from collections import deque
class GameStateManager:
    def __init__(self) -> None:
        states: list[State] = []
        self.states = deque(states)

    def push(self, state: State, asset_cache):
        self.states.append(state)
        state.on_enter(asset_cache)

    def pop(self) -> State:
        s = self.states.pop()
        s.on_exit()
        return s
    
    def peek(self) -> State:
        return self.states[-1]