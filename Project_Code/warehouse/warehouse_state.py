import numpy as np
from PIL.ImageEnhance import Color
from numpy import ndarray

import constants
from agentsearch.action import Action
from agentsearch.state import State


class WarehouseState(State[Action]):

    def __init__(self, matrix: ndarray, rows, columns, process_matrix: bool = True, allow_collisions: bool = True):
        super().__init__()

        self.allow_collisions = allow_collisions
        self.is_default = True

        self.rows = rows
        self.columns = columns
        self.matrix = matrix.copy()

        if not process_matrix:
            return

        for i in range(self.rows):
            for j in range(self.columns):
                cell_info = matrix[i][j]
                if cell_info == constants.FORKLIFT:
                    self.line_forklift = i
                    self.column_forklift = j
                elif cell_info == constants.EXIT:
                    self.line_exit = i
                    self.column_exit = j

    def is_movable_cell(self, line: int, column: int) -> bool:
        cell = self.matrix[line][column]
        return cell == constants.EMPTY or cell == constants.EXIT or self.allow_collisions and cell == constants.FORKLIFT

    def can_move_up(self) -> bool:
        if self.line_forklift <= 0:
            return False

        return self.is_movable_cell(self.line_forklift - 1, self.column_forklift)

    def can_move_right(self) -> bool:
        if self.column_forklift >= self.columns - 1:
            return False

        return self.is_movable_cell(self.line_forklift, self.column_forklift + 1)

    def can_move_down(self) -> bool:
        if self.line_forklift >= self.rows - 1:
            return False

        return self.is_movable_cell(self.line_forklift + 1, self.column_forklift)

    def can_move_left(self) -> bool:
        if self.column_forklift <= 0:
            return False

        return self.is_movable_cell(self.line_forklift, self.column_forklift - 1)

    def update_forklift_in_matrix(self, new_line: int, new_column: int):
        self.is_default = False
        if self.line_forklift != self.line_exit or self.column_forklift != self.column_exit:
            self.matrix[self.line_forklift][self.column_forklift] = constants.EMPTY

        self.line_forklift = new_line
        self.column_forklift = new_column
        if self.line_forklift != self.line_exit or self.column_forklift != self.column_exit:
            self.matrix[new_line][new_column] = constants.FORKLIFT

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

    def __copy__(self) -> "WarehouseState":
        new_state = self.__class__(self.matrix, self.rows, self.columns, False, self.allow_collisions)
        new_state.line_forklift = self.line_forklift
        new_state.column_forklift = self.column_forklift
        new_state.line_exit = self.line_exit
        new_state.column_exit = self.column_exit
        new_state.is_default = self.is_default
        return new_state

    def __str__(self):
        matrix_string = str(self.rows) + " " + str(self.columns) + "\n"
        for row in self.matrix:
            for column in row:
                matrix_string += str(column) + " "
            matrix_string += "\n"
        return matrix_string + f"{self.line_forklift}-{self.column_forklift}\n"

    def __eq__(self, other):
        if isinstance(other, WarehouseState):
            return np.array_equal(self.matrix, other.matrix)
        return NotImplemented

    def __hash__(self):
        return hash((self.matrix.tostring(), self.line_forklift, self.column_forklift))
