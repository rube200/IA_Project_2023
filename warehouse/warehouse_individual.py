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

        forklifts = self.agent.forklifts
        forklift_index = 0

        forklifts_gene = [[] * 1] * len(forklifts)
        # noinspection PyTypeChecker
        forklifts_gene[forklift_index] = []

        products = self.agent.products
        products_size = len(products)

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene >= products_size:
                forklift_index = gene - products_size + 1
                forklifts_gene[forklift_index] = []
            else:
                forklifts_gene[forklift_index].append(gene)

        forklifts_paths = [[] * 1] * len(forklifts)
        state = copy.deepcopy(self.agent.initial_environment)

        for fk in range(len(forklifts_gene)):
            forklift = forklifts[fk]
            forklifts_paths[fk] = [forklift]

            state.line_forklift = forklift.line
            state.column_forklift = forklift.column

            temp_steps = 0
            for g in range(len(forklifts_gene[fk])):
                gene = forklifts_gene[fk][g]
                product = products[gene]

                steps = self.simulate_actions(forklift, product, state, forklifts_paths[fk])
                temp_steps += steps
                self.fitness += steps
                forklift = product

            steps = self.simulate_actions(forklift, self.agent.exit, state, forklifts_paths[fk])
            temp_steps += steps
            self.fitness += steps

            if self.steps < temp_steps:
                self.steps = temp_steps

        self.best_forklift_path = forklifts_paths
        return self.fitness

    def obtain_all_path(self):
        return self.best_forklift_path, self.steps + 1

    def simulate_actions(self, cell1: Cell, cell2: Cell, state: WarehouseState, forklift_paths) -> int:
        temp_steps = 0
        pair = self.agent.get_pair(cell1, cell2)
        for action in pair.actions:
            action.execute(state)
            new_cell = Cell(state.line_forklift, state.column_forklift)
            forklift_paths.append(new_cell)
            temp_steps += 1
        return temp_steps

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
