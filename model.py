from mesa import Model
from mesa.space import MultiGrid

from agents import GreenAgent, YellowAgent, RedAgent, RobotAgent
from env import Waste, Radioactivity, Environment

import numpy as np
from IPython import display


class RobotMission(Model):
    def __init__(self, n_agents, n_wastes, grid_size, seed=None):
        """
        n_agents is a dict with the number of agents per color
        """
        super().__init__(seed=seed)
        self.grid_size = grid_size
        self.n_wastes = n_wastes
        green_agents = [
            GreenAgent(self, knowledge={}) for _ in range(n_agents["green"])
        ]
        yellow_agents = [
            YellowAgent(self, knowledge={}) for _ in range(n_agents["yellow"])
        ]
        red_agents = [RedAgent(self, knowledge={}) for _ in range(n_agents["red"])]
        self.grid = MultiGrid(grid_size, grid_size, False)
        for agent in green_agents + yellow_agents + red_agents:
            self.place_robot_agents(agent)
        self.place_cell_agents()
        self.env = Environment(self, self.grid)
        self.initialize_agent()

    def place_robot_agents(self, agent):
        # TO DO: PLACE THE AGENTS CORRECTLY (ROBOT AGENTS)
        if isinstance(agent, GreenAgent):
            random_x = np.random.randint(0, self.grid.width / 3)
            random_y = np.random.randint(0, self.grid.height)
        elif isinstance(agent, YellowAgent):
            random_x = np.random.randint(0, self.grid.width / 3 * 2)
            random_y = np.random.randint(0, self.grid.height)
        else:
            random_x = np.random.randint(0, self.grid.width)
            random_y = np.random.randint(0, self.grid.height)
        random_pos = (random_x, random_y)
        self.grid.place_agent(agent, random_pos)
        agent.pos = random_pos

    def place_cell_agents(self):
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                pos = (i, j)
                # first region place Radioactivity(0,0,0) second region Radioactivity(0.5), third Radioactivity(0.8)
                if i < self.grid.width / 3:
                    radioactivity = Radioactivity(self, 0, 0, 0)
                elif self.grid.width / 3 <= i < (self.grid.width / 3) * 2:
                    radioactivity = Radioactivity(self, 0.5, 0, 0)
                else:
                    radioactivity = Radioactivity(self, 0.8, 0, 0)
                self.grid.place_agent(radioactivity, pos)
                radioactivity.pos = pos
        # randomly place wastes
        green_wastes = [
            Waste(self, color_waste=0) for _ in range(self.n_wastes["green"])
        ]
        yellow_wastes = [
            Waste(self, color_waste=1) for _ in range(self.n_wastes["yellow"])
        ]
        red_wastes = [Waste(self, color_waste=2) for _ in range(self.n_wastes["red"])]
        # randomly place them in the possible zones
        wastes = green_wastes + yellow_wastes + red_wastes
        np.random.shuffle(wastes)
        for waste in wastes:
            if waste.color_waste == 0:
                random_x = np.random.randint(0, self.grid.width / 3)
                random_y = np.random.randint(0, self.grid.height)
            elif waste.color_waste == 1:
                random_x = np.random.randint(
                    self.grid.width / 3 + 1, self.grid.width / 3 * 2
                )
                random_y = np.random.randint(0, self.grid.height)
            else:
                random_x = np.random.randint(self.grid.width / 3 * 2 + 1, self.grid.width)
                random_y = np.random.randint(0, self.grid.height)
            random_pos = (random_x, random_y)
            self.grid.place_agent(waste, random_pos)
            waste.pos = random_pos

    def step(self):
        self.agents.shuffle_do("step")

    def initialize_agent(self):
        for agent in self.agents:
            if isinstance(agent, RobotAgent):
                knowledge = self.env.get_info(agent.pos)
                knowledge["carried"] = []
                agent.knowledge = knowledge

    def do(self, agent, action):
        perceipt = self.env.step(agent, action)
        return perceipt

    def get_robot_agents_pos(self):
        return [agent.pos for agent in self.agents if isinstance(agent, RobotAgent)]


test_model = RobotMission(
    {"green": 2, "yellow": 3, "red": 2},
    {"green": 10, "yellow": 10, "red": 10},
    grid_size=10,
)

import matplotlib.pyplot as plt

for i in range(100):
    test_model.step()
    # print(test_model.get_robot_agents_pos())
    # plot the grid and robot agents
    # show wastes with color for each waste

    # color background with radioactivity level
    plt.figure(6)
    plt.clf()
    for agent in test_model.agents:
        if isinstance(agent, Radioactivity):
            try:
                if agent.radioactivity_level == 0:
                    plt.scatter(agent.pos[0], agent.pos[1], marker="o", color="white")
                elif agent.radioactivity_level == 0.5:
                    plt.scatter(agent.pos[0], agent.pos[1], marker="o", color="gray")
                elif agent.radioactivity_level == 0.8:
                    plt.scatter(agent.pos[0], agent.pos[1], marker="o", color="black")
            except:
                print(agent)
                raise ValueError
    for agent in test_model.agents:
        if isinstance(agent, Waste) and agent.pos is not None:
            if agent.color_waste == 0:
                plt.scatter(agent.pos[0], agent.pos[1], marker="o", color="green")
            elif agent.color_waste == 1:
                plt.scatter(agent.pos[0], agent.pos[1], marker="o", color="yellow")
            elif agent.color_waste == 2:
                plt.scatter(agent.pos[0], agent.pos[1], marker="o", color="red")
    # set grid width and height
    plt.xlim(-1, test_model.grid.width)
    plt.ylim(-1, test_model.grid.height)
    plt.grid(True)
    plt.xticks(range(test_model.grid.width))
    plt.yticks(range(test_model.grid.height))
    for agent in test_model.agents:
        if isinstance(agent, GreenAgent):
            plt.scatter(agent.pos[0], agent.pos[1], marker="x", color="green")
        elif isinstance(agent, YellowAgent):
            plt.scatter(agent.pos[0], agent.pos[1], marker="x", color="yellow")
        elif isinstance(agent, RedAgent):
            plt.scatter(agent.pos[0], agent.pos[1], marker="x", color="red")
        #print radioactivity of neighbours
    plt.title("Step: " + str(i))
    plt.pause(0.001)
    display.display(plt.gcf())
    display.clear_output(wait=True)
