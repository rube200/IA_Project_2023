from experiments.experiment import Experiment
from experiments.experiment_listener import ExperimentListener
from experiments.experiments_factory import ExperimentsFactory
from experiments_statistics.statistic_best_average import StatisticBestAverage
from experiments_statistics.statistic_best_in_run import StatisticBestInRun
from ga.genetic_algorithm import GeneticAlgorithm
from ga.genetic_operators.mutation_insert import MutationInsert
from ga.genetic_operators.mutation_psm import MutationPSM
from ga.genetic_operators.mutation_rsm import MutationRSM
from ga.genetic_operators.recombination_cx import RecombinationCX
from ga.genetic_operators.recombination_ox1 import RecombinationOX1
from ga.genetic_operators.recombination_pmx import RecombinationPMX
from ga.selection_methods.tournament import Tournament
from warehouse.warehouse_agent_search import read_state_from_txt_file, WarehouseAgentSearch
from warehouse.warehouse_problemforGA import WarehouseProblemGA
from warehouse.warehouse_state import WarehouseState


class WarehouseExperimentsFactory(ExperimentsFactory):

    def __init__(self, filename: str):
        super().__init__(filename)
        self.population_size = None
        self.max_generations = None
        self.selection_method = None
        self.recombination_method = None
        self.mutation_method = None
        self.problem = None
        self.experiment = None

    def build_experiment(self) -> Experiment:
        self.num_runs = int(self.get_parameter_value('Runs'))

        if self.contains_parameter('Allow_Collisions'):
            allow_col = self.get_parameter_value('Allow_Collisions').lower()
            if allow_col in ('n', 'no', 'f', 'false', 'off', '0'):
                self.allow_collisions = False

        self.population_size = int(self.get_parameter_value('Population_size'))
        self.max_generations = int(self.get_parameter_value('Max_generations'))

        # SELECTION
        match self.get_parameter_value('Selection'):
            case 'tournament':
                tournament_size = int(self.get_parameter_value('Tournament_size'))
                self.selection_method = Tournament(tournament_size)

        # RECOMBINATION
        recombination_probability = float(self.get_parameter_value('Recombination_probability'))
        match self.get_parameter_value('Recombination'):
            case 'pmx':
                self.recombination_method = RecombinationPMX(recombination_probability)
            case 'ox1':
                self.recombination_method = RecombinationOX1(recombination_probability)
            case 'cx':
                self.recombination_method = RecombinationCX(recombination_probability)

        # MUTATION
        mutation_probability = float(self.get_parameter_value('Mutation_probability'))
        match self.get_parameter_value('Mutation'):
            case 'insert':
                self.mutation_method = MutationInsert(mutation_probability)
            case 'rsm':
                self.mutation_method = MutationRSM(mutation_probability)
            case 'psm':
                self.mutation_method = MutationPSM(mutation_probability)

        # PROBLEM
        matrix, num_rows, num_columns = read_state_from_txt_file(self.get_parameter_value("Problem_file"))

        agent_search = WarehouseAgentSearch(
            WarehouseState(matrix, num_rows, num_columns, allow_collisions=self.allow_collisions))
        agent_search.calculate_pairs_distances()

        self.problem = WarehouseProblemGA(agent_search)

        experiment_textual_representation = self.build_experiment_textual_representation()
        experiment_header = self.build_experiment_header()
        experiment_configuration_values = self.build_experiment_values()

        self.experiment = Experiment(
            self,
            self.num_runs,
            self.problem,
            experiment_textual_representation,
            experiment_header,
            experiment_configuration_values)

        self.statistics.clear()
        for statistic_name in self.statistics_names:
            statistic = self.build_statistic(statistic_name, experiment_header)
            self.statistics.append(statistic)
            self.experiment.add_listener(statistic)

        return self.experiment

    def generate_ga_instance(self, seed: int) -> GeneticAlgorithm:
        ga = GeneticAlgorithm(
            seed,
            self.population_size,
            self.max_generations,
            self.selection_method,
            self.recombination_method,
            self.mutation_method
        )

        for statistic in self.statistics:
            ga.add_listener(statistic)

        return ga

    def build_statistic(self, statistic_name: str, experiment_header: str) -> ExperimentListener:
        if statistic_name == 'BestIndividual':
            return StatisticBestInRun(experiment_header)
        if statistic_name == 'BestAverage':
            return StatisticBestAverage(self.num_runs, experiment_header)

    def build_experiment_textual_representation(self) -> str:
        string = 'Population size: ' + str(self.population_size) + '\r\n'
        string += 'Max generations: ' + str(self.max_generations) + '\r\n'
        string += 'Selection: ' + str(self.selection_method) + '\r\n'
        string += 'Recombination: ' + str(self.recombination_method) + '\r\n'
        string += 'Mutation: ' + str(self.mutation_method) + '\r\n'
        string += 'Allow Collisions: ' + str(self.allow_collisions) + '\r\n'
        return string

    def build_experiment_header(self) -> str:
        string = 'Population size:' + '\t'
        string += 'Max generations: ' + '\t'
        string += 'Selection: ' + '\t'
        string += 'Recombination: ' + '\t'
        string += 'Mutation: ' + '\t'
        return string

    def build_experiment_values(self) -> str:
        string = str(self.population_size) + '\t'
        string += str(self.max_generations) + '\t'
        string += str(self.selection_method) + '\t'
        string += str(self.recombination_method) + '\t'
        string += str(self.mutation_method) + '\t'
        return string
