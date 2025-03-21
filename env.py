import numpy as np
from typing import List, Tuple
from mesa import Agent, Model
from mesa.space import MultiGrid
from agents import RobotAgent

ACTIONS_DICT = {
    0: "pick",
    1: "release_G",
    2: "release_Y",
    3: "release_R",
    4: "move_up",
    5: "move_right",
    6: "move_down",
    7: "move_left"
}

class Waste(Agent):
    def __init__(self):
        self.color_waste = 0

class Radioactivity(Agent):
    def __init__(self):
        self.radioactivity_level = 0
        self.is_waste_disposal = 0
        self.is_wall = 0

class Environment:
    def __init__(self, grid:MultiGrid, agent_coords:List[Tuple[int, int]]):
        self.grid = grid
        self.agent_coords = agent_coords


    def step(self, pos, action):
        #called in model.do
        #find way to get pos from Model
        if action == 0:
            agent = self.grid.get_cell_list_contents(pos)[0]
            agent.color_waste = 0
        #check success
        success = False
        neighbours = self.grid.get_neighborhood(pos, moore=True, include_center=False)
        neighbours_info = neighbours
        return success + neighbours_info
    
    def reset(self):
        pass
    
    def can_pickup(self, pos):
        #check if there is not another robot heree
        cell_agent = self.grid.get_cell_list_contents(pos)
        #check if it is a RobotAgent
        if len(cell_agent) == 1 and isinstance(cell_agent[0], RobotAgent):
            return False
        return True

