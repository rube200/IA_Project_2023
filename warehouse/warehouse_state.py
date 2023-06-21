import numpy as np
from PIL.ImageEnhance import Color
from numpy import ndarray

import constants
from agentsearch.state import State
from agentsearch.action import Action
from warehouse.cell import Cell


class WarehouseState(State[Action]):

    def __init__(self, matrix: ndarray, rows, columns):
        super().__init__()
        self.steps = 0

        self.rows = rows
        self.columns = columns
        self.current_forklift = -1
        self.forklifts = []
        self.matrix = np.full([self.rows, self.columns], fill_value=0, dtype=int)

        for i in range(self.rows):
            for j in range(self.columns):
                self.matrix[i][j] = matrix[i][j]
                if self.matrix[i][j] == constants.FORKLIFT:
                    self.forklifts.append(Cell(i, j))
                    self.current_forklift = len(self.forklifts) - 1
                elif self.matrix[i][j] == constants.EXIT:
                    self.line_exit = i
                    self.column_exit = j

    def choose_forklift_by_cell(self, cell: Cell) -> bool:
        forklift_index = self.get_forklift_index_by_cell(cell)
        if forklift_index == -1:
            return False

        self.current_forklift = forklift_index
        return True

    def get_forklift_index_by_cell(self, cell: Cell, ignore_index: int = -1) -> int:
        for i in range(len(self.forklifts)):
            if i == ignore_index:
                continue

            forklift = self.forklifts[i]
            if forklift.line == cell.line and forklift.column == cell.column:
                return i

        return -1

    def get_current_forklift(self) -> (int, int):
        forklift = self.forklifts[self.current_forklift]
        return forklift.line, forklift.column

    @staticmethod
    def is_movable_cell(target_cell: Cell) -> bool:
        return target_cell == constants.EMPTY or target_cell == constants.EXIT or target_cell == constants.FORKLIFT

    def can_move_up(self) -> bool:
        line_forklift, column_forklift = self.get_current_forklift()
        if line_forklift <= 0:
            return False

        target_cell = self.matrix[line_forklift - 1][column_forklift]
        return self.is_movable_cell(target_cell)

    def can_move_right(self) -> bool:
        line_forklift, column_forklift = self.get_current_forklift()
        if column_forklift == self.columns - 1:
            return False

        target_cell = self.matrix[line_forklift][column_forklift + 1]
        return self.is_movable_cell(target_cell)

    def can_move_down(self) -> bool:
        line_forklift, column_forklift = self.get_current_forklift()
        if line_forklift == self.rows - 1:
            return False

        target_cell = self.matrix[line_forklift + 1][column_forklift]
        return self.is_movable_cell(target_cell)

    def can_move_left(self) -> bool:
        line_forklift, column_forklift = self.get_current_forklift()
        if column_forklift <= 0:
            return False

        target_cell = self.matrix[line_forklift][column_forklift - 1]
        return self.is_movable_cell(target_cell)

    def update_forklift_in_matrix(self, new_line: int, new_column: int, increment_steps: bool = False):  # todo colisoes
        line_forklift, column_forklift = self.get_current_forklift()
        if line_forklift != self.line_exit or column_forklift != self.column_exit:
            another_forklift_index = self.get_forklift_index_by_cell(Cell(line_forklift, column_forklift), self.current_forklift)
            if another_forklift_index != -1:
                old_cell_state = constants.FORKLIFT
            else:
                old_cell_state = constants.EMPTY
        else:
            old_cell_state = constants.EXIT

        self.matrix[line_forklift][column_forklift] = old_cell_state
        self.forklifts[self.current_forklift] = Cell(new_line, new_column)
        self.matrix[new_line][new_column] = constants.FORKLIFT

        if increment_steps:
            self.steps += 1

    def move_up(self) -> None:
        line_forklift, column_forklift = self.get_current_forklift()
        self.update_forklift_in_matrix(line_forklift - 1, column_forklift, True)

    def move_right(self) -> None:
        line_forklift, column_forklift = self.get_current_forklift()
        self.update_forklift_in_matrix(line_forklift, column_forklift + 1, True)

    def move_down(self) -> None:
        line_forklift, column_forklift = self.get_current_forklift()
        self.update_forklift_in_matrix(line_forklift + 1, column_forklift, True)

    def move_left(self) -> None:
        line_forklift, column_forklift = self.get_current_forklift()
        self.update_forklift_in_matrix(line_forklift, column_forklift - 1, True)

    def get_cell_color(self, row: int, column: int) -> Color:
        if row == self.line_exit and column == self.column_exit:
            for forklift in self.forklifts:
                if forklift.line == row and forklift.column == column:
                    return constants.COLORFORKLIFT

            return constants.COLOREXIT

        if self.matrix[row][column] == constants.PRODUCT_CATCH:
            return constants.COLORSHELFPRODUCTCATCH

        if self.matrix[row][column] == constants.PRODUCT:
            return constants.COLORSHELFPRODUCT

        switcher = {
            constants.FORKLIFT: constants.COLORFORKLIFT,
            constants.SHELF: constants.COLORSHELF,
            constants.EMPTY: constants.COLOREMPTY
        }
        return switcher.get(self.matrix[row][column], constants.COLOREMPTY)

    def __str__(self):
        matrix_string = str(self.rows) + " " + str(self.columns) + "\n"
        for row in self.matrix:
            for column in row:
                matrix_string += str(column) + " "
            matrix_string += "\n"
        return matrix_string

    def __eq__(self, other):
        if isinstance(other, WarehouseState):
            return np.array_equal(self.matrix, other.matrix)
        return NotImplemented

    def __hash__(self):
        return hash(self.matrix.tostring())
