from agentsearch.action import Action
from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual_int_vector import IntVectorIndividual
from warehouse.actions import ActionNoMove
from warehouse.cell import Cell
from warehouse.dynamic_forklift import DynamicForklift
from warehouse.warehouse_problemforSearch import WarehouseProblemSearch
from warehouse.warehouse_state import WarehouseState


class WarehouseIndividual(IntVectorIndividual):
    # noinspection PyUnresolvedReferences
    def __init__(self, problem: "WarehouseProblem", num_genes: int, initialize_genome: bool = True):
        super().__init__(problem, num_genes)
        self.agent = self.problem.agent_search
        self.forklifts_actions = []

        if not initialize_genome:
            return

        for i in range(self.num_genes):
            new_gene = GeneticAlgorithm.rand.randint(0, num_genes - 1)
            while new_gene in self.genome:
                new_gene = GeneticAlgorithm.rand.randint(0, num_genes - 1)
            self.genome[i] = new_gene

    def compute_fitness(self) -> float:
        self.forklifts_actions = [[] for _ in range(len(self.agent.forklifts))]
        if self.agent.initial_environment.allow_collisions:
            self.fitness = self.compute_fitness_without_collision()
            return self.fitness

        self.fitness = self.compute_fitness_with_collision()
        return self.fitness

    def compute_fitness_without_collision(self) -> float:
        fitness = 0

        forklifts = self.agent.forklifts
        forklift_index = 0
        forklift_pos = forklifts[forklift_index]

        products = self.agent.products
        products_size = len(products)

        def get_fitness(origin_cell: Cell, target_cell: Cell):
            p, normal_order = self.agent.get_pair(origin_cell, target_cell)
            self.forklifts_actions[forklift_index].extend(p.actions if normal_order else p.actions_reversed)
            return p.value

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene < products_size:
                product = products[gene]
                fitness += get_fitness(forklift_pos, product)
                forklift_pos = product
                continue

            fitness += get_fitness(forklift_pos, self.agent.exit)
            forklift_index = gene - products_size + 1
            forklift_pos = forklifts[forklift_index]

        fitness += get_fitness(forklift_pos, self.agent.exit)
        return fitness

    def compute_fitness_with_collision(self) -> float:
        forklifts = self.agent.forklifts
        forklifts_len = len(forklifts)
        forklift_index = 0

        forklifts_data = [DynamicForklift(forklifts[i]) for i in range(forklifts_len)]

        products = self.agent.products
        products_size = len(products)

        # Prepare data to simulate movement
        def append_target(fork_data: DynamicForklift, target_cell: Cell):
            pair, normal_order = self.agent.get_pair(fork_data.current_position, target_cell)
            fork_data.append_target(target_cell, pair.actions if normal_order else pair.actions_reversed)

        for g in range(self.num_genes):
            gene = self.genome[g]
            forklift_data = forklifts_data[forklift_index]

            if gene < products_size:
                product = products[gene]
                append_target(forklift_data, product)
                forklift_data.current_position = product
                continue

            append_target(forklift_data, self.agent.exit)
            forklift_data.current_position = forklifts[forklift_index].copy()
            forklift_index = gene - products_size + 1

        append_target(forklifts_data[forklift_index], self.agent.exit)
        forklifts_data[forklift_index].current_position = forklifts[forklift_index].copy()

        # Simulation

        fitness = 0
        forklift_index = 0
        state = self.agent.initial_environment.soft_copy()

        while any(not forklift_data.in_exit for forklift_data in forklifts_data):
            forklift_data = forklifts_data[forklift_index]
            if forklift_data.in_exit:
                forklift_index += 1
                forklift_index %= forklifts_len
                continue

            if forklift_data.move_tries > 3:
                forklift_data.in_exit = True
                fitness += 999
                break

            action = self.get_next_simulation_action(forklift_data)
            if action is None:
                forklift_data.in_exit = True
                forklift_index += 1
                forklift_index %= forklifts_len
                continue

            state.line_forklift = forklift_data.current_position.line
            state.column_forklift = forklift_data.current_position.column

            if not action.is_valid(state):
                state_copy = state.soft_copy()
                new_path = self.search_alternative_path(forklift_data, state_copy)
                if new_path:
                    action = self.get_next_simulation_action(forklift_data)
                    if action is None:
                        forklift_data.in_exit = True
                        forklift_index += 1
                        forklift_index %= forklifts_len
                        continue
                    else:
                        forklift_data.move_tries = 0
                else:
                    action = ActionNoMove()
                    forklift_data.move_tries += 1
            else:
                forklift_data.move_tries = 0

            action.execute(state)
            fitness += action.cost
            self.forklifts_actions[forklift_index].append(action)

            forklift_data.current_position.line = state.line_forklift
            forklift_data.current_position.column = state.column_forklift
            forklift_data.next_action()

            forklift_index += 1
            forklift_index %= forklifts_len

        return fitness

    @staticmethod
    def get_next_simulation_action(forklift_data: DynamicForklift) -> Action | None:
        action = forklift_data.get_action()
        # action can be None with next target if cells are parallel to each other on same corridor
        while action is None and forklift_data.have_more_targets():
            forklift_data.next_target()
            action = forklift_data.get_action()
        return action

    def search_alternative_path(self, forklift_data: DynamicForklift, state: WarehouseState) -> bool:
        state.line_forklift = forklift_data.current_position.line
        state.column_forklift = forklift_data.current_position.column

        target = forklift_data.get_target()
        problem = WarehouseProblemSearch(state, target)
        solution = self.agent.solve_problem(problem)

        if solution:
            forklift_data.update_target(solution.actions)
            return True

        forklift_data.move_tries += 1
        return False

    def obtain_all_path(self):
        forklifts = self.agent.forklifts
        forklifts_path = [[forklift] for forklift in forklifts]
        max_steps = 0

        state = self.agent.initial_environment.soft_copy()
        state.allow_collisions = True

        for i in range(len(self.forklifts_actions)):
            forklift_actions = self.forklifts_actions[i]
            forklift_actions_len = len(forklift_actions)

            if forklift_actions_len > max_steps:
                max_steps = forklift_actions_len

            forklift = forklifts[i]
            state.line_forklift = forklift.line
            state.column_forklift = forklift.column

            for action in forklift_actions:
                action.execute(state)
                # noinspection PyTypeChecker
                forklifts_path[i].append(Cell(state.line_forklift, state.column_forklift))

        return forklifts_path, max_steps + 1

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
        new_instance = self.__class__(self.problem, self.num_genes, False)
        new_instance.genome = self.genome.copy()
        new_instance.fitness = self.fitness
        new_instance.forklifts_actions = self.forklifts_actions.copy()
        return new_instance
