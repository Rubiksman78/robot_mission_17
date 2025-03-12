from mesa import Agent
import random


class RobotAgent(Agent):
    def __init__(self, id, model, knowledge: dict):  # TODO ask yourself how to create model
        super().__init__(model)
        self.id = id
        self.knowledge = knowledge
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
        pass
    
    def update(self, percepts, action): # The robot picks up waste
        if action == 0 and percepts["success"]:
            if self.knowledge["carried"] == []:
                self.knowledge["carried"] = [self.knowledge["color_waste"][1][1]]
            elif self.knowledge["carried"] == [self.knowledge["color_waste"][1][1]]:
                self.knowledge["carried"] = [self.knowledge["color_waste"][1][1] + 1]

        elif action in [1, 2, 3] and percepts["success"]: # The robot drops some waste 
            self.knowledge["carried"].remove(action)

        self.knowledge.update(percepts)

    def step(self):
        action = self.deliberate()
        percepts = self.model.do(self, action)
        self.update(percepts, action)


class GreenAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super.__init__(self, model, knowledge)
        self.treshold = 1 / 3
        self.color_to_gather = 1  # Can only gather green wastes
        self.max_carry = 2

    def deliberate(self):
        if (
            self.knowledge["color_waste"][1, 1] == self.color_to_gather
            and len(self.knowledge["carried"]) < self.max_carry
        ):
            return self.actions_dict["pick"]

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["is_waste_disposal"][1, 1] == 0
        ):
            return self.actions_dict["release"]

        possible_actions = []

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["color_waste"][1, 1] == 0
        ):
            possible_actions.append("release")

        if (
            self.knowledge["other_robots"][2, 2] == 0
            and self.knowledge["radioactivity"][1, 2] <= self.treshold
        ):
            possible_actions.append("move_Right")

        if (
            self.knowledge["other_robots"][0, 2] == 0
            and self.knowledge["radioactivity"][0, 1] <= self.treshold
        ):
            possible_actions.append("move_Up")

        if (
            self.knowledge["other_robots"][0, 0] == 0
            and self.knowledge["radioactivity"][1, 0] <= self.treshold
        ):
            possible_actions.append("move_Left")

        if (
            self.knowledge["other_robots"][2, 0] == 0
            and self.knowledge["radioactivity"][2, 1] <= self.treshold
        ):
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        if action == "release":
            action = action + "_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]


class YellowAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super.__init__(self, model, knowledge)
        self.treshold = 2 / 3
        self.color_to_gather = 2  # Can only gather yellow wastes
        self.max_carry = 2

    def deliberate(self):
        if (
            self.knowledge["color_waste"][1, 1] == self.color_to_gather
            and len(self.knowledge["carried"]) < self.max_carry
        ):
            return self.actions_dict["pick"]

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["is_waste_disposal"][1, 1] == 0
        ):
            return self.actions_dict["release"]

        possible_actions = []

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["color_waste"][1, 1] == 0
        ):
            possible_actions.append("release")

        if (
            self.knowledge["other_robots"][2, 2] == 0
            and self.knowledge["radioactivity"][1, 2] <= self.treshold
        ):
            possible_actions.append("move_Right")

        if (
            self.knowledge["other_robots"][0, 2] == 0
            and self.knowledge["radioactivity"][0, 1] <= self.treshold
        ):
            possible_actions.append("move_Up")

        if (
            self.knowledge["other_robots"][0, 0] == 0
            and self.knowledge["radioactivity"][1, 0] <= self.treshold
        ):
            possible_actions.append("move_Left")

        if (
            self.knowledge["other_robots"][2, 0] == 0
            and self.knowledge["radioactivity"][2, 1] <= self.treshold
        ):
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        if action == "release":
            action = action + "_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]


class RedAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super.__init__(self, model, knowledge)
        self.treshold = 1
        self.color_to_gather = 2  # Can only gather yellow wastes
        self.max_carry = 1

    def deliberate(self):
        if (
            self.knowledge["color_waste"][1, 1] == self.color_to_gather
            and len(self.knowledge["carried"]) < self.max_carry
        ):
            return self.actions_dict["pick"]

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["is_waste_disposal"][1, 1] == 0
        ):
            return self.actions_dict["release"]

        possible_actions = []

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["color_waste"][1, 1] == 0
        ):
            possible_actions.append("release")

        if (
            self.knowledge["other_robots"][2, 2] == 0
            and self.knowledge["radioactivity"][1, 2] <= self.treshold
        ):
            possible_actions.append("move_Right")

        if (
            self.knowledge["other_robots"][0, 2] == 0
            and self.knowledge["radioactivity"][0, 1] <= self.treshold
        ):
            possible_actions.append("move_Up")

        if (
            self.knowledge["other_robots"][0, 0] == 0
            and self.knowledge["radioactivity"][1, 0] <= self.treshold
        ):
            possible_actions.append("move_Left")

        if (
            self.knowledge["other_robots"][2, 0] == 0
            and self.knowledge["radioactivity"][2, 1] <= self.treshold
        ):
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        if action == "release":
            action = action + "_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]
