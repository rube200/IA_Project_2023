import copy

from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual_int_vector import IntVectorIndividual
from warehouse.cell import Cell
from warehouse.warehouse_state import WarehouseState


class WarehouseIndividual(IntVectorIndividual):
    # noinspection PyUnresolvedReferences
    def __init__(self, problem: "WarehouseProblem", num_genes: int):
        super().__init__(problem, num_genes)
        self.agent = self.problem.agent_search
        self.total_steps = 0

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

        forklifts = self.agent.forklifts
        forklift = forklifts[0]
        exit_cell = self.agent.exit
        products = self.agent.products
        products_size = len(products)

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene < products_size:
                product = products[gene]
                self.fitness += self.agent.get_distance(forklift, product)
                forklift = product
                continue

            self.fitness += self.agent.get_distance(forklift, exit_cell)
            forklift_index = gene - products_size + 1
            forklift = forklifts[forklift_index]

        self.fitness += self.agent.get_distance(forklift, exit_cell)
        return self.fitness

    def obtain_all_path(self):
        forklifts = self.agent.forklifts
        forklift_index = 0
        forklift = forklifts[forklift_index]

        forklift_path = [[forklift]]

        products = self.agent.products
        products_size = len(products)

        state = copy.deepcopy(self.agent.initial_environment)
        state.line_forklift = forklift.line
        state.column_forklift = forklift.column
        self.total_steps = 0

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene < products_size:
                product = products[gene]
                self.simulate_actions(forklift, product, state, forklift_path)
                forklift = product
                continue

            self.simulate_actions(forklift, self.agent.exit, state, forklift_path)

            forklift_index = gene - products_size + 1
            forklift = forklifts[forklift_index]
            state.line_forklift = forklift.line
            state.column_forklift = forklift.column
            forklift_path.append([forklift])

        self.simulate_actions(forklift, self.agent.exit, state, forklift_path)
        return forklift_path, self.total_steps

    def simulate_actions(self, cell1: Cell, cell2: Cell, state: WarehouseState, forklift_path):
        pair = self.agent.get_pair(cell1, cell2)
        for action in pair.actions:
            action.execute(state)
            new_cell = Cell(state.line_forklift, state.column_forklift)
            forklift_path[len(forklift_path) - 1].append(new_cell)
            self.total_steps += 1

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
        new_instance.total_steps = self.total_steps
        return new_instance
