import copy

from agentsearch.action import Action
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

        forklifts_data = self.prepare_forklift_data(self.agent.exit)

        if not self.agent.initial_environment.allow_collisions:
            self.compute_fitness_by_simulation(forklifts_data)
        else:
            self.compute_fitness_without_collision(forklifts_data)

        self.best_forklift_path = []
        for forklift_data in forklifts_data:
            self.fitness += forklift_data.steps
            self.best_forklift_path.append(forklift_data.path)
            if forklift_data.steps > self.steps:
                self.steps = forklift_data.steps

        return self.fitness

    def prepare_forklift_data(self, exit_cell: Cell) -> [DynamicForklift]:
        forklifts = self.agent.forklifts
        forklifts_data = []
        for i in range(len(forklifts)):
            forklifts_data.append(DynamicForklift(forklifts[i]))

        forklift_index = 0
        products = self.agent.products
        products_size = len(products)

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene < products_size:
                product = products[gene]
                forklift_data = forklifts_data[forklift_index]
                pair = self.agent.get_pair(forklift_data.current_position, product)
                forklift_data.append_target_cell(product, pair.actions)
                forklift_data.current_position = product
            else:
                forklift_index = gene - products_size + 1

        for i in range(len(forklifts)):
            forklift_data = forklifts_data[i]
            pair = self.agent.get_pair(forklift_data.current_position, exit_cell)
            forklift_data.append_target_cell(exit_cell, pair.actions)
            forklifts_data[i].current_position = forklifts[i]

        return forklifts_data

    def compute_fitness_by_simulation(self, forklifts_data: [DynamicForklift]):
        forklifts_data_len = len(forklifts_data)
        forklift_index = 0
        state = WarehouseState(self.agent.initial_environment.matrix, self.agent.initial_environment.rows,
                               self.agent.initial_environment.columns, False)
        while any(not forklift_data.in_exit for forklift_data in forklifts_data):
            forklift_data = forklifts_data[forklift_index]
            if forklift_data.in_exit:
                forklift_index += 1
                forklift_index %= forklifts_data_len
                continue

            if forklift_data.move_tries > 3:
                forklift_data.in_exit = True
                forklift_data.steps = 999
                forklift_index += 1
                forklift_index %= forklifts_data_len
                continue

            action = self.get_next_simulation_action(forklift_data)
            if not forklift_data.have_targets():
                forklift_data.in_exit = True
                forklift_index += 1
                forklift_index %= forklifts_data_len
                continue

            if not action.is_valid(state):#todo edit
                state_copy = copy.deepcopy(state)
                result = self.search_alternative_path(forklift_data, state_copy)
                if not result:
                    forklift_index += 1
                    forklift_index %= forklifts_data_len
                    continue

                action = self.get_next_simulation_action(forklift_data)
                if not forklift_data.have_targets():
                    forklift_data.in_exit = True
                    forklift_index += 1
                    forklift_index %= forklifts_data_len
                    continue

            state.line_forklift = forklift_data.current_position.line
            state.column_forklift = forklift_data.current_position.column

            action.execute(state)
            forklift_data.append_cell(Cell(state.line_forklift, state.column_forklift))
            forklift_data.next_action()

            forklift_index += 1
            forklift_index %= forklifts_data_len

    @staticmethod
    def get_next_simulation_action(forklift_data: DynamicForklift) -> Action | None:
        action = forklift_data.get_action()
        while action is None:
            forklift_data.next_target()
            if not forklift_data.have_targets():
                return None
            action = forklift_data.get_action()
        return action

    def search_alternative_path(self, forklift_data: DynamicForklift, state: WarehouseState) -> bool:
        state.line_forklift = forklift_data.current_position.line
        state.column_forklift = forklift_data.current_position.column

        target = forklift_data.get_target()
        problem = WarehouseProblemSearch(state, target)
        solution = self.agent.solve_problem(problem)

        if solution and solution.actions:
            forklift_data.update_target(solution.actions)
            return True

        forklift_data.move_tries += 1
        return False

    def compute_fitness_without_collision(self, forklifts_data: [DynamicForklift]):
        state = WarehouseState(self.agent.initial_environment.matrix, self.agent.initial_environment.rows,
                               self.agent.initial_environment.columns, True)
        forklifts_data_len = len(forklifts_data)

        for i in range(forklifts_data_len):
            forklift_data = forklifts_data[i]

            actions = forklift_data.get_actions()
            while actions or forklift_data.have_targets():
                if actions:
                    self.move_forklift_without_collision(forklift_data, actions, state)

                forklift_data.next_target()
                actions = forklift_data.get_actions()

    @staticmethod
    def move_forklift_without_collision(forklift_data: DynamicForklift, actions: [Action], state: WarehouseState):
        state.line_forklift = forklift_data.current_position.line
        state.column_forklift = forklift_data.current_position.column

        for action in actions:
            action.execute(state)
            forklift_data.append_cell(Cell(state.line_forklift, state.column_forklift))

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
