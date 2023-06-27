from abc import ABC, abstractmethod


class Individual(ABC):

    def __init__(self, problem: "Problem", num_genes: int):
        self.num_genes = num_genes
        self.problem = problem
        self.genome = [-1] * num_genes
        self.fitness = 0

    @abstractmethod
    def swap_genes(self, other, index: int):
        pass

    @abstractmethod
    def compute_fitness(self) -> float:
        pass

    @abstractmethod
    def better_than(self, other: "Individual") -> bool:
        pass
