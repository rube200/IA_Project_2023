from joblib import delayed, Parallel

from ga.individual import Individual
from ga.problem import Problem


class Population:

    def __init__(self, size: int, problem: Problem = None):
        self.size = size
        self.individuals = []
        self.best_individual = None
        self.problem = problem
        if problem is not None:
            for i in range(size):
                self.individuals.append(problem.generate_individual())

    def evaluate(self, parallel_run: bool = False) -> Individual:
        if parallel_run:
            self.individuals = Parallel(n_jobs=-2)(delayed(self.compute_ind)(ind) for ind in self.individuals)
        else:
            for ind in self.individuals:
                self.compute_ind(ind)

        for ind in self.individuals:
            if self.best_individual is None or ind.better_than(self.best_individual):
                self.best_individual = ind

        return self.best_individual

    @staticmethod
    def compute_ind(ind: Individual) -> Individual:
        ind.compute_fitness()
        return ind

    @property
    def average_fitness(self) -> float:
        fitness_sum = 0
        for ind in self.individuals:
            fitness_sum += ind.fitness
        return fitness_sum / self.size

    def __str__(self):
        return str(self.individuals)
