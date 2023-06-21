from ga.problem import Problem
from warehouse.warehouse_agent_search import WarehouseAgentSearch
from warehouse.warehouse_individual import WarehouseIndividual


class WarehouseProblemGA(Problem):
    def __init__(self, agent_search: WarehouseAgentSearch):
        self.forklifts = agent_search.forklifts
        self.pairs = agent_search.pairs
        self.products = agent_search.products
        self.agent_search = agent_search

    def generate_individual(self) -> "WarehouseIndividual":
        return WarehouseIndividual(self, len(self.agent_search.products))

    def __str__(self):
        string = "# of forklifts: "
        string += f'{len(self.forklifts)}'
        string = "# of products: "
        string += f'{len(self.products)}'
        return string

