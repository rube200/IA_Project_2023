from abc import abstractmethod

from ga.genetic_algorithm import GeneticAlgorithm
from ga.genetic_operators.genetic_operator import GeneticOperator
from ga.individual import Individual
from ga.population import Population


class Mutation(GeneticOperator):

    def __init__(self, probability: float):
        super().__init__(probability)

    def run(self, population: Population) -> None:
        population_size = len(population.individuals)
        for i in range(population_size):
            if GeneticAlgorithm.rand.random() < self.probability:
                self.mutate(population.individuals[i])

    @abstractmethod
    def mutate(self, individual: Individual) -> None:
        pass

    @staticmethod
    def permute(individual: Individual, index1: int, index2: int) -> None:
        aux = individual.genome[index2]
        individual.genome[index2] = individual.genome[index1]
        individual.genome[index1] = aux
