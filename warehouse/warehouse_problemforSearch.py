import copy

from agentsearch.problem import Problem
from warehouse.actions import *
from warehouse.cell import Cell
from warehouse.warehouse_state import WarehouseState


class WarehouseProblemSearch(Problem[WarehouseState]):

    def __init__(self, initial_state: WarehouseState, goal_position: Cell):
        super().__init__(initial_state)
        self.actions = [ActionDown(), ActionUp(), ActionRight(), ActionLeft(), ActionNotMove()]
        self.goal_position = goal_position

    def get_actions(self, state: WarehouseState) -> list:
        valid_actions = []
        for action in self.actions:
            if action.is_valid(state):
                valid_actions.append(action)
        return valid_actions

    def get_successor(self, state: WarehouseState, action: Action) -> WarehouseState:
        successor = copy.deepcopy(state)
        action.execute(successor)
        return successor

    def is_goal(self, state: WarehouseState) -> bool:
        if self.goal_position.line == state.line_exit and self.goal_position.column == state.column_exit:
            return self.goal_position.line == state.line_forklift and self.goal_position.column == state.column_forklift

        if self.goal_position.line == state.line_forklift:
            return self.goal_position.column == state.column_forklift + 1 or self.goal_position.column == state.column_forklift - 1

        return self.goal_position.line == state.line_forklift and self.goal_position.column == state.column_forklift
