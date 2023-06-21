from ga.genetic_algorithm import GeneticAlgorithm
from ga.individual_int_vector import IntVectorIndividual
from ga.genetic_operators.mutation import Mutation


class MutationRSM(Mutation):
    def __init__(self, probability):
        super().__init__(probability)

    def mutate(self, ind: IntVectorIndividual) -> None:
        num_genes = ind.num_genes
        cut1 = cut2 = GeneticAlgorithm.rand.randint(0, num_genes - 1)
        while cut1 == cut2:
            cut2 = GeneticAlgorithm.rand.randint(0, num_genes - 1)

        if cut1 > cut2:
            cut1, cut2 = cut2, cut1

        while cut1 < cut2:
            self.permute(ind, cut1, cut2)
            cut1 += 1
            cut2 -= 1

    def __str__(self):
        return "RSM (" + f'{self.probability}' + ")"
