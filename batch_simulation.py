import matplotlib.pyplot as plt
import numpy as np

from agents import RandomGreenAgent, RandomRedAgent, RandomYellowAgent, GreenAgent, YellowAgent
from env import Waste
from model import RobotMission


def run_batch_simu(num_simulations=10, random_agents=True, steps=1000):
    mean_waste_counts = {"green": [], "yellow": [], "red": []}
    for _ in range(num_simulations):
        model = RobotMission(
            n_agents={
                "green": 3,
                "yellow": 3,
                "red": 3,
            },
            n_wastes={
                "green": 10,
                "yellow": 10,
                "red": 10,
            },
            grid_size=20,
            use_random_agents=random_agents,
        )
        waste_counts = visualize_simulation(model, steps=steps, use_random_agents=random_agents)
        for color in waste_counts:
            mean_waste_counts[color].append(waste_counts[color])
    return mean_waste_counts


def visualize_simulation(model, steps, use_random_agents):
    waste_counts = {"green": [], "yellow": [], "red": []}
    if use_random_agents:
        greenagentclass = RandomGreenAgent
        yellowagentclass = RandomYellowAgent
        redagentclass = RandomRedAgent
    else:
        greenagentclass = GreenAgent
        yellowagentclass = YellowAgent
        # redagentclass = GreenAgent
    for step in range(steps):
        model.step()
        green_count, yellow_count, red_count = 0, 0, 0

        # Draw waste and robot agents
        for agent in model.agents:
            if isinstance(agent, Waste) and agent.pos is not None:
                color = ["green", "yellow", "red"][agent.color_waste]
                if color == "green":
                    green_count += 1
                elif color == "yellow":
                    yellow_count += 1
                else:
                    red_count += 1
            elif isinstance(
                agent, (greenagentclass, yellowagentclass, redagentclass)
            ):
                color = (
                    "green"
                    if isinstance(agent, greenagentclass)
                    else "yellow" if isinstance(agent, yellowagentclass) else "red"
                )
        waste_counts["green"].append(green_count)
        waste_counts["yellow"].append(yellow_count)
        waste_counts["red"].append(red_count)
    return waste_counts


if __name__ == "__main__":
    mean_waste_counts = run_batch_simu(num_simulations=20, random_agents=True, steps=200)
    waste_counts_green = mean_waste_counts["green"]
    waste_counts_yellow = mean_waste_counts["yellow"]
    waste_counts_red = mean_waste_counts["red"]

    mean_waste_counts_green = np.mean(waste_counts_green, axis=0)
    mean_waste_counts_yellow = np.mean(waste_counts_yellow, axis=0)
    mean_waste_counts_red = np.mean(waste_counts_red, axis=0)

    plt.plot(
        range(len(mean_waste_counts_green)),
        mean_waste_counts_green,
        label="green",
        color="green",
    )
    plt.plot(
        range(len(mean_waste_counts_yellow)),
        mean_waste_counts_yellow,
        label="yellow",
        color="yellow",
    )
    plt.plot(
        range(len(mean_waste_counts_red)),
        mean_waste_counts_red,
        label="red",
        color="red",
    )

    plt.xlabel("Step")
    plt.ylabel("Waste Count")
    plt.legend()
    plt.show()
