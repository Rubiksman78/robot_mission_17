from mesa import Agent
import random
import numpy as np

EMPTY = -1
WALL = 0


class RobotAgent(Agent):
    def __init__(self, model, knowledge: dict):  # TODO ask yourself how to create model
        super().__init__(model)
        self.knowledge = knowledge
        self.colors_ids = {0: "green", 1: "yellow", 2: "red"}
        self.actions_dict = {
            "pick": 0,
            "release_green": 1,
            "release_yellow": 2,
            "release_red": 3,
            "move_Up": 4,
            "move_Right": 5,
            "move_Down": 6,
            "move_Left": 7,
            "nothing": 8,
        }
        #self.grid_size = self.knowledge["grid_size"]
        self.grid_size = self.model.grid_size
        self.grid = np.zeros((self.grid_size + 2, self.grid_size + 2)) - 1
        self.color_to_gather = - 1

    def deliberate(self):
        pass

    def update(self, percepts, action):  # The robot picks up waste
        # TODO Change this to remember the previous objects found in the way but not used
        if action == self.actions_dict["pick"] and percepts["success"]:
            if self.knowledge["carried"] == []:
                self.knowledge["carried"] = [self.knowledge["color_waste"][1][1]]
            elif self.knowledge["carried"] == [self.knowledge["color_waste"][1][1]]:
                self.knowledge["carried"] = [self.knowledge["color_waste"][1][1] + 1]

        elif (
            action
            in [
                self.actions_dict["release_green"],
                self.actions_dict["release_yellow"],
                self.actions_dict["release_red"],
            ]
            and percepts["success"]
        ):  # The robot drops some waste
            self.knowledge["carried"] = []

        '''elif (
            action
            in [
                self.actions_dict["move_Up"],
                self.actions_dict["move_Right"],
                self.actions_dict["move_Down"],
                self.actions_dict["move_Left"],
            ]
            and percepts["success"]
        ):  
            if action == self.actions_dict["move_Up"]:
                self.knowledge["position"][0] += 1 
            elif action == self.actions_dict["move_Down"]:
                self.knowledge["position"][0] += -1
            elif action == self.actions_dict["move_Right"]:
                self.knowledge["position"][1] += 1
            else:
                self.knowledge["position"][1] += -1'''

        #update known environment
        i, j = self.pos
        i+=1
        j+=1
        mask = percepts["color_waste"] == self.color_to_gather

        self.grid[i-1:i+2, j-1:j+2][mask] = percepts["color_waste"][mask]
        self.knowledge.update(percepts)

    def step(self):
        action = self.deliberate()
        percepts = self.model.do(self, action)
        self.update(percepts, action)


class RandomGreenAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.threshold = 1 / 3
        self.color_to_gather = 0  # Can only gather green wastes

    def deliberate(self):
        if self.knowledge["color_waste"][1, 1] == self.color_to_gather and (
            len(self.knowledge["carried"]) == 0
            or self.knowledge["carried"][0] == self.color_to_gather
        ):
            return self.actions_dict["pick"]

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["is_waste_disposal"][1, 1] == 1
        ):
            return self.actions_dict[
                "release_" + self.colors_ids[self.knowledge["carried"][0]]
            ]

        possible_actions = []

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["color_waste"][1, 1] == 0
        ):
            possible_actions.append(
                "release_" + self.colors_ids[self.knowledge["carried"][0]]
            )

        if 0 <= self.knowledge["radioactivity"][2, 1] <= self.threshold:
            possible_actions.append("move_Right")

        if 0 <= self.knowledge["radioactivity"][1, 2] <= self.threshold:
            possible_actions.append("move_Up")

        if 0 <= self.knowledge["radioactivity"][0, 1] <= self.threshold:
            possible_actions.append("move_Left")

        if 0 <= self.knowledge["radioactivity"][1, 0] <= self.threshold:
            possible_actions.append("move_Down")

        if len(possible_actions) == 0:
            action = "nothing"
        else:
            action = random.choice(possible_actions)

        if action == "release":
            action +="_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]


class RandomYellowAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.threshold = 2 / 3
        self.color_to_gather = 1  # Can only gather yellow wastes

    def deliberate(self):
        if self.knowledge["color_waste"][1, 1] == self.color_to_gather and (
            len(self.knowledge["carried"]) == 0
            or self.knowledge["carried"][0] == self.color_to_gather
        ):
            return self.actions_dict["pick"]

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["is_waste_disposal"][1, 1] == 1
        ):
            return self.actions_dict[
                "release_" + self.colors_ids[self.knowledge["carried"][0]]
            ]

        possible_actions = []

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["color_waste"][1, 1] == 0
        ):
            possible_actions.append(
                "release_" + self.colors_ids[self.knowledge["carried"][0]]
            )

        if 0 <= self.knowledge["radioactivity"][2, 1] <= self.threshold:
            possible_actions.append("move_Right")

        if 0 <= self.knowledge["radioactivity"][1, 2] <= self.threshold:
            possible_actions.append("move_Up")

        if 0 <= self.knowledge["radioactivity"][0, 1] <= self.threshold:
            possible_actions.append("move_Left")

        if 0 <= self.knowledge["radioactivity"][1, 0] <= self.threshold:
            possible_actions.append("move_Down")

        if len(possible_actions) == 0:
            action = "nothing"
        else:
            action = random.choice(possible_actions)

        if action == "release":
            action = "_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]


class RandomRedAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.threshold = 1
        self.color_to_gather = 2  # Can only gather red wastes

    def deliberate(self):
        if self.knowledge["color_waste"][1, 1] == self.color_to_gather and (
            len(self.knowledge["carried"]) == 0
        ):
            return self.actions_dict["pick"]

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["is_waste_disposal"][1, 1] == 1
        ):
            return self.actions_dict[
                "release_" + self.colors_ids[self.knowledge["carried"][0]]
            ]

        possible_actions = []

        if (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["color_waste"][1, 1] == 0
        ):
            possible_actions.append(
                "release_" + self.colors_ids[self.knowledge["carried"][0]]
            )

        if 0 <= self.knowledge["radioactivity"][2, 1] <= self.threshold:
            possible_actions.append("move_Right")

        if 0 <= self.knowledge["radioactivity"][1, 2] <= self.threshold:
            possible_actions.append("move_Up")

        if 0 <= self.knowledge["radioactivity"][0, 1] <= self.threshold:
            possible_actions.append("move_Left")

        if 0 <= self.knowledge["radioactivity"][1, 0] <= self.threshold:
            possible_actions.append("move_Down")

        if len(possible_actions) == 0:
            action = "nothing"
        else:
            action = random.choice(possible_actions)

        if action == "release":
            action += "_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]

class GreenAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super.__init__(model, knowledge)
        self.treshold = 1 / 3
        self.color_to_gather = 1  # Can only gather green wastes
        self.begin = True
        self.yellow_deposit_not_available = False

    def random_walk(self):
        possible_actions = []

        if self.knowledge["radioactivity"][1, 2] <= self.treshold:
            possible_actions.append("move_Right")

        if self.knowledge["radioactivity"][0, 1] <= self.treshold:
            possible_actions.append("move_Up")

        if self.knowledge["radioactivity"][1, 0] <= self.treshold:
            possible_actions.append("move_Left")

        if self.knowledge["radioactivity"][2, 1] <= self.treshold:
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        return action

    def is_on_yellow_deposit(self):
        pass

    def is_on_green_deposit(self):
        pass

    def is_on_correct_waste(self):
        return self.knowledge["color_waste"][1, 1] == self.color_to_gather

    def must_deliver(self):
        return (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["carried"][0] != self.color_to_gather
        )

    def has_one_correct_waste(self):
        return (
            len(self.knowledge["carried"]) > 0
            and self.knowledge["carried"][0] == self.color_to_gather
        )

    def go_to_green_deposit(self):
        pass  # TODO: go up until wall then right until yellow zone

    def go_to_yellow_deposit(self):
        pass  # TODO: go right until yellow zone then down until wall

    def can_release(self):
        return self.knowledge["color_waste"][1, 1] == EMPTY

    def release(self):
        return self.actions_dict[
            "release_" + self.colors_ids[self.knowledge["carried"][0]]
        ]

    def pick(self):
        return self.actions_dict["pick"]

    def act_in_yellow_deposit(self):
        if self.can_release():
            return self.release()

        else:
            self.yellow_deposit_not_available = True
            return self.deliberate()

    def find_place_to_deliver(self):
        pass

    def reachable_waste(self):
        reachable_mask = self.knowledge["radioactivity"] <= self.treshold
        correct_wastes = self.knowledge["color_waste"] == self.color_to_gather
        return (reachable_mask * correct_wastes).any()

    def reach_waste(self):
        if self.is_on_correct_waste():
            return self.pick()
        pass

    def deliberate(self):
        if self.begin:
            if not self.is_on_yellow_deposit():
                return self.go_to_yellow_deposit()
            else:
                self.begin = False

        if self.must_deliver():
            if self.yellow_deposit_not_available:
                if self.can_release():
                    return self.release()

                else:
                    return self.find_place_to_deliver()

            elif self.is_on_yellow_deposit():
                return self.act_in_yellow_deposit()

            else:
                return self.go_to_yellow_deposit()

        self.yellow_deposit_not_available = False

        if self.reachable_waste():
            return self.reach_waste()

        if self.has_one_correct_waste():
            if self.is_on_green_deposit():
                if self.can_release():
                    return self.release()
            else:
                return self.go_to_green_deposit()

        return self.random_walk()