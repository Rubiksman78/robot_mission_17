import matplotlib.pyplot as plt
import tkinter as tk
from agents import GreenAgent, YellowAgent, RedAgent
from env import Waste
from model import RobotMission   
from matplotlib import colors as mcolors

def visualize_simulation(model, steps=50):
    fig, ax = plt.subplots()
    
    for step in range(steps):
        model.step()
        ax.clear()
        
        # Draw heatmap for radioactivity
        cmap = mcolors.ListedColormap(["lightgreen", "lightyellow", "lightcoral", "black"])
        bounds = [0, 0.1, 0.6, 1.5, 2.1]  # Define thresholds for different levels
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        ax.imshow(model.radioactivity_map, cmap=cmap, norm=norm, origin="upper", alpha=0.6)
        
        # Draw waste and robot agents
        for agent in model.agents:
            if isinstance(agent, Waste) and agent.pos is not None:
                color = ['green', 'yellow', 'red'][agent.color_waste]
                ax.scatter(agent.pos[0], agent.pos[1], color=color, marker='s', edgecolors='black', s=100)
            elif isinstance(agent, (GreenAgent, YellowAgent, RedAgent)):
                color = 'green' if isinstance(agent, GreenAgent) else 'yellow' if isinstance(agent, YellowAgent) else 'red'
                ax.scatter(agent.pos[0], agent.pos[1], color=color, marker='o', edgecolors='black', s=100)
        
        ax.set_xlim(-0.5, model.grid_size - 0.5)
        ax.set_ylim(-0.5, model.grid_size - 0.5)
        ax.set_xticks(range(model.grid_size))
        ax.set_yticks(range(model.grid_size))
        ax.set_title(f"Step: {step}")
        plt.pause(0.2)
    
def start_gui():
    def run_simulation():
        model = RobotMission(
            n_agents={'green': green_var.get(), 'yellow': yellow_var.get(), 'red': red_var.get()},
            n_wastes={'green': green_waste_var.get(), 'yellow': yellow_waste_var.get(), 'red': red_waste_var.get()},
            grid_size=grid_size_var.get()
        )
        visualize_simulation(model, steps=steps_var.get())
    
    root = tk.Tk()
    root.title("Simulation Settings")
    
    tk.Label(root, text="Number of Steps").pack()
    steps_var = tk.IntVar(value=50)
    tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, variable=steps_var).pack()

    tk.Label(root, text="Grid Size").pack()
    grid_size_var = tk.IntVar(value=10)
    tk.Scale(root, from_=5, to=30, orient=tk.HORIZONTAL, variable=grid_size_var).pack()
    
    green_var = tk.IntVar(value=3)
    yellow_var = tk.IntVar(value=3)
    red_var = tk.IntVar(value=3)
    
    tk.Label(root, text="Green Robots").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=green_var).pack()
    
    tk.Label(root, text="Yellow Robots").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=yellow_var).pack()
    
    tk.Label(root, text="Red Robots").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=red_var).pack()
    
    green_waste_var = tk.IntVar(value=5)
    yellow_waste_var = tk.IntVar(value=5)
    red_waste_var = tk.IntVar(value=5)
    
    tk.Label(root, text="Green Waste").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=green_waste_var).pack()
    
    tk.Label(root, text="Yellow Waste").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=yellow_waste_var).pack()
    
    tk.Label(root, text="Red Waste").pack()
    tk.Scale(root, from_=0, to=20, orient=tk.HORIZONTAL, variable=red_waste_var).pack()
    
    tk.Button(root, text="Run Simulation", command=run_simulation).pack()
    tk.Button(root, text="Close Simulation", command=root.destroy).pack()
    root.mainloop()
    
if __name__ == "__main__":
    start_gui()
