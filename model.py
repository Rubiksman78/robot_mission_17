from mesa import Model
from mesa.space import MultiGrid

from agents import GreenAgent, YellowAgent, RedAgent
from env import Waste, Radioactivity, Environment

import numpy as np
class RobotMission(Model):
    def __init__(self, n_agents, grid_size, seed = None):
        '''
        n_agents is a dict with the number of agents per color
        '''
        super().__init__(seed=seed)
        green_agents = [GreenAgent(self, id=len(self.agents), knowledge=self.initialize_agent("green")) for _ in range(n_agents["green"])]
        yellow_agents = [YellowAgent(self, id=len(self.agents), knowledge=self.initialize_agent("yellow")) for _ in range(n_agents["yellow"])]
        red_agents = [RedAgent(self, id=len(self.agents), knowledge=self.initialize_agent("red")) for _ in range(n_agents["red"])]
        self.grid = MultiGrid(grid_size, grid_size, False)
        wastes = [Waste(self) for i in range(grid_size) for j in range(grid_size)]
        radioactivities = [Radioactivity(self) for i in range(grid_size) for j in range(grid_size)]
        for agent in green_agents + yellow_agents + red_agents + wastes + radioactivities:
            self.place_agents(agent)
            self.agents.add(agent)
        self.env = Environment(self.grid)

    def place_agents(self, agent):
        #TO DO: PLACE THE AGENTS CORRECTLY (ROBOT AGENTS + WASTE AGENTS + RADIOACTIVITY AGENTS)
        random_pos = np.random.randint(0, self.width, 2)
        random_pos = tuple(random_pos)
        self.grid.place_agent(agent, random_pos)
        agent.pos = random_pos

    def step(self):
        self.agents.shuffle_do("step")

    def initialize_agent(self, color):
        knowledge = {}
        return knowledge

    def do(self, agent, action):
        perceipt = self.env.step(agent, action)
        return perceipt
    
# test_model = RobotMission({"green": 1, "yellow": 1, "red": 1}, 10)
# test_model.step()