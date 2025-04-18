import random
from mailbox.Mailbox import Mailbox
from scipy.spatial.distance import cdist

import numpy as np
from mesa import Agent

from message.Message import Message
from message.MessagePerformative import MessagePerformative
from message.MessageService import MessageService

EMPTY = -1
WALL = -1
UNEXPLORED = -2


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
        self.grid_size = self.model.grid_size
        self.color_to_gather = -1

        self.green_threshold = 1 / 3
        self.yellow_threshold = 2 / 3
        self.red_threshold = 1

        self.__mailbox = Mailbox()
        self.__messages_service = MessageService.get_instance()

    def get_pos(self):
        i, j = self.pos
        return (
            j + 1,
            i + 1,
        )

    def deliberate(self):
        pass

    def update(self, percepts, action, other_grids=None):
        self.knowledge["carried_by_others"] = {0: {}, 1: {}, 2: {}}
        if other_grids is not None:
            for subgrid, (i, j), carried, color in other_grids:
                for k in range(3):
                    for l in range(3):
                        if subgrid[k][l] != -2:
                            self.knowledge["grid"][self.grid_size - i + k][
                                j - 1 + l
                            ] = subgrid[k][l]

                self.knowledge["carried_by_others"][color][(i, j)] = carried

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

        i, j = self.get_pos()
        self.knowledge["grid"][
            self.grid_size - i : self.grid_size - i + 3, j - 1 : j + 2
        ] = percepts["color_waste"]

        self.knowledge.update(percepts)

    def step(self):
        action = self.deliberate()
        percepts = self.model.do(self, action)
        other_grids = self.read_messages()
        self.update(percepts, action, other_grids)
        self.broadcast_message()

    def read_messages(self):
        all_grids = []
        list_messages = self.get_new_messages()
        for message in list_messages:
            content = message.get_content()
            all_grids.append(content)
        return all_grids

    def broadcast_message(self):
        # Broadcast to all agents
        for agent_id in self.knowledge["id"]:
            if agent_id != self.get_id():
                i, j = self.get_pos()
                sub_grid = self.knowledge["grid"][
                    self.grid_size - i : self.grid_size - i + 3, j - 1 : j + 2
                ]

                self.send_message(
                    Message(
                        self.get_id(),
                        agent_id,
                        MessagePerformative.QUERY_REF,
                        (
                            sub_grid,
                            (i, j),
                            self.knowledge["carried"],
                            self.color_to_gather,
                        ),
                    )
                )

    def get_id(self):
        return self.unique_id

    def receive_message(self, message):
        """Receive a message (called by the MessageService object) and store it in the mailbox."""
        self.__mailbox.receive_messages(message)

    def send_message(self, message):
        """Send message through the MessageService object."""
        self.__messages_service.send_message(message)

    def get_new_messages(self):
        """Return all the unread messages."""
        return self.__mailbox.get_new_messages()

    def get_messages(self):
        """Return all the received messages."""
        return self.__mailbox.get_messages()

    def get_messages_from_performative(self, performative):
        """Return a list of messages which have the same performative."""
        return self.__mailbox.get_messages_from_performative(performative)

    def get_messages_from_exp(self, exp):
        """Return a list of messages which have the same sender."""
        return self.__mailbox.get_messages_from_exp(exp)


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
        self.color_to_gather = 0  # Can only gather green wastes
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

    def explore(self):
        nearest_unexplored = self.find_nearest_unexplored()
        if isinstance(nearest_unexplored, tuple):
            return self.reach_location(*nearest_unexplored)
        else:
            return self.random_walk()

    def find_nearest_unexplored(self):
        targets = np.argwhere(self.knowledge["grid"] == UNEXPLORED)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
                if (position[1] <= self.green_deposit_position[1]).any()
            ]
        )  # do not look for green waste in green deposit

        if len(targets) == 0:
            return None

        x, y = self.get_pos()

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (targets[:, 1], -targets[:, 0], distances)
        )  # en cas d'égalité des distances, le plus en haut à gauche gagne
        return tuple(targets[sorted_indices[0]])

    def wall_map(self):
        return self.knowledge["radioactivity"] == WALL

    def is_on_yellow_deposit(self):
        return self.get_pos() == self.find_nearest_yellow_deposit()

    def is_on_green_deposit(self):
        return (
            (self.wall_map()[0, :]).all()
            and (self.knowledge["radioactivity"][1:, 2] > self.green_threshold).all()
            and (self.knowledge["radioactivity"][1:, :2] <= self.green_threshold).all()
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
        if not self.wall_map()[0, 1] and not self.knowledge["other_robots"][0, 1] == 1:
            possible_actions.append("move_Up")

        if (
            self.knowledge["radioactivity"][1, 2] <= self.green_threshold
            and not self.knowledge["other_robots"][1, 2] == 1
        ):
            possible_actions.append("move_Right")

        if len(possible_actions) > 0:
            action = random.choice(possible_actions)
            return self.actions_dict[action]
        else:
            return self.random_walk()

    def go_to_init_position(self):
        if (
            self.knowledge["radioactivity"][1, 2] <= self.green_threshold
            and not self.knowledge["other_robots"][1, 2] == 1
        ):
            action = "move_Right"

        elif not self.knowledge["other_robots"][2, 1] == 1:
            action = "move_Down"

        else:
            return self.random_walk()
        return self.actions_dict[action]

    def find_nearest_yellow_deposit(self):
        targets = np.argwhere(self.knowledge["grid"] == EMPTY)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
                if (
                    (position[1] <= self.yellow_deposit_position[1]).any()
                    and position[0] not in [0, len(self.knowledge["grid"]) - 1]
                    and (position != self.green_deposit_position).any()
                )
            ]
        )  # do not look for green waste in green deposit
        if len(targets) == 0:
            return None

        x, y = self.get_pos()

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (distances, -targets[:, 1])
        )  # en cas d'égalité des positions en x, le plus proche gagne
        return tuple(targets[sorted_indices[0]])

    def go_to_yellow_deposit(self):
        targetx, targety = self.find_nearest_yellow_deposit()
        return self.reach_location(targetx, targety)

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
            return self.deliberate()

    def reachable_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == self.color_to_gather)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
                if (position != self.green_deposit_position).any()
            ]
        )  # do not look for green waste in green deposit

        if len(targets) == 0:
            return None

        prio1 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if self.knowledge["carried_by_others"][self.color_to_gather][pos]
            == [self.color_to_gather]
        ]

        prio2 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if len(self.knowledge["carried_by_others"][self.color_to_gather][pos]) == 0
        ]

        x, y = self.get_pos()
        if self.knowledge["carried"] == [self.color_to_gather]:
            prio1.append((x, y))

        elif len(self.knowledge["carried"]) == 0:
            prio2.append((x, y))

        attributions, targets = self.attribution(prio1, targets)
        attributions, targets = self.attribution(prio2, targets, attributions)
        return (x, y) in attributions

    def attribution(self, positions, targets, attributions={}):
        positions = np.array(positions)
        targets = np.array(targets)
        while len(positions) > 0 and len(targets) > 0:
            mat = cdist(positions, targets)
            min_id = np.argmin(mat)
            i, j = np.unravel_index(min_id, mat.shape)
            attributions[tuple(positions[i])] = tuple(targets[j])
            positions = np.array(np.delete(positions, i, axis=0))
            targets = np.array(np.delete(targets, j, axis=0))

        return attributions, targets

    def find_nearest_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == self.color_to_gather)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
                if (position != self.green_deposit_position).any()
            ]
        )  # do not look for green waste in green deposit

        if len(targets) == 0:
            return None

        prio1 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if self.knowledge["carried_by_others"][self.color_to_gather][pos]
            == [self.color_to_gather]
        ]

        prio2 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if len(self.knowledge["carried_by_others"][self.color_to_gather][pos]) == 0
        ]

        x, y = self.get_pos()
        if self.knowledge["carried"] == [self.color_to_gather]:
            prio1.append((x, y))

        elif len(self.knowledge["carried"]) == 0:
            prio2.append((x, y))

        attributions, targets = self.attribution(prio1, targets)
        attributions, targets = self.attribution(prio2, targets, attributions)
        if (x, y) in attributions:
            return tuple(attributions[(x, y)])
        else:
            return None

    def reach_location(self, targetx, targety):
        possible_actions = []
        x, y = self.get_pos()
        if (
            targetx > x
            and not self.knowledge["other_robots"][0, 1] == 1
            and not self.wall_map()[0, 1]
        ):
            possible_actions.append("move_Up")
        elif (
            targetx < x
            and not self.knowledge["other_robots"][2, 1] == 1
            and not self.wall_map()[2, 1]
        ):
            possible_actions.append("move_Down")
        if (
            targety > y
            and not self.knowledge["other_robots"][1, 2] == 1
            and not self.wall_map()[1, 2]
        ):
            possible_actions.append("move_Right")
        elif (
            targety < y
            and not self.knowledge["other_robots"][1, 0] == 1
            and not self.wall_map()[1, 0]
        ):
            possible_actions.append("move_Left")

        if len(possible_actions) > 0:
            action = random.choice(possible_actions)
            return self.actions_dict[action]
        else:
            return self.random_walk()

    def reach_waste(self):
        if self.is_on_correct_waste():
            return self.pick()

        targetx, targety = self.find_nearest_waste()
        return self.reach_location(targetx, targety)

    def deliberate(self):
        if self.begin:
            self.green_deposit_position = [
                1,
                (len(self.knowledge["grid"]) - 2)
                - 2 * (len(self.knowledge["grid"]) - 2) // 3,
            ]

            self.yellow_deposit_position = [
                len(self.knowledge["grid"]) - 2,
                (len(self.knowledge["grid"]) - 2)
                - 2 * (len(self.knowledge["grid"]) - 2) // 3,
            ]
            self.red_deposit_position = [
                len(self.knowledge["grid"]) - 2,
                (len(self.knowledge["grid"]) - 2)
                - (len(self.knowledge["grid"]) - 2) // 3,
            ]
            self.begin = False

        if self.must_deliver():
            if self.is_on_yellow_deposit():
                return self.act_in_yellow_deposit()

            else:
                return self.go_to_yellow_deposit()

        if self.reachable_waste():
            return self.reach_waste()

        if self.has_one_correct_waste():
            if self.is_on_green_deposit():
                if self.can_release():
                    return self.release()
                elif self.is_on_correct_waste():
                    return self.pick()
            else:
                return self.go_to_green_deposit()

        return self.explore()


class YellowAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.color_to_gather = 1  # Can only gather yellow wastes
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

    def explore(self):
        nearest_unexplored = self.find_nearest_unexplored()
        if isinstance(nearest_unexplored, tuple):
            return self.reach_location(*nearest_unexplored)
        else:
            return self.random_walk()

    def find_nearest_unexplored(self):
        targets = np.argwhere(self.knowledge["grid"] == UNEXPLORED)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
                if (position[1] <= self.red_deposit_position[1]).any()
            ]
        )  # do not look for green waste in green deposit
        if len(targets) == 0:
            return None

        x, y = self.get_pos()

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (targets[:, 1], -targets[:, 0], distances)
        )  # en cas d'égalité des distances, le plus en haut à gauche gagne
        return tuple(targets[sorted_indices[0]])

    def wall_map(self):
        return self.knowledge["radioactivity"] == WALL

    def is_on_yellow_deposit(self):
        return (
            (self.wall_map()[2, :]).all()
            and (self.knowledge["radioactivity"][:2, 2] > self.green_threshold).all()
            and (self.knowledge["radioactivity"][:, :2] <= self.green_threshold).all()
        )

    def is_on_red_deposit(self):
        return self.find_nearest_deposit() == self.get_pos()

    def is_on_green_deposit(self):
        return (
            (self.wall_map()[0, :]).all()
            and (self.knowledge["radioactivity"][1:, 2] > self.green_threshold).all()
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

    def go_to_init_position(self):
        if not self.wall_map()[0, 1]:
            if (
                self.knowledge["radioactivity"][1, 1] <= self.green_threshold
                and not self.knowledge["other_robots"][1, 2] == 1
            ):
                action = "move_Right"
            elif (
                self.knowledge["radioactivity"][1, 0] > self.green_threshold
                and not self.knowledge["other_robots"][1, 0] == 1
            ):
                action = "move_Left"
            elif not self.knowledge["other_robots"][0, 1] == 1:
                action = "move_Up"
            else:
                return self.random_walk()
        elif not self.knowledge["other_robots"][1, 0] == 1:
            action = "move_Left"
        else:
            action = "nothing"

        return self.actions_dict[action]

    def go_to_yellow_deposit(self):
        if not self.wall_map()[2, 1] and not self.knowledge["other_robots"][2, 1] == 1:
            action = "move_Down"

        elif (
            self.knowledge["radioactivity"][1, 2] <= self.green_threshold
            and not self.knowledge["other_robots"][1, 2] == 1
        ):
            action = "move_Right"

        elif (
            self.knowledge["radioactivity"][1, 1] > self.green_threshold
            and not self.knowledge["other_robots"][1, 0] == 1
        ):
            action = "move_Left"

        else:
            return self.random_walk()

        return self.actions_dict[action]

    def find_nearest_deposit(self):
        targets = np.argwhere(self.knowledge["grid"] == EMPTY)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
                if (
                    (position[1] <= self.red_deposit_position[1]).any()
                    and position[0] not in [0, len(self.knowledge["grid"]) - 1]
                )
            ]
        )  # do not look for green waste in green deposit
        if len(targets) == 0:
            return None

        x, y = self.get_pos()

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (distances, -targets[:, 1])
        )  # en cas d'égalité des positions en x, le plus proche gagne
        return tuple(targets[sorted_indices[0]])

    def go_to_red_deposit(self):
        targetx, targety = self.find_nearest_deposit()
        return self.reach_location(targetx, targety)

    def can_release(self):
        return self.knowledge["color_waste"][1, 1] == EMPTY

    def release(self):
        return self.actions_dict[
            "release_" + self.colors_ids[self.knowledge["carried"][0]]
        ]

    def pick(self):
        return self.actions_dict["pick"]

    def act_in_red_deposit(self):
        if self.can_release():
            return self.release()

    def find_place_to_deliver(self):
        if self.go_up:
            if self.wall_map()[0, 1]:
                if not self.wall_map()[1, 0]:
                    self.go_up = False
                    return self.actions_dict["move_Left"]
                else:
                    self.go_up = True
                    self.red_deposit_not_available = False
                    return self.deliberate()  # go back to red deposit and start again
            else:
                return self.actions_dict["move_Up"]
        else:
            if self.wall_map()[2, 1]:
                if not self.wall_map()[1, 0]:
                    self.go_up = True
                    return self.actions_dict["move_Left"]
                else:
                    self.go_up = True
                    self.red_deposit_not_available = False
                    return self.deliberate()  # go back to red deposit and start again
            else:
                return self.actions_dict["move_Down"]

    def reachable_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == self.color_to_gather)
        targets = [
            [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
            for position in targets
            if (position != self.yellow_deposit_position).any()
        ]

        if len(targets) == 0:
            return None

        prio1 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if self.knowledge["carried_by_others"][self.color_to_gather][pos]
            == [self.color_to_gather]
        ]

        prio2 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if len(self.knowledge["carried_by_others"][self.color_to_gather][pos]) == 0
        ]

        x, y = self.get_pos()
        if self.knowledge["carried"] == [self.color_to_gather]:
            prio1.append((x, y))

        elif len(self.knowledge["carried"]) == 0:
            prio2.append((x, y))

        attributions, targets = self.attribution(prio1, targets)
        attributions, targets = self.attribution(prio2, targets, attributions)
        return (x, y) in attributions

    def attribution(self, positions, targets, attributions={}):
        positions = np.array(positions)
        targets = np.array(targets)
        while len(positions) > 0 and len(targets) > 0:
            mat = cdist(positions, targets)
            min_id = np.argmin(mat)
            i, j = np.unravel_index(min_id, mat.shape)
            attributions[tuple(positions[i])] = tuple(targets[j])
            positions = np.array(np.delete(positions, i, axis=0))
            targets = np.array(np.delete(targets, j, axis=0))

        return attributions, targets

    def find_nearest_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == self.color_to_gather)
        targets = [
            [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
            for position in targets
            if (position != self.yellow_deposit_position).any()
        ]

        if len(targets) == 0:
            return None

        prio1 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if self.knowledge["carried_by_others"][self.color_to_gather][pos]
            == [self.color_to_gather]
        ]

        prio2 = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if len(self.knowledge["carried_by_others"][self.color_to_gather][pos]) == 0
        ]

        x, y = self.get_pos()
        if self.knowledge["carried"] == [self.color_to_gather]:
            prio1.append((x, y))

        elif len(self.knowledge["carried"]) == 0:
            prio2.append((x, y))

        attributions, targets = self.attribution(prio1, targets)
        attributions, targets = self.attribution(prio2, targets, attributions)
        if (x, y) in attributions:
            return tuple(attributions[(x, y)])
        else:
            return None

    def reach_location(self, targetx, targety):
        possible_actions = []
        x, y = self.get_pos()
        if (
            targetx > x
            and not self.knowledge["other_robots"][0, 1] == 1
            and not self.wall_map()[0, 1]
        ):
            possible_actions.append("move_Up")
        elif (
            targetx < x
            and not self.knowledge["other_robots"][2, 1] == 1
            and not self.wall_map()[2, 1]
        ):
            possible_actions.append("move_Down")
        if (
            targety > y
            and not self.knowledge["other_robots"][1, 2] == 1
            and not self.wall_map()[1, 2]
        ):
            possible_actions.append("move_Right")
        elif (
            targety < y
            and not self.knowledge["other_robots"][1, 0] == 1
            and not self.wall_map()[1, 0]
        ):
            possible_actions.append("move_Left")

        if len(possible_actions) > 0:
            action = random.choice(possible_actions)
            return self.actions_dict[action]
        else:
            return self.random_walk()

    def reach_waste(self):
        if self.is_on_correct_waste():
            return self.pick()

        targetx, targety = self.find_nearest_waste()
        return self.reach_location(targetx, targety)

    def deliberate(self):
        if self.begin:
            self.green_deposit_position = [
                1,
                (len(self.knowledge["grid"]) - 2)
                - 2 * (len(self.knowledge["grid"]) - 2) // 3,
            ]

            self.yellow_deposit_position = [
                len(self.knowledge["grid"]) - 2,
                (len(self.knowledge["grid"]) - 2)
                - 2 * (len(self.knowledge["grid"]) - 2) // 3,
            ]
            self.red_deposit_position = [
                len(self.knowledge["grid"]) - 2,
                (len(self.knowledge["grid"]) - 2)
                - (len(self.knowledge["grid"]) - 2) // 3,
            ]
            self.begin = False

        if self.must_deliver():
            if self.red_deposit_not_available:
                if (
                    self.can_release()
                    and not self.is_on_green_deposit()
                    and not self.is_on_yellow_deposit()
                ):
                    return self.release()

                else:
                    return self.find_place_to_deliver()

            elif self.is_on_red_deposit():
                return self.act_in_red_deposit()

            else:
                return self.go_to_red_deposit()

        self.red_deposit_not_available = False

        if self.reachable_waste():
            return self.reach_waste()

        if self.has_one_correct_waste():
            if self.is_on_yellow_deposit():
                if self.can_release():
                    return self.release()
                elif self.is_on_correct_waste():
                    return self.pick()
            else:
                return self.go_to_yellow_deposit()

        return self.explore()


class RedAgent(RobotAgent):
    def __init__(self, model, knowledge):
        super().__init__(model, knowledge)
        self.color_to_gather = 2  # Can only gather red wastes
        self.random_walk_counter = (
            0  # Every 15 random_walk steps, the agent goes to the red waste deposit
        )
        self.going_to_deposit = False

    def random_walk(self):
        possible_actions = []

        if (
            self.knowledge["radioactivity"][1, 2] <= self.red_threshold
            and not self.wall_map()[1, 2]
        ):
            possible_actions.append("move_Right")

        if (
            self.knowledge["radioactivity"][0, 1] <= self.red_threshold
            and not self.wall_map()[0, 1]
        ):
            possible_actions.append("move_Up")

        if (
            self.knowledge["radioactivity"][1, 0] <= self.red_threshold
            and not self.wall_map()[1, 0]
        ):
            possible_actions.append("move_Left")

        if (
            self.knowledge["radioactivity"][2, 1] <= self.red_threshold
            and not self.wall_map()[2, 1]
        ):
            possible_actions.append("move_Down")

        action = random.choice(possible_actions)
        self.random_walk_counter += 1
        if self.random_walk_counter == 2 * self.grid_size:
            self.going_to_deposit = True
        return self.actions_dict[action]

    def explore(self):
        nearest_unexplored = self.find_nearest_unexplored()
        if isinstance(nearest_unexplored, tuple):
            return self.reach_location(*nearest_unexplored)
        else:
            return self.random_walk()

    def find_nearest_unexplored(self):
        targets = np.argwhere(self.knowledge["grid"] == UNEXPLORED)
        targets = np.array(
            [
                [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
                for position in targets
            ]
        )  # do not look for green waste in green deposit

        if len(targets) == 0:
            return None

        x, y = self.get_pos()

        distances = np.abs(targets[:, 0] - x) + np.abs(targets[:, 1] - y)
        sorted_indices = np.lexsort(
            (-targets[:, 1], -targets[:, 0], distances)
        )  # en cas d'égalité des distances, le plus en haut à droite gagne
        return tuple(targets[sorted_indices[0]])

    def wall_map(self):
        return self.knowledge["radioactivity"] == WALL

    def is_on_red_deposit(self):
        return (
            (self.wall_map()[2, :]).all()
            and (self.knowledge["radioactivity"][:2, 2] > self.yellow_threshold).all()
            and (self.knowledge["radioactivity"][:, :2] <= self.yellow_threshold).all()
        )

    def is_on_waste_disposal(self):
        return self.knowledge["is_waste_disposal"][1, 1]

    def is_on_correct_waste(self):
        return self.knowledge["color_waste"][1, 1] == self.color_to_gather

    def must_deliver(self):
        return len(self.knowledge["carried"]) > 0

    def go_to_waste_disposal(self):
        possible_actions = []
        if (
            self.get_pos()[1] < len(self.knowledge["grid"]) - 3
            and not self.knowledge["other_robots"][1, 2] == 1
        ):
            possible_actions.append("move_Right")

        if (
            self.get_pos()[0] < len(self.knowledge["grid"]) // 2
            and not self.knowledge["other_robots"][0, 1] == 1
        ):
            possible_actions.append("move_Up")

        elif not self.knowledge["other_robots"][2, 1] == 1:
            possible_actions.append("move_Down")

        if len(possible_actions) == 0:
            return self.random_walk()

        action = random.choice(possible_actions)
        return self.actions_dict[action]

    def go_to_red_deposit(self):
        action = ""

        if not self.wall_map()[2, 1] and not self.knowledge["other_robots"][2, 1] == 1:
            action = "move_Down"

        elif (
            self.knowledge["radioactivity"][1, 2] <= self.yellow_threshold
            and not self.wall_map()[1, 2]
            and not self.knowledge["other_robots"][1, 2] == 1
        ):
            action = "move_Right"

        elif (
            self.knowledge["radioactivity"][1, 1] > self.yellow_threshold
            and not self.knowledge["other_robots"][1, 0] == 1
        ):
            action = "move_Left"

        if len(action) > 0:
            return self.actions_dict[action]
        else:
            return self.random_walk()

    def release(self):
        return self.actions_dict[
            "release_" + self.colors_ids[self.knowledge["carried"][0]]
        ]

    def pick(self):
        return self.actions_dict["pick"]

    def reachable_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == self.color_to_gather)
        targets = [
            [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
            for position in targets
        ]

        if len(targets) == 0:
            return None

        prio = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if len(self.knowledge["carried_by_others"][self.color_to_gather][pos]) == 0
        ]

        x, y = self.get_pos()

        if len(self.knowledge["carried"]) == 0:
            prio.append((x, y))

        attributions, targets = self.attribution(prio, targets)
        return (x, y) in attributions

    def attribution(self, positions, targets, attributions={}):
        positions = np.array(positions)
        targets = np.array(targets)
        while len(positions) > 0 and len(targets) > 0:
            mat = cdist(positions, targets)
            min_id = np.argmin(mat)
            i, j = np.unravel_index(min_id, mat.shape)
            attributions[tuple(positions[i])] = tuple(targets[j])
            positions = np.array(np.delete(positions, i, axis=0))
            targets = np.array(np.delete(targets, j, axis=0))

        return attributions, targets

    def find_nearest_waste(self):
        targets = np.argwhere(self.knowledge["grid"] == self.color_to_gather)
        targets = [
            [len(self.knowledge["grid"]) - position[0] - 1, position[1]]
            for position in targets
        ]

        if len(targets) == 0:
            return None

        prio = [
            pos
            for pos in self.knowledge["carried_by_others"][self.color_to_gather]
            if len(self.knowledge["carried_by_others"][self.color_to_gather][pos]) == 0
        ]

        x, y = self.get_pos()

        if len(self.knowledge["carried"]) == 0:
            prio.append((x, y))

        attributions, targets = self.attribution(prio, targets)
        if (x, y) in attributions:
            return tuple(attributions[(x, y)])
        else:
            return None

    def reach_location(self, targetx, targety):
        possible_actions = []
        x, y = self.get_pos()
        if (
            targetx > x
            and not self.knowledge["other_robots"][0, 1] == 1
            and not self.wall_map()[0, 1]
        ):
            possible_actions.append("move_Up")
        elif (
            targetx < x
            and not self.knowledge["other_robots"][2, 1] == 1
            and not self.wall_map()[2, 1]
        ):
            possible_actions.append("move_Down")
        if (
            targety > y
            and not self.knowledge["other_robots"][1, 2] == 1
            and not self.wall_map()[1, 2]
        ):
            possible_actions.append("move_Right")
        elif (
            targety < y
            and not self.knowledge["other_robots"][1, 0] == 1
            and not self.wall_map()[1, 0]
        ):
            possible_actions.append("move_Left")

        if len(possible_actions) > 0:
            action = random.choice(possible_actions)
            return self.actions_dict[action]
        else:
            return self.random_walk()

    def reach_waste(self):
        if self.is_on_correct_waste():
            return self.pick()

        targetx, targety = self.find_nearest_waste()
        return self.reach_location(targetx, targety)

    def deliberate(self):
        if self.must_deliver():
            if self.is_on_waste_disposal():
                return self.release()

            else:
                return self.go_to_waste_disposal()

        if self.reachable_waste():
            self.random_walk_counter = 0
            return self.reach_waste()

        if self.going_to_deposit:
            if self.is_on_red_deposit():
                self.going_to_deposit = False
                self.random_walk_counter = 0

            else:
                return self.go_to_red_deposit()
        return self.explore()
