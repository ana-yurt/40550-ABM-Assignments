from mesa import Model
from mesa.space import SingleGrid
from agents import SchellingAgent
from mesa.datacollection import DataCollector

class SchellingModel(Model):
    ## Define initiation, requiring all needed parameter inputs
    def __init__(self, width = 50, height = 50, density = 0.7,
        group_one_share=0.7,
        tolerance_mean=0.5,
        tolerance_std=0.1,
        tolerance_upper=0.9,
        radius=1,
        seed=None,
    ):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.density = density
        self.group_one_share = group_one_share
        self.radius = radius

        # new parameters
        self.tolerance_mean = tolerance_mean
        self.tolerance_std = tolerance_std
        self.tolerance_upper = tolerance_upper
        self.grid = SingleGrid(width, height, torus = True)
        self.happy = 0
        ## Define data collector, to collect happy agents and share of agents currently happy
        self.datacollector = DataCollector(
            model_reporters = {
                "happy" : "happy",
                "share_happy" : lambda m : (m.happy / len(m.agents)) * 100
                if len(m.agents) > 0
                else 0
            }
        )
        ## Place agents randomly around the grid, randomly assigning them to agent types.
        for cont, pos in self.grid.coord_iter():
            if self.random.random() < self.density:
                agent_type = 1 if self.random.random() < self.group_one_share else 0
                # CHANGE: draw each agent’s tolerance from a uniform distribution
                tolerance = self.random.gauss(self.tolerance_mean, self.tolerance_std)
                if tolerance < 0.01:
                    tolerance = 0.01
                elif tolerance > 0.99:
                    tolerance = 0.99
                if self.tolerance_upper > tolerance:
                    upper = self.tolerance_upper
                else:
                    upper = 1
                a = SchellingAgent(
                    model=self,
                    agent_type=agent_type,
                    lower_threshold=tolerance,
                    upper_threshold=upper,
                )
                self.grid.place_agent(a, pos)

        ## Initialize datacollector
        self.datacollector.collect(self)

    def step(self):
        self.happy = 0
        self.agents.shuffle_do("move")
        self.datacollector.collect(self)
        ## Run model until all agents are happy
        self.running = self.happy < len(self.agents)
