class Cell:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return False
        return self.line == other.line and self.column == other.column

    def __str__(self) -> str:
        return f"{self.line}-{self.column}"

    def is_cell(self, other: "Cell") -> bool:
        return self.line == other.line and self.column == other.column

    def __copy__(self):
        return self.__class__(self.line, self.column)
