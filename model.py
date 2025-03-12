from mesa import Model

from agents import GreenAgent, YellowAgent, RedAgent


class RobotMission(Model):
    def __init__(self, n_agents, seed = None):
        '''
        n_agents is a dict with the number of agents per color
        '''
        super().__init__(seed=seed)
        _ = [GreenAgent(self, id=len(self.agents), knowledge=self.initialize_agent("green")) for _ in range(n_agents["green"])]
        _ = [YellowAgent(self, id=len(self.agents), knowledge=self.initialize_agent("yellow")) for _ in range(n_agents["yellow"])]
        _ = [RedAgent(self, id=len(self.agents), knowledge=self.initialize_agent("red")) for _ in range(n_agents["red"])]


    def step(self):
        self.agents.shuffle_do("step")

    def initialize_agent(self, color):
        knowledge = {}

        return knowledge

    def do(self, agent, action):
        perceipt = self.env.step(agent, action)