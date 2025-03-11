import random


class RobotAgent:
    def __init__(self):
        pass


class GreenAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super.__init__(self, model, knowledge)
        self.treshold = 1 / 3
        self.color_to_gather = 1  # Can only gather green wastes
        self.colors_ids = {1: "green", 2: "yellow", 3: "red"}
        self.actions_dict = {
            "pick": 0,
            "release_green": 1,
            "release_yellow": 2,
            "release_red": 3,
            "move_Up": 4,
            "move_Right": 5,
            "move_Down": 6,
            "move_Left": 7,
        }

    def deliberate(self):
        if self.knowledge.color_waste[1, 1] == self.color_to_gather:
            return self.actions_dict["pick"]

        possible_actions = []

        if len(self.knowledge.carried) > 0 and self.knowledge.color_waste[1, 1] == 0:
            possible_actions.append("release")

        if self.knowledge.other_robots[2, 2] == 0:
            possible_actions.append("move_Right")

        if self.knowledge.other_robots[0, 2] == 0:
            possible_actions.append("move_Up")

        if self.knowledge.other_robots[0, 0] == 0:
            possible_actions.append("move_Left")

        if self.knowledge.other_robots[2, 0] == 0:
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        if action == "release":
            action = action + "_" + self.colors_ids[self.knowledge.carried[0]]

        return self.actions_dict[action]
