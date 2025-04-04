import random

import numpy as np
from mesa import Agent

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
        # self.grid_size = self.knowledge["grid_size"]
        self.grid_size = self.model.grid_size
        self.grid = np.zeros((self.grid_size + 2, self.grid_size + 2)) - 1
        self.color_to_gather = -1

        self.green_threshold = 1 / 3
        self.yellow_threshold = 2 / 3
        self.red_threshold = 1

    def get_pos(self):
        i,j = self.pos
        return i+1, j+1

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


        i, j = self.pos[0] + 1, self.pos[1] + 1 

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
        self.threshold = self.green_threshold
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

        if 0 <= self.knowledge["radioactivity"][1, 2] <= self.threshold:
            possible_actions.append("move_Right")

        if 0 <= self.knowledge["radioactivity"][0, 1] <= self.threshold:
            possible_actions.append("move_Up")

        if 0 <= self.knowledge["radioactivity"][1, 0] <= self.threshold:
            possible_actions.append("move_Left")

        if 0 <= self.knowledge["radioactivity"][2, 1] <= self.threshold:
            possible_actions.append("move_Down")

        if len(possible_actions) == 0:
            action = "nothing"
        else:
            action = random.choice(possible_actions)

        if action == "release":
            action += "_" + self.colors_ids[self.knowledge["carried"][0]]

        return self.actions_dict[action]


class RandomYellowAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.threshold = self.yellow_threshold
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

        if 0 <= self.knowledge["radioactivity"][1, 2] <= self.threshold:
            possible_actions.append("move_Right")

        if 0 <= self.knowledge["radioactivity"][0, 1] <= self.threshold:
            possible_actions.append("move_Up")

        if 0 <= self.knowledge["radioactivity"][1, 0] <= self.threshold:
            possible_actions.append("move_Left")

        if 0 <= self.knowledge["radioactivity"][2, 1] <= self.threshold:
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
        self.threshold = self.red_threshold
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

        if 0 <= self.knowledge["radioactivity"][1, 2] <= self.threshold:
            possible_actions.append("move_Right")

        if 0 <= self.knowledge["radioactivity"][0, 1] <= self.threshold:
            possible_actions.append("move_Up")

        if 0 <= self.knowledge["radioactivity"][1, 0] <= self.threshold:
            possible_actions.append("move_Left")

        if 0 <= self.knowledge["radioactivity"][2, 1] <= self.threshold:
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
        super().__init__(model, knowledge)
        self.color_to_gather = 1  # Can only gather green wastes
        self.begin = True
        self.yellow_deposit_not_available = False
        self.go_up = True

    def random_walk(self):
        possible_actions = []

        if (
            self.knowledge["radioactivity"][1, 2] <= self.green_threshold
            and not self.wall_map()[1, 2]
        ):
            possible_actions.append("move_Right")

        if (
            self.knowledge["radioactivity"][0, 1] <= self.green_threshold
            and not self.wall_map()[0, 1]
        ):
            possible_actions.append("move_Up")

        if (
            self.knowledge["radioactivity"][1, 0] <= self.green_threshold
            and not self.wall_map()[1, 0]
        ):
            possible_actions.append("move_Left")

        if (
            self.knowledge["radioactivity"][2, 1] <= self.green_threshold
            and not self.wall_map()[2, 1]
        ):
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        return self.actions_dict[action]

    def wall_map(self):
        return self.knowledge["radioactivity"] == -1

    def is_on_yellow_deposit(self):
        return (
            (self.wall_map()[2, :]).all()
            and (self.knowledge["radioactivity"][:, 2] > self.green_threshold).all()
            and (self.knowledge["radioactivity"][:, :2] <= self.green_threshold).all()
        )

    def is_on_green_deposit(self):
        return (
            (self.wall_map()[0, :]).all()
            and (self.knowledge["radioactivity"][:, 2] > self.green_threshold).all()
            and (self.knowledge["radioactivity"][:, :2] <= self.green_threshold).all()
        )

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
        possible_actions = []
        if not self.wall_map()[0, 1]:
            possible_actions.append("move_Up")

        if self.knowledge["radioactivity"][1, 2] <= self.green_threshold:
            possible_actions.append("move_Right")

        action = random.choice(possible_actions)
        return self.actions_dict[action]

    def go_to_init_position(self):
        if self.knowledge["radioactivity"][1, 2] <= self.green_threshold:
            action = "move_Right"

        else:
            action = "move_Down"

        return self.actions_dict[action]

    def go_to_yellow_deposit(self):
        possible_actions = []
        if not self.wall_map()[2, 1]:
            possible_actions.append("move_Down")

        if self.knowledge["radioactivity"][1, 2] <= self.green_threshold:
            possible_actions.append("move_Right")

        action = random.choice(possible_actions)
        return self.actions_dict[action]

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
        if self.go_up:
            if self.wall_map()[0, 1]:
                if not self.wall_map()[1, 0]:
                    self.go_up = False
                    return self.actions_dict["move_Left"]
                else:
                    self.go_up = True
                    self.yellow_deposit_not_available = False
                    return (
                        self.deliberate()
                    )  # go back to yellow deposit and start again
            else:
                return self.actions_dict["move_Up"]
        else:
            if self.wall_map()[2, 1]:
                if not self.wall_map()[1, 0]:
                    self.go_up = True
                    return self.actions_dict["move_Left"]
                else:
                    self.go_up = True
                    self.yellow_deposit_not_available = False
                    return (
                        self.deliberate()
                    )  # go back to yellow deposit and start again
            else:
                return self.actions_dict["move_Down"]

    def reachable_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == 1)
        targets = [
            position
            for position in targets
            if position
            != [
                len(self.knowledge["grid"]) - 1,
                len([self.knowledge["grid"][len(self.knowledge["grid"]) - 1]]) - 1,
            ]
        ]  # do not look for green waste in green deposit
        return len(targets) > 0

    def find_nearest_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == 1)
        targets = np.array(
            [
                position
                for position in targets
                if position
                != [
                    len(self.knowledge["grid"]) - 1,
                    len([self.knowledge["grid"][len(self.knowledge["grid"]) - 1]]) - 1,
                ]
            ]
        )  # do not look for green waste in green deposit
        if len(targets) == 0:
            return None

        x, y = self.knowledge["position"]

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (targets[:, 1], targets[:, 0], distances)
        )  # en cas d'égalité des distances, le plus en haut à droite gagne

        return tuple(targets[sorted_indices[0]])

    def reach_waste(self):
        if self.is_on_correct_waste():
            return self.pick()

        possible_actions = []
        targetx, targety = self.find_nearest_waste()
        x, y = self.knowledge["position"]
        if targetx > x:
            possible_actions.append("move_Right")
        elif targetx < x:
            possible_actions.append("move_Left")
        if targety > y:
            possible_actions.append("move_Right")
        elif targety < y:
            possible_actions.append("move_Left")

        action = random.choice(possible_actions)
        return self.actions_dict[action]

    def deliberate(self):
        if self.begin:
            if not self.is_on_yellow_deposit():
                return self.go_to_init_position()
            else:
                self.begin = False

        if self.must_deliver():
            if self.yellow_deposit_not_available:
                if self.can_release() and not self.is_on_green_deposit():
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


class YellowAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.color_to_gather = 2  # Can only gather yellow wastes
        self.begin = True
        self.red_deposit_not_available = False
        self.go_up = True

    def random_walk(self):
        possible_actions = []

        if (
            self.knowledge["radioactivity"][1, 2] <= self.yellow_threshold
            and not self.wall_map()[1, 2]
        ):
            possible_actions.append("move_Right")

        if (
            self.knowledge["radioactivity"][0, 1] <= self.yellow_threshold
            and not self.wall_map()[0, 1]
        ):
            possible_actions.append("move_Up")

        if (
            self.knowledge["radioactivity"][1, 0] <= self.yellow_threshold
            and not self.wall_map()[1, 0]
        ):
            possible_actions.append("move_Left")

        if (
            self.knowledge["radioactivity"][2, 1] <= self.yellow_threshold
            and not self.wall_map()[2, 1]
        ):
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)

        return self.actions_dict[action]

    def wall_map(self):
        return self.knowledge["radioactivity"] == -1

    def is_on_yellow_deposit(self):
        return (
            (self.wall_map()[2, :]).all()
            and (self.knowledge["radioactivity"][:, 2] > self.green_threshold).all()
            and (self.knowledge["radioactivity"][:, :2] <= self.green_threshold).all()
        )

    def is_on_green_deposit(self):
        return (
            (self.wall_map()[0, :]).all()
            and (self.knowledge["radioactivity"][:, 2] > self.green_threshold).all()
            and (self.knowledge["radioactivity"][:, :2] <= self.green_threshold).all()
        )

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
        possible_actions = []
        if not self.wall_map()[0, 1]:
            possible_actions.append("move_Up")

        if self.knowledge["radioactivity"][1, 2] <= self.green_threshold:
            possible_actions.append("move_Right")

        action = random.choice(possible_actions)
        return self.actions_dict[action]

    def go_to_init_position(self):
        if self.knowledge["radioactivity"][1, 2] <= self.green_threshold:
            action = "move_Right"

        else:
            action = "move_Down"

        return self.actions_dict[action]

    def go_to_yellow_deposit(self):
        possible_actions = []
        if not self.wall_map()[2, 1]:
            possible_actions.append("move_Down")

        if self.knowledge["radioactivity"][1, 2] <= self.green_threshold:
            possible_actions.append("move_Right")

        action = random.choice(possible_actions)
        return self.actions_dict[action]

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
        if self.go_up:
            if self.wall_map()[0, 1]:
                if not self.wall_map()[1, 0]:
                    self.go_up = False
                    return self.actions_dict["move_Left"]
                else:
                    self.go_up = True
                    self.yellow_deposit_not_available = False
                    return (
                        self.deliberate()
                    )  # go back to yellow deposit and start again
            else:
                return self.actions_dict["move_Up"]
        else:
            if self.wall_map()[2, 1]:
                if not self.wall_map()[1, 0]:
                    self.go_up = True
                    return self.actions_dict["move_Left"]
                else:
                    self.go_up = True
                    self.yellow_deposit_not_available = False
                    return (
                        self.deliberate()
                    )  # go back to yellow deposit and start again
            else:
                return self.actions_dict["move_Down"]

    def reachable_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == 1)
        return len(targets) > 0

    def find_nearest_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == 1)
        if len(targets) == 0:
            return None

        x, y = self.knowledge["position"]

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (targets[:, 1], targets[:, 0], distances)
        )  # en cas d'égalité des distances, le plus en haut à droite gagne

        return tuple(targets[sorted_indices[0]])

    def reach_waste(self):
        if self.is_on_correct_waste():
            return self.pick()

        possible_actions = []
        targetx, targety = self.find_nearest_waste()
        x, y = self.knowledge["position"]
        if targetx > x:
            possible_actions.append("move_Right")
        elif targetx < x:
            possible_actions.append("move_Left")
        if targety > y:
            possible_actions.append("move_Right")
        elif targety < y:
            possible_actions.append("move_Left")

        action = random.choice(possible_actions)
        return self.actions_dict[action]

    def deliberate(self):
        if self.begin:
            if not self.is_on_yellow_deposit():
                return self.go_to_init_position()
            else:
                self.begin = False

        if self.must_deliver():
            if self.yellow_deposit_not_available:
                if self.can_release() and not self.is_on_green_deposit():
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
