from mesa import Agent


class RobotAgent(Agent):
    def __init__(self, model, knowledge:dict): #TODO ask yourself how to create model
        super().__init__(model)
        self.knowledge = knowledge

    def deliberate(self):
        pass

    def update(self, percepts, action):
        if action == 0 and percepts["success"]:
            self.knowledge["carried"] = True
        elif action in [1,2,3] and percepts["success"]:
            self.knowledge["carried"] = False
        self.knowledge.update()


    def step(self):
        action = self.deliberate(self.knowledge)
        percepts = self.model.do(self, action)
        self.knowledge.update(percepts)


