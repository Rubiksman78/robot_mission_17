import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

from agents import GreenAgent, RandomRedAgent, YellowAgent
from env import Waste
from model import RobotMission


def visualize_simulation(model, steps=50):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ax, ax_right = axes

    waste_counts = {"green": [], "yellow": [], "red": []}

    for step in range(steps):
        model.step()
        ax.clear()
        ax_right.clear()

        # Draw heatmap for radioactivity
        cmap = mcolors.ListedColormap(
            ["lightgreen", "lightyellow", "lightcoral", "black"]
        )
        bounds = [0, 0.1, 0.6, 1.5, 2.1]  # Define thresholds for different levels
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        ax.imshow(
            model.radioactivity_map, cmap=cmap, norm=norm, origin="upper", alpha=0.6
        )

        # Track waste counts
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
                ax.scatter(
                    agent.pos[0],
                    agent.pos[1],
                    color=color,
                    marker="s",
                    edgecolors="black",
                    s=100,
                    alpha=0.5,
                )
            elif isinstance(agent, (GreenAgent, YellowAgent, RandomRedAgent)):
                color = (
                    "green"
                    if isinstance(agent, GreenAgent)
                    else "yellow"
                    if isinstance(agent, YellowAgent)
                    else "red"
                )
                ax.scatter(
                    agent.pos[0],
                    agent.pos[1],
                    color=color,
                    marker="o",
                    edgecolors="black",
                    s=100,
                )

        # Update waste count history
        waste_counts["green"].append(green_count)
        waste_counts["yellow"].append(yellow_count)
        waste_counts["red"].append(red_count)

        # Plot waste count trends
        ax_right.plot(waste_counts["green"], color="green", label="Green Waste")
        ax_right.plot(waste_counts["yellow"], color="yellow", label="Yellow Waste")
        ax_right.plot(waste_counts["red"], color="red", label="Red Waste")
        ax_right.set_title("Waste Counts Over Time")
        ax_right.set_xlabel("Steps")
        ax_right.set_ylabel("Count")
        ax_right.legend()

        ax.set_xlim(-0.5, model.grid_size - 0.5)
        ax.set_ylim(-0.5, model.grid_size - 0.5)
        ax.set_xticks(range(model.grid_size))
        ax.set_yticks(range(model.grid_size))
        ax.set_title(f"Step: {step}")

        plt.pause(0.2)


def start_gui():
    def run_simulation():
        model = RobotMission(
            n_agents={
                "green": green_var.get(),
                "yellow": yellow_var.get(),
                "red": red_var.get(),
            },
            n_wastes={
                "green": green_waste_var.get(),
                "yellow": yellow_waste_var.get(),
                "red": red_waste_var.get(),
            },
            grid_size=grid_size_var.get(),
            use_random_agents=use_random_agents.get(),
        )
        visualize_simulation(model, steps=steps_var.get())

    root = tk.Tk()
    root.title("Simulation Settings")

    tk.Label(root, text="Number of Steps").pack()
    steps_var = tk.IntVar(value=100)
    tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, variable=steps_var).pack()

    tk.Label(root, text="Grid Size").pack()
    grid_size_var = tk.IntVar(value=10)
    tk.Scale(root, from_=5, to=30, orient=tk.HORIZONTAL, variable=grid_size_var).pack()

    green_var = tk.IntVar(value=3)
    yellow_var = tk.IntVar(value=3)
    red_var = tk.IntVar(value=3)
    use_random_agents = tk.BooleanVar(value=True)

    tk.Label(root, text="Use Random Agents").pack()
    tk.Checkbutton(
        root, variable=use_random_agents, onvalue=True, offvalue=False
    ).pack()

    tk.Label(root, text="Green Robots").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=green_var).pack()

    tk.Label(root, text="Yellow Robots").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=yellow_var).pack()

    tk.Label(root, text="Red Robots").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=red_var).pack()

    green_waste_var = tk.IntVar(value=10)
    yellow_waste_var = tk.IntVar(value=10)
    red_waste_var = tk.IntVar(value=10)

    tk.Label(root, text="Green Waste").pack()
    tk.Scale(
        root, from_=0, to=20, orient=tk.HORIZONTAL, variable=green_waste_var
    ).pack()

    tk.Label(root, text="Yellow Waste").pack()
    tk.Scale(
        root, from_=0, to=20, orient=tk.HORIZONTAL, variable=yellow_waste_var
    ).pack()

    tk.Label(root, text="Red Waste").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=red_waste_var).pack()

    tk.Button(root, text="Run Simulation", command=run_simulation).pack()
    tk.Button(root, text="Close Simulation", command=root.destroy).pack()
    root.mainloop()


if __name__ == "__main__":
    start_gui()
