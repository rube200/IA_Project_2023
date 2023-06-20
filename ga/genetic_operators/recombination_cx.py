from ga.genetic_algorithm import GeneticAlgorithm
from ga.genetic_operators.recombination import Recombination
from ga.individual import Individual


class RecombinationCX(Recombination):

    def __init__(self, probability: float):
        super().__init__(probability)

    def recombine(self, ind1: Individual, ind2: Individual) -> None:
        start_with_ind1 = bool(GeneticAlgorithm.rand.getrandbits(1))

        child1_genome, child2_genome = self.recombine_parent(ind1, ind2, start_with_ind1)
        ind1.genome = child1_genome
        ind2.genome = child2_genome

    @staticmethod
    def recombine_parent(ind1: Individual, ind2: Individual, start_with_ind1: bool) -> ([], []):
        genome_size = ind1.num_genes
        child1_genome, child2_genome = [-1] * genome_size, [-1] * genome_size

        if start_with_ind1:
            main_ind = ind1
            other_ind = ind2
        else:
            main_ind = ind2
            other_ind = ind1

        target_index = 0
        while target_index < genome_size:
            if child1_genome[target_index] != -1:
                target_index += 1
                continue

            child1_genome[target_index] = main_ind.genome[target_index]
            child2_genome[target_index] = value = other_ind.genome[target_index]

            target_index = main_ind.genome.index(value)

        return child1_genome, child2_genome

    def __str__(self):
        return "CX Recombination (" + f'{self.probability}' + ")"
