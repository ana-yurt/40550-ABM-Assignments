# model.py
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import EthnicAgent
from collections import deque
import os

class EthnicViolenceModel(Model):

    def __init__(self, width=60, height=60, majority_pct=0.7, density=0.6,
                 alpha=0.2, beta=0.05, decay=0.8, vision=2, aversion=0.1):
        super().__init__()
        self.width        = width
        self.height       = height
        self.majority_pct = majority_pct
        self.density      = density
        self.alpha        = alpha
        self.beta         = beta
        self.decay        = decay
        self.vision       = vision
        self.aversion     = aversion

        self.grid             = MultiGrid(width, height, torus=False)
        self.interactions_log = {}
        self.max_cell_memory = 10 
        self.schedule_time    = 0

        # initialize agents with random grievance & threshold
        total = width * height
        n    = int(density * total)
        pos  = [(x, y) for x in range(width) for y in range(height)]
        self.random.shuffle(pos)
        chosen = pos[:n]

        self.agent_list = []

        for uid, p in enumerate(chosen):
            eth   = "majority" if self.random.random() < majority_pct else "minority"
            g0    = self.random.random() * 0.2 # grievance in [0, 0.2]
            t0    = self.random.random() * 0.8 + 0.2 # threshold in [0.2, 1.0]
            agent = EthnicAgent(uid, self, eth, g0, t0, aversion=self.aversion)
            self.grid.place_agent(agent, p)
            self.agent_list.append(agent)

        self.datacollector = DataCollector(model_reporters={
            "Avg_Maj_Grievance":   lambda m: sum(a.grievance    for a in m.agent_list if a.ethnicity=="majority")
                                      / max(1, sum(1 for a in m.agent_list if a.ethnicity=="majority")),
            "Avg_Min_Grievance":   lambda m: sum(a.grievance    for a in m.agent_list if a.ethnicity=="minority")
                                      / max(1, sum(1 for a in m.agent_list if a.ethnicity=="minority")),
            "Avg_Maj_Threshold":   lambda m: sum(a.violence_threshold for a in m.agent_list if a.ethnicity=="majority")
                                      / max(1, sum(1 for a in m.agent_list if a.ethnicity=="majority")),
            "Overall_Hosility_Level": lambda m: (
                                        sum(i == "hostile" for logs in m.interactions_log.values() for i in logs) /
                                        max(1, sum(len(logs) for logs in m.interactions_log.values()))
                                    )
        })

    def step(self):
        self.datacollector.collect(self)
        self.random.shuffle(self.agent_list)
        for a in self.agent_list:
            a.step()
        self.schedule_time += 1

    def record_interaction(self, interaction, pos):
        if pos not in self.interactions_log:
            self.interactions_log[pos] = deque(maxlen=self.max_cell_memory)
        self.interactions_log[pos].append(interaction)
