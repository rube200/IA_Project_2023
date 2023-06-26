from copy import copy

from agentsearch.action import Action
from warehouse.cell import Cell


class DynamicForklift:
    def __init__(self, initial_cell: Cell):
        self.current_position = copy(initial_cell)
        self.in_exit = False
        self.move_tries = 0
        self.targets_info = []
        self.current_action_index = 0
        self.current_target_index = 0

    def append_target(self, cell: Cell, info: [int | Action]):
        self.targets_info.append((cell, info))

    def get_actions(self) -> [Action]:
        if self.current_target_index >= len(self.targets_info):
            return None

        _, actions = self.targets_info[self.current_target_index]
        return actions

    def get_action(self) -> None | Action:
        actions = self.get_actions()
        if not actions or self.current_action_index >= len(actions):
            return None

        return actions[self.current_action_index]

    def get_target(self) -> Cell | None:
        if not self.have_target():
            return None

        target, _ = self.targets_info[self.current_target_index]
        return target

    def get_target_cost(self) -> (Cell, int):
        if not self.have_target():
            return None

        _, cost = self.targets_info[self.current_target_index]
        return cost

    def have_target(self) -> bool:
        return self.current_target_index < len(self.targets_info)

    def have_more_targets(self) -> bool:
        return self.current_target_index + 1 < len(self.targets_info)

    def next_action(self):
        self.current_action_index += 1

    def next_target(self):
        self.current_target_index += 1
        self.current_action_index = 0

    def update_target(self, actions: [Action]):
        target = self.get_target()
        if target is None:
            return

        self.targets_info[self.current_target_index] = (target, actions)
        self.current_action_index = 0
