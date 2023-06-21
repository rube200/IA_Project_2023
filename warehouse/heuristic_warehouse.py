from agentsearch.heuristic import Heuristic
from warehouse.warehouse_problemforSearch import WarehouseProblemSearch
from warehouse.warehouse_state import WarehouseState


class HeuristicWarehouse(Heuristic[WarehouseProblemSearch, WarehouseState]):

    def __init__(self):
        super().__init__()

    def compute(self, state: WarehouseState) -> float:
        line_forklift, column_forklift = state.get_current_forklift()
        return abs(line_forklift - self.problem.goal_position.line) + abs(column_forklift - self.problem.goal_position.column)

    def __str__(self):
        return "Distance to goal position"

