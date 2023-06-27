from ga.genetic_algorithm import GeneticAlgorithm
from ga.genetic_operators.recombination import Recombination
from ga.individual import Individual


class RecombinationOX1(Recombination):

    def __init__(self, probability: float):
        super().__init__(probability)

    def recombine(self, ind1: Individual, ind2: Individual) -> None:
        cut1 = cut2 = GeneticAlgorithm.rand.randint(0, ind1.num_genes - 1)
        while cut1 == cut2:
            cut2 = GeneticAlgorithm.rand.randint(0, ind1.num_genes - 1)

        if cut1 > cut2:
            cut1, cut2 = cut2, cut1

        child1_genome, child2_genome = self.recombine_parents(ind1, ind2, cut1, cut2)
        ind1.genome = child1_genome
        ind2.genome = child2_genome

    @staticmethod
    def recombine_parents(ind1: Individual, ind2: Individual, cut1: int, cut2: int) -> ([], []):
        genome_size = ind1.num_genes
        child1_genome, child2_genome = [-1] * genome_size, [-1] * genome_size

        for i in range(cut1, cut2 + 1):
            child1_genome[i] = ind1.genome[i]
            child2_genome[i] = ind2.genome[i]

        index = ind1_index = ind2_index = (cut2 + 1) % genome_size
        while -1 in child1_genome or -1 in child2_genome:
            gene = ind2.genome[index]
            if gene not in child1_genome:
                child1_genome[ind1_index] = gene
                ind1_index = (ind1_index + 1) % genome_size

            gene = ind1.genome[index]
            if gene not in child2_genome:
                child2_genome[ind2_index] = gene
                ind2_index = (ind2_index + 1) % genome_size

            index = (index + 1) % genome_size

        return child1_genome, child2_genome

    def __str__(self):
        return "OX1 (" + f'{self.probability}' + ")"
