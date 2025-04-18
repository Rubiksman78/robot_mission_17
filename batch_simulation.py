import argparse

import matplotlib.pyplot as plt
import numpy as np
import tqdm
import yaml

from agents import (GreenAgent, RandomGreenAgent, RandomRedAgent,
                    RandomYellowAgent, RedAgent, YellowAgent)
from env import Waste
from message.MessageService import MessageService
from model import RobotMission


def run_batch_simu(num_simulations, random_agents, steps):
    mean_waste_counts = {"green": [], "yellow": [], "red": []}
    with open("configs/batch_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    for _ in tqdm.tqdm(range(num_simulations)):
        model = RobotMission(
            n_agents={
                "green": config["green_robots"],
                "yellow": config["yellow_robots"],
                "red": config["red_robots"],
            },
            n_wastes={
                "green": config["green_wastes"],
                "yellow": config["yellow_wastes"],
                "red": config["red_wastes"],
            },
            grid_size=config["grid_size"],
            use_random_agents=random_agents,
        )
        MessageService.get_instance().set_instant_delivery(True)
        waste_counts = visualize_simulation(
            model, steps=steps, use_random_agents=random_agents
        )
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
        redagentclass = RedAgent
    for step in range(steps):
        model.step()
        green_count, yellow_count, red_count = 0, 0, 0
        for agent in model.agents:
            if isinstance(agent, Waste) and agent.pos is not None:
                color = ["green", "yellow", "red"][agent.color_waste]
                if color == "green":
                    green_count += 1
                elif color == "yellow":
                    yellow_count += 1
                else:
                    red_count += 1
            elif isinstance(agent, (greenagentclass, yellowagentclass, redagentclass)):
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
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--n_sim",
        type=int,
        default=20,
        help="Number of simulations to run",
    )
    argparser.add_argument(
        "--steps", type=int, default=400, help="Number of steps to run the simulation"
    )
    argparser.add_argument(
        "--do_random", action="store_true", help="Use random agents", default=False
    )
    args = argparser.parse_args()
    mean_waste_counts = run_batch_simu(
        num_simulations=args.n_sim, random_agents=args.do_random, steps=args.steps
    )
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

    # Compute the AUC for each color
    auc_green = np.trapz(mean_waste_counts_green, dx=1) / (
        args.steps * mean_waste_counts_green[0]
    )
    auc_yellow = np.trapz(mean_waste_counts_yellow, dx=1) / (
        args.steps * mean_waste_counts_yellow[0]
    )
    auc_red = np.trapz(mean_waste_counts_red, dx=1) / (
        args.steps * mean_waste_counts_red[0]
    )
    max_wastes = max(
        mean_waste_counts_green[0],
        mean_waste_counts_yellow[0],
        mean_waste_counts_red[0],
    )
    plt.xlabel("Step")
    plt.ylabel("Waste Count")
    plt.text(
        args.steps / 2,
        max_wastes - 1,
        f"Score green: {1-auc_green:.2f}\nScore yellow: {1-auc_yellow:.2f}\nScore red: {1-auc_red:.2f}",
    )
    plt.legend()
    plt.show()
