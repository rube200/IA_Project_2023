from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual import Individual
from ga.genetic_operators.recombination import Recombination


class RecombinationOX1(Recombination):

    def __init__(self, probability: float):
        super().__init__(probability)

    def recombine(self, ind1: Individual, ind2: Individual) -> None:
        cut1 = GeneticAlgorithm.rand.randint(0, ind1.num_genes - 1)
        cut2 = GeneticAlgorithm.rand.randint(0, ind1.num_genes - 1)

        if cut1 > cut2:
            cut1, cut2 = cut2, cut1

        child1_genome, child2_genome = self.recombine_parent(ind1, ind2, cut1, cut2)
        ind1.genome = child1_genome
        ind2.genome = child2_genome

    @staticmethod
    def recombine_parent(ind1: Individual, ind2: Individual, cut1: int, cut2: int) -> ([], []):
        genome_size = ind1.num_genes
        child1_genome, child2_genome = [-1] * genome_size, [-1] * genome_size

        for i in range(cut1, cut2 + 1):
            child1_genome[i] = ind2.genome[i]
            child2_genome[i] = ind1.genome[i]

        index, ind1_index, ind2_index = 0, 0, 0
        while index < genome_size:
            if cut1 <= index <= cut2:
                index = cut2 + 1
                continue

            if child1_genome[index] == -1:
                next_genome = ind1.genome[ind1_index]
                while next_genome in child1_genome:
                    ind1_index += 1
                    next_genome = ind1.genome[ind1_index]

                child1_genome[index] = next_genome

            if child2_genome[index] == -1:
                next_genome = ind2.genome[ind2_index]
                while next_genome in child2_genome:
                    ind2_index += 1
                    next_genome = ind2.genome[ind2_index]

                child2_genome[index] = next_genome

            index += 1

        return child1_genome, child2_genome

    def __str__(self):
        return "OX1 Recombination (" + f'{self.probability}' + ")"
