from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual_int_vector import IntVectorIndividual


class WarehouseIndividual(IntVectorIndividual):
    # noinspection PyUnresolvedReferences
    def __init__(self, problem: "WarehouseProblem", num_genes: int):
        super().__init__(problem, num_genes)
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
        agent = self.problem.agent_search

        forklifts = agent.forklifts
        forklift = forklifts[0]
        products = agent.products
        products_size = len(products)

        for g in range(self.num_genes):
            gene = self.genome[g]
            if gene >= products_size:
                forklift_index = gene - products_size + 1
                forklift = forklifts[forklift_index]
                continue

            product = products[gene]
            self.fitness += self.problem.agent_search.get_distance(forklift, product)
            forklift = product

        return self.fitness

    def obtain_all_path(self):
        # TODO
        pass

    def __str__(self):
        string = 'Fitness: ' + f'{self.fitness}' + '\n'
        string += str(self.genome) + "\n\n"
        # TODO
        return string

    def better_than(self, other: "WarehouseIndividual") -> bool:
        return True if self.fitness < other.fitness else False

    # __deepcopy__ is implemented here so that all individuals share the same problem instance
    def __deepcopy__(self, memo):
        new_instance = self.__class__(self.problem, self.num_genes)
        new_instance.genome = self.genome.copy()
        new_instance.fitness = self.fitness
        # TODO
        return new_instance
