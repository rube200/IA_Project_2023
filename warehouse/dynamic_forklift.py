from warehouse.cell import Cell


class DynamicForklift:
    def __init__(self, initial_cell: Cell):
        self.current_position = initial_cell
        self.in_exit = False
        self.move_tries = 0
        self.next_action = None
        self.products = []
        self.current_product_index = 0
        self.path = [initial_cell]
        self.steps = 0

    def append_cell(self, cell: Cell):
        self.current_position = cell
        self.path.append(cell)
        self.move_tries = 0
        self.steps += 1

    def append_product(self, cell: Cell):
        self.products.append(cell)

    def get_current_product(self) -> Cell | None:
        if self.current_product_index < len(self.products):
            return self.products[self.current_product_index]
        return None
