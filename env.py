import numpy as np
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
    7: "move_left",
}


class Waste(Agent):
    def __init__(self, model: Model, color_waste=0):
        super().__init__(model)
        self.color_waste = color_waste


class Radioactivity(Agent):
    def __init__(self, model, radioactivity_level=0, is_waste_disposal=0, is_wall=0):
        super().__init__(model)
        self.radioactivity_level = radioactivity_level
        self.is_waste_disposal = is_waste_disposal
        self.is_wall = is_wall


class Environment:
    def __init__(self, model, grid: MultiGrid):
        self.model = model
        self.grid = grid
        self.width = grid.width
        self.height = grid.height

    def step(self, agent, action):
        # called in model.do
        # desired output is [radioactivity_level 3*3, color_waste 3*3, is_waste_disposal 3*3, is_wall 3*3, other_robots 3*3, success]
        pos = agent.pos
        cell_agent = self.grid.get_cell_list_contents(pos)  # get agents at the same pos as the robot (Waste+Radioactivity)
        # neighbours = self.grid.get_neighborhood(pos, moore=True, include_center=False)
        observation = self.get_info(pos)
        success = observation["success"]
        # Update the cell according to the action
        position_moved = None
        if action != 8:
            if action == 0 and success:
                for agent in cell_agent:
                    if isinstance(agent, Waste):
                        self.grid.remove_agent(agent)
            if action in [1, 2, 3]:
                for agent in cell_agent:
                    if isinstance(agent, Radioactivity):
                        is_waste_disposal = agent.is_waste_disposal
                if is_waste_disposal == 0:
                    waste_agent = Waste(self.model, color_waste=action - 1)
                    self.grid.place_agent(waste_agent, pos)
                else:
                    for agent in cell_agent:
                        if isinstance(agent, Waste):
                            self.grid.remove_agent(agent)
            elif action in [4, 5, 6, 7]:
                if action == 4:#up
                    new_position = (pos[0], pos[1] + 1)
                elif action == 5:#right
                    new_position = (pos[0] + 1, pos[1])
                elif action == 6:#down
                    new_position = (pos[0], pos[1] -1)
                elif action == 7:#left
                    new_position = (pos[0] - 1, pos[1])
                agent_newpos = self.grid.get_cell_list_contents(new_position)
                agent_already_here = False
                for agent_new in agent_newpos:
                    if isinstance(agent_new, RobotAgent):
                        agent_already_here = True
                if (
                    0 <= new_position[0] < self.width
                    and 0 <= new_position[1] < self.height
                ) and not agent_already_here:
                    self.grid.move_agent(agent, new_position)
                    position_moved = new_position
        if position_moved is None:
            position_moved = pos
        new_observation = self.get_info(position_moved)
        return new_observation

    def get_info(self, pos):
        # Get information from neighbouts
        radioactivity_level = np.zeros((3, 3))-1
        color_waste = np.zeros((3, 3))-1
        is_waste_disposal = np.zeros((3, 3)) - 1
        is_wall = np.zeros((3, 3))
        other_robots = np.zeros((3, 3))
        neighbours = self.grid.get_neighborhood(pos, moore=True, include_center=True)
        success = self.can_pickup(pos)
        for i, neighbour in enumerate(neighbours):
            neighbour_agent = self.grid.get_cell_list_contents(neighbour)
            if len(neighbour_agent) == 0:
                print(neighbour)
                raise ValueError
            waste_agent, radioactivity_agent, robot_agent = None, None, None
            for agent in neighbour_agent:
                if isinstance(agent, Waste):
                    waste_agent = agent
                elif isinstance(agent, Radioactivity):
                    radioactivity_agent = agent
                elif isinstance(agent, RobotAgent):
                    robot_agent = agent
            #compute position in the 3*3 matrix while considering edges
            x_neigh, y_neigh = neighbour
            x = (x_neigh - pos[0] + 1) % 3
            y = (y_neigh - pos[1] + 1) % 3
            radioactivity_level[x][y] = radioactivity_agent.radioactivity_level
            is_waste_disposal[x][y] = radioactivity_agent.is_waste_disposal
            is_wall[x][y] = radioactivity_agent.is_wall
            if waste_agent is not None:
                color_waste[x][y] = waste_agent.color_waste
            if robot_agent is not None:
                other_robots[x][y] = 1
        color_waste = color_waste.astype(int)
        radioactivity_level = np.rot90(radioactivity_level)
        is_waste_disposal = np.rot90(is_waste_disposal)
        is_wall = np.rot90(is_wall)
        other_robots = np.rot90(other_robots)
        observation = {
            "radioactivity": radioactivity_level,
            "color_waste": color_waste,
            "is_waste_disposal": is_waste_disposal,
            "is_wall": is_wall,
            "other_robots": other_robots,
            "success": success,
        }
        return observation

    def reset(self):
        pass

    def can_pickup(self, pos):
        # check if there is not another robot here
        cell_agent = self.grid.get_cell_list_contents(pos)
        count_agent = 0
        for agent in cell_agent:
            if isinstance(agent, RobotAgent):
                count_agent += 1
        if count_agent > 1:
            return False
        return True
