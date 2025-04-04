import numpy as np
from mesa import Model
from mesa.space import MultiGrid

from agents import (RandomGreenAgent, RandomRedAgent, RandomYellowAgent,
                    RobotAgent, YellowAgent)
from env import Environment, Radioactivity, Waste


class RobotMission(Model):
    def __init__(
        self, n_agents, n_wastes, grid_size, use_random_agents=True, seed=None
    ):
        """
        n_agents is a dict with the number of agents per color
        """
        super().__init__(seed=seed)
        self.grid_size = grid_size
        self.n_wastes = n_wastes
        if use_random_agents:
            self.greenagent = RandomGreenAgent
            self.yellowagent = RandomYellowAgent
            self.redagent = RandomRedAgent
        else:
            self.greenagent = RobotAgent
            self.yellowagent = YellowAgent
            self.redagent = RobotAgent
        green_agents = [
            self.greenagent(self, knowledge={}) for _ in range(n_agents["green"])
        ]
        yellow_agents = [
            self.yellowagent(self, knowledge={}) for _ in range(n_agents["yellow"])
        ]
        red_agents = [self.redagent(self, knowledge={}) for _ in range(n_agents["red"])]
        self.grid = MultiGrid(grid_size, grid_size, False)
        self.already_placed = set()
        for agent in green_agents + yellow_agents + red_agents:
            self.place_robot_agents(agent)
        self.radioactivity_map = np.zeros((grid_size, grid_size))
        self.place_cell_agents()
        self.env = Environment(self, self.grid)
        self.initialize_agent()

    def place_robot_agents(self, agent):
        placed = False
        while not placed:
            if isinstance(agent, self.greenagent):
                random_x = np.random.randint(0, self.grid.width / 3)
                random_y = np.random.randint(0, self.grid.height)
            elif isinstance(agent, self.yellowagent):
                random_x = np.random.randint(0, self.grid.width / 3 * 2)
                random_y = np.random.randint(0, self.grid.height)
            else:
                random_x = np.random.randint(0, self.grid.width)
                random_y = np.random.randint(0, self.grid.height)
            random_pos = (random_x, random_y)
            if random_pos not in self.already_placed:
                self.already_placed.add(random_pos)
                placed = True
        self.grid.place_agent(agent, random_pos)
        agent.pos = random_pos

    def place_cell_agents(self):
        # Place radioactivity
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                pos = (i, j)
                is_waste_disposal = 0
                if i < self.grid.width / 3:
                    level = 0
                elif self.grid.width / 3 <= i < (self.grid.width / 3) * 2:
                    level = 0.5
                else:
                    level = 0.8
                level_plot = level
                # add a 2*5 waste zone right
                if (
                    self.grid.width - 2 <= i < self.grid.width
                    and j > (self.grid.height / 2) - 2
                    and j < (self.grid.height / 2) + 2
                ):
                    is_waste_disposal = 1
                    level_plot = 2
                radioactivity = Radioactivity(self, level, is_waste_disposal, 0)
                self.radioactivity_map[j, i] = level_plot
                self.grid.place_agent(radioactivity, pos)
                radioactivity.pos = pos
        # Place wastes randomly
        green_wastes = [
            Waste(self, color_waste=0) for _ in range(self.n_wastes["green"])
        ]
        yellow_wastes = [
            Waste(self, color_waste=1) for _ in range(self.n_wastes["yellow"])
        ]
        red_wastes = [Waste(self, color_waste=2) for _ in range(self.n_wastes["red"])]
        wastes = green_wastes + yellow_wastes + red_wastes
        np.random.shuffle(wastes)
        for waste in wastes:
            placed = False
            while not placed:
                if waste.color_waste == 0:
                    random_x = np.random.randint(0, self.grid.width / 3)
                    random_y = np.random.randint(0, self.grid.height)
                elif waste.color_waste == 1:
                    random_x = np.random.randint(
                        self.grid.width / 3 + 1, self.grid.width / 3 * 2
                    )
                    random_y = np.random.randint(0, self.grid.height)
                else:
                    random_x = np.random.randint(
                        self.grid.width / 3 * 2 + 1, self.grid.width
                    )
                    random_y = np.random.randint(0, self.grid.height)
                random_pos = (random_x, random_y)
                if random_pos not in self.already_placed:
                    self.already_placed.add(random_pos)
                    placed = True
            self.grid.place_agent(waste, random_pos)
            waste.pos = random_pos

    def step(self):
        self.agents.shuffle_do("step")

    def initialize_agent(self):
        for agent in self.agents:
            if isinstance(agent, RobotAgent):
                knowledge = self.env.get_info(agent.pos)
                knowledge["carried"] = []
                knowledge["grid"] = np.zeros((self.grid_size + 2, self.grid_size + 2)) - 1
                agent.knowledge = knowledge

    def do(self, agent, action):
        perceipt = self.env.step(agent, action)
        return perceipt

    def get_robot_agents_pos(self):
        return [agent.pos for agent in self.agents if isinstance(agent, RobotAgent)]
