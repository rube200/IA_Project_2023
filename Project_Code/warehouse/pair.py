from warehouse.actions import *
from warehouse.cell import Cell


class Pair:
    def __init__(self, cell1: Cell, cell2: Cell):
        self.actions = []
        self.actions_reversed = []
        self.cell1 = cell1
        self.cell2 = cell2
        self.value = 0

    def hash(self):
        return str(self.cell1.line) + "_" + str(self.cell1.column) + "_" + str(
            self.cell2.line) + "_" + str(self.cell2.column)

    def __str__(self):
        string = f'{self.cell1.line}-{self.cell1.column} / {self.cell2.line}-{self.cell2.column}: {self.value}->'

        num_actions = len(self.actions)
        for a in range(num_actions):
            action = self.actions[a]
            string += f'{action}'
            if a + 1 < num_actions:
                string += ','

        string += '\n'
        return string

    def invert_actions(self):
        for action in self.actions[::-1]:
            if type(action) == ActionUp:
                self.actions_reversed.append(ActionDown())
            elif type(action) == ActionDown:
                self.actions_reversed.append(ActionUp())
            elif type(action) == ActionLeft:
                self.actions_reversed.append(ActionRight())
            elif type(action) == ActionRight:
                self.actions_reversed.append(ActionLeft())

    def is_pair(self, cell1: Cell, cell2: Cell):
        return self.cell1.is_cell(cell1) and self.cell2.is_cell(cell2)
