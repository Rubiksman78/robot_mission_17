import numpy as np
from mesa import Agent
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
    def __init__(self, model):
        super().__init__(model)
        self.color_waste = 0

class Radioactivity(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.radioactivity_level = 0
        self.is_waste_disposal = 0
        self.is_wall = 0

class Environment:
    def __init__(self, grid:MultiGrid):
        self.grid = grid

    def step(self, agent, action):
        #called in model.do
        #desired output is [radioactivity_level 3*3, color_waste 3*3, is_waste_disposal 3*3, is_wall 3*3, other_robots 3*3, success]
        pos = agent.pos
        cell_agent = self.grid.get_cell_list_contents(pos)[0] #get agents at the same pos as the robot (Waste+Radioactivity)
        #Get information from neighbouts
        radioactivity_level = np.zeros((3, 3))
        color_waste = np.zeros((3, 3))
        is_waste_disposal = np.zeros((3, 3))
        is_wall = np.zeros((3, 3))
        other_robots = np.zeros((3, 3))
        neighbours = self.grid.get_neighborhood(pos, moore=True, include_center=False)
        success = self.can_pickup(pos)
        for i, neighbour in enumerate(neighbours):
            neighbour_agent = self.grid.get_cell_list_contents(neighbour)[0]
            x,y = i//3, i%3
            radioactivity_level[x][y] = neighbour_agent.radioactivity_level
            color_waste[x][y] = neighbour_agent.color_waste
            is_waste_disposal[x][y] = neighbour_agent.is_waste_disposal
            is_wall[x][y] = neighbour_agent.is_wall
            if isinstance(neighbour_agent, RobotAgent):
                other_robots[x][y] = 1
        observation = {
            "radioactivity": radioactivity_level,
            "color_waste": color_waste,
            "is_waste_disposal": is_waste_disposal,
            "is_wall": is_wall,
            "other_robots": other_robots,
            "success": success
        }
        #Update the cell according to the action
        if action in [0, 1, 2, 3] and success:
            cell_agent.color_waste = action
        elif action in [4, 5, 6, 7]:
            new_position = neighbours[action-4]
            self.grid.move_agent(cell_agent, new_position)
        return observation
    
    def reset(self):
        pass
    
    def can_pickup(self, pos):
        #check if there is not another robot here
        cell_agent = self.grid.get_cell_list_contents(pos)
        if len(cell_agent) == 1 and isinstance(cell_agent[0], RobotAgent):
            return False
        return True

