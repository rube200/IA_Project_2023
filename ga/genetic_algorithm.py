import copy
import time
from random import Random

from ga.ga_event import GAEvent
from ga.population import Population
from ga.selection_methods.selection_method import SelectionMethod


class GeneticAlgorithm:
    rand = None

    def __init__(self,
                 seed: int,
                 population_size: int,
                 max_generations: int,
                 selection_method: SelectionMethod,
                 recombination: "Recombination",
                 mutation: "Mutation",
                 parallel_run: bool = False):
        GeneticAlgorithm.rand = Random(seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.selection_method = selection_method
        self.recombination_method = recombination
        self.mutation_method = mutation
        self.parallel_run = parallel_run
        self.population = None
        self.generation = 0
        self.stopped = False
        self.best_in_run = None
        self.problem = None
        self.listeners = []

    def stop(self) -> None:
        self.stopped = True

    def run(self) -> None:
        if self.problem is None:
            return None

        start_time = time.perf_counter_ns()
        self.generation = 0
        self.population = Population(self.population_size, self.problem)
        self.population.evaluate(self.parallel_run)
        self.best_in_run = self.population.best_individual
        self.fire_generation_ended()

        while self.generation < self.max_generations and not self.stopped:
            self.population = self.selection_method.run(self.population)
            self.recombination_method.run(self.population)
            self.mutation_method.run(self.population)
            self.population.evaluate(self.parallel_run)
            if self.population.best_individual.better_than(self.best_in_run):
                self.best_in_run = copy.deepcopy(self.population.best_individual)
            self.generation += 1
            self.fire_generation_ended()
        self.fire_run_ended()
        print("Performance: ", time.perf_counter_ns() - start_time)

    def __str__(self):
        return "GA: \n" + str(self.population)

    # Listeners

    def add_listener(self, listener):
        self.listeners.append(listener)

    def fire_generation_ended(self) -> None:
        for listener in self.listeners:
            listener.generation_ended(GAEvent(copy.deepcopy(self.best_in_run), self.population.average_fitness))

    def fire_run_ended(self) -> None:
        for listener in self.listeners:
            listener.run_ended(GAEvent(copy.deepcopy(self.best_in_run), self.population.average_fitness, True))
