### OUTDATED DON'T USE ###

from IPython import display

from agents import GreenAgent, RedAgent, YellowAgent
from env import Radioactivity, Waste
from model import RobotMission

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
        # print radioactivity of neighbours
    plt.title("Step: " + str(i))
    plt.pause(0.001)
    display.display(plt.gcf())
    display.clear_output(wait=True)
