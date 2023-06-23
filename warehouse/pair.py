from warehouse.cell import Cell


class Pair:
    def __init__(self, cell1: Cell, cell2: Cell):
        self.actions = []
        self.cell1 = cell1
        self.cell2 = cell2
        self.value = 0

    def hash(self):
        return str(self.cell1.line) + "_" + str(self.cell1.column) + "_" + str(
            self.cell2.line) + "_" + str(self.cell2.column)

    def __str__(self):
        return f'{self.cell1.line}-{self.cell1.column} / {self.cell2.line}-{self.cell2.column}: {self.value} -> {[str(x) for x in self.actions]}\n'
