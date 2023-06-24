import copy

from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual_int_vector import IntVectorIndividual
from warehouse.cell import Cell
from warehouse.dynamic_forklift import DynamicForklift
from warehouse.warehouse_problemforSearch import WarehouseProblemSearch
from warehouse.warehouse_state import WarehouseState


class WarehouseIndividual(IntVectorIndividual):
    # noinspection PyUnresolvedReferences
    def __init__(self, problem: "WarehouseProblem", num_genes: int):
        super().__init__(problem, num_genes)
        self.agent = self.problem.agent_search
        self.best_forklift_path = None
        self.steps = 0

        for i in range(self.num_genes):
            new_gene = GeneticAlgorithm.rand.randint(0, num_genes - 1)
            while self._is_gene_assigned(new_gene):
                new_gene = GeneticAlgorithm.rand.randint(0, num_genes - 1)
            self.genome[i] = new_gene

    def _is_gene_assigned(self, gene: int) -> bool:
        for i in range(self.num_genes):
            if self.genome[i] == gene:
                return True

        return False

    def compute_fitness(self) -> float:
        self.fitness = 0
        self.steps = 0

        forklift_index = 0
        forklifts = self.agent.forklifts
        forklifts_data = []
        for i in range(len(forklifts)):
            forklifts_data.append(DynamicForklift(forklifts[i]))

        products = self.agent.products
        products_size = len(products)

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene < products_size:
                product = products[gene]
                forklifts_data[forklift_index].append_product(product)
            else:
                forklift_index = gene - products_size + 1

        if not self.agent.initial_environment.allow_collisions:
            self.compute_fitness_by_simulation(forklifts_data)
        else:
            self.compute_fitness_without_collision(forklifts_data)

        self.best_forklift_path = []
        for forklift_data in forklifts_data:
            self.fitness += forklift_data.steps
            self.best_forklift_path.append(forklift_data.path)

        return self.fitness

    def compute_fitness_by_simulation(self, forklifts_data: []):
        forklifts_data_len = len(forklifts_data)
        forklift_index = 0
        state = copy.deepcopy(self.agent.initial_environment)
        while any(not forklift_data.in_exit for forklift_data in forklifts_data):
            forklift_data = forklifts_data[forklift_index]
            if forklift_data.move_tries > 3:
                forklift_data.in_exit = True
                forklift_data.steps = 999
                forklift_index += 1
                forklift_index %= forklifts_data_len
                continue

            if forklift_data.in_exit:
                forklift_index += 1
                forklift_index %= forklifts_data_len
                continue

            state.line_forklift = forklift_data.current_position.line
            state.column_forklift = forklift_data.current_position.column

            target_cell = product = forklift_data.get_current_product()
            if target_cell is None:
                target_cell = self.agent.exit

            if not state.is_movable_cell(target_cell.line, target_cell.column):
                best_distance_to_cell = -1
                best_distance_to_forklift = -1
                for line in range(state.rows):
                    for column in range(state.columns):
                        if not state.is_movable_cell(line, column):
                            continue

                        forklift_distance = abs(line - state.line_forklift) + abs(column - state.column_forklift)
                        product_distance = abs(line - product.line) * 2 + abs(column - product.column)
                        if best_distance_to_cell == -1 or product_distance < best_distance_to_cell:
                            best_distance_to_cell = product_distance
                            best_distance_to_forklift = forklift_distance
                            target_cell = Cell(line, column)
                            continue

                        if product_distance > best_distance_to_cell:
                            continue

                        if forklift_distance < best_distance_to_forklift:
                            best_distance_to_cell = product_distance
                            best_distance_to_forklift = forklift_distance
                            target_cell = Cell(line, column)

            problem = WarehouseProblemSearch(state, target_cell)
            solution = self.agent.solve_problem(problem)

            if solution and solution.actions:
                next_action = solution.actions[0]
                next_action.execute(state)
                forklift_data.append_cell(Cell(state.line_forklift, state.column_forklift))
            else:
                forklift_data.move_tries += 1

            if problem.is_goal(state):
                if product is not None:
                    state.catch_product()
                    forklift_data.current_product_index += 1
                else:
                    forklift_data.in_exit = True

            forklift_index += 1
            forklift_index %= forklifts_data_len

    def compute_fitness_without_collision(self, forklifts_data: []):
        state = copy.deepcopy(self.agent.initial_environment)

        forklifts_data_len = len(forklifts_data)
        for i in range(forklifts_data_len):
            max_steps = 0
            forklift_data = forklifts_data[i]

            state.line_forklift = forklift_data.current_position.line
            state.column_forklift = forklift_data.current_position.column

            for product in forklift_data.products:
                max_steps += self.move_forklift_without_collision(forklift_data, product, state)

            max_steps += self.move_forklift_without_collision(forklift_data, self.agent.exit, state)

            if self.steps < max_steps:
                self.steps = max_steps

    def move_forklift_without_collision(self, forklift_data, cell2: Cell, state: WarehouseState) -> int:
        temp_steps = 0
        pair = self.agent.get_pair(Cell(state.line_forklift, state.column_forklift), cell2)

        state.line_forklift = forklift_data.current_position.line
        state.column_forklift = forklift_data.current_position.column

        for action in pair.actions:
            action.execute(state)
            forklift_data.append_cell(Cell(state.line_forklift, state.column_forklift))
            temp_steps += 1

        state.line_forklift = cell2.line
        state.column_forklift = cell2.column
        return temp_steps

    def obtain_all_path(self):
        return self.best_forklift_path, self.steps + 1

    def __str__(self):
        string = f'Fitness: {self.fitness}\nA->'

        products_size = len(self.agent.products)
        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene < products_size:
                string += f'{gene + 1}'
                if g + 1 < self.num_genes and self.genome[g + 1] < products_size:
                    string += ','
            else:
                string += f'\n{chr(gene - products_size + 66)}->'

        string += '\n\n'
        return string

    def better_than(self, other: "WarehouseIndividual") -> bool:
        return True if self.fitness < other.fitness else False

    # __deepcopy__ is implemented here so that all individuals share the same problem instance
    def __deepcopy__(self, memo):
        new_instance = self.__class__(self.problem, self.num_genes)
        new_instance.genome = self.genome.copy()
        new_instance.fitness = self.fitness
        new_instance.steps = self.steps
        new_instance.best_forklift_path = self.best_forklift_path
        return new_instance
