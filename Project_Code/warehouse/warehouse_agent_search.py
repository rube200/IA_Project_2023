from copy import copy
from typing import TypeVar

import numpy as np

import constants
from agentsearch.agent import Agent
from agentsearch.state import State
from warehouse.cell import Cell
from warehouse.heuristic_warehouse import HeuristicWarehouse
from warehouse.pair import Pair
from warehouse.warehouse_problemforSearch import WarehouseProblemSearch


class WarehouseAgentSearch(Agent):
    S = TypeVar('S', bound=State)

    def __init__(self, environment: S):
        super().__init__()
        self.initial_environment = environment
        self.heuristic = HeuristicWarehouse()
        self.forklifts = []
        self.products = []
        self.exit = None
        self.pairs = []
        for i in range(environment.rows):
            for j in range(environment.columns):
                if environment.matrix[i][j] == constants.FORKLIFT:
                    self.forklifts.append(Cell(i, j))
                elif environment.matrix[i][j] == constants.EXIT:
                    self.exit = Cell(i, j)
                elif environment.matrix[i][j] == constants.PRODUCT:
                    self.products.append(Cell(i, j))

        for a in self.forklifts:
            for p in self.products:
                self.pairs.append(Pair(a, p))

        for i in range(len(self.products) - 1):
            for j in range(i + 1, len(self.products)):
                self.pairs.append(Pair(self.products[i], self.products[j]))

        for p in self.products:
            self.pairs.append(Pair(p, self.exit))

        for a in self.forklifts:
            self.pairs.append(Pair(a, self.exit))

    def __str__(self) -> str:
        string = "Pairs:\n"
        for p in self.pairs:
            string += f"{p}\n"
        return string

    def calculate_pairs_distances(self):
        state = copy(self.initial_environment)
        state.allow_collisions = True
        for pair in self.pairs:
            pair_line = pair.cell1.line
            pair_column = pair.cell1.column

            if state.is_movable_cell(pair_line, pair_column):
                state.update_forklift_in_matrix(pair_line, pair_column)
            elif pair_column > 0 and state.is_movable_cell(pair_line, pair_column - 1):
                state.update_forklift_in_matrix(pair_line, pair_column - 1)
            elif pair_column < state.columns - 1 and state.is_movable_cell(pair_line, pair_column + 1):
                state.update_forklift_in_matrix(pair_line, pair_column + 1)
            else:
                state.update_forklift_in_matrix(pair_line, pair_column)

            problem = WarehouseProblemSearch(state, pair.cell2)
            solution = self.solve_problem(problem)
            pair.actions = solution.actions
            pair.invert_actions()
            pair.value = solution.cost

    def get_pair(self, cell1: Cell, cell2: Cell) -> (Pair | None, bool | None):
        for pair in self.pairs:
            if pair.is_pair(cell1, cell2):
                return pair, True
            elif pair.is_pair(cell2, cell1):
                return pair, False

        return None, None

    def get_distance(self, cell1: Cell, cell2: Cell) -> int:
        pair, _ = self.get_pair(cell1, cell2)
        if pair:
            return pair.value

        return 999


def read_state_from_txt_file(filename: str):
    with open(filename, 'r') as file:
        num_rows, num_columns = map(int, file.readline().split())
        int_puzzle = np.genfromtxt(file, dtype=int, delimiter=' ')
        return int_puzzle, num_rows, num_columns
