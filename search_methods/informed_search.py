from abc import abstractmethod

from agentsearch.problem import Problem
from agentsearch.state import State
from search_methods.graph_search import GraphSearch
from search_methods.node import Node
from search_methods.solution import Solution
from utils.node_priority_queue import NodePriorityQueue


class InformedSearch(GraphSearch[NodePriorityQueue]):

    def __init__(self):
        super().__init__(NodePriorityQueue)
        self.heuristic = None

    def search(self, problem: Problem) -> Solution:
        self.reset()
        self.stopped = False
        self.heuristic = problem.heuristic
        return self.graph_search(problem)

    @abstractmethod
    def add_successor_to_frontier(self, successor: State, parent: Node) -> None:
        pass
