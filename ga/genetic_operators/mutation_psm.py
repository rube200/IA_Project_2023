from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual_int_vector import IntVectorIndividual
from ga.genetic_operators.mutation import Mutation


class MutationPSM(Mutation):
    def __init__(self, probability):
        super().__init__(probability)

    def mutate(self, ind: IntVectorIndividual) -> None:
        for i in range(ind.num_genes):
            if GeneticAlgorithm.rand.random() >= self.probability:
                continue

            random_index = GeneticAlgorithm.rand.randint(0, ind.num_genes)
            while random_index == i:
                random_index = GeneticAlgorithm.rand.randint(0, ind.num_genes)

            self.permute(ind, i, random_index)

    def __str__(self):
        return "PSM (" + f'{self.probability}' + ")"
