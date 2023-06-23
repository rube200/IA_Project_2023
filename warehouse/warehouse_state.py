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

        self.is_default = True
        self.rows = rows
        self.columns = columns
        self.matrix = np.full([self.rows, self.columns], fill_value=0, dtype=int)

        for i in range(self.rows):
            for j in range(self.columns):
                self.matrix[i][j] = matrix[i][j]
                if self.matrix[i][j] == constants.FORKLIFT:
                    self.line_forklift = i
                    self.column_forklift = j
                elif self.matrix[i][j] == constants.EXIT:
                    self.line_exit = i
                    self.column_exit = j

    @staticmethod
    def is_movable_cell(target_cell: Cell) -> bool:
        return target_cell == constants.EMPTY or target_cell == constants.EXIT

    @staticmethod
    def can_not_move() -> bool:
        return True

    def can_move_up(self) -> bool:
        if self.line_forklift <= 0:
            return False

        target_cell = self.matrix[self.line_forklift - 1][self.column_forklift]
        return self.is_movable_cell(target_cell)

    def can_move_right(self) -> bool:
        if self.column_forklift == self.columns - 1:
            return False

        target_cell = self.matrix[self.line_forklift][self.column_forklift + 1]
        return self.is_movable_cell(target_cell)

    def can_move_down(self) -> bool:
        if self.line_forklift == self.rows - 1:
            return False

        target_cell = self.matrix[self.line_forklift + 1][self.column_forklift]
        return self.is_movable_cell(target_cell)

    def can_move_left(self) -> bool:
        if self.column_forklift <= 0:
            return False

        target_cell = self.matrix[self.line_forklift][self.column_forklift - 1]
        return self.is_movable_cell(target_cell)

    def update_forklift_in_matrix(self, new_line: int, new_column: int):
        self.is_default = False
        if self.line_forklift != self.line_exit or self.column_forklift != self.column_exit:
            old_cell_state = constants.EMPTY
        else:
            old_cell_state = constants.EXIT

        self.matrix[self.line_forklift][self.column_forklift] = old_cell_state
        self.line_forklift = new_line
        self.column_forklift = new_column
        self.matrix[new_line][new_column] = constants.FORKLIFT

    def not_move(self) -> None:
        pass

    def move_up(self) -> None:
        self.update_forklift_in_matrix(self.line_forklift - 1, self.column_forklift)

    def move_right(self) -> None:
        self.update_forklift_in_matrix(self.line_forklift, self.column_forklift + 1)

    def move_down(self) -> None:
        self.update_forklift_in_matrix(self.line_forklift + 1, self.column_forklift)

    def move_left(self) -> None:
        self.update_forklift_in_matrix(self.line_forklift, self.column_forklift - 1)

    def get_cell_color(self, row: int, column: int) -> Color:
        if row == self.line_exit and column == self.column_exit and (
                row != self.line_forklift or column != self.column_forklift):
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
