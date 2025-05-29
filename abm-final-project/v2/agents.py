# agents.py
from mesa import Agent
from collections import deque
import random


class EthnicAgent(Agent):
    def __init__(self, unique_id, model, ethnicity, grievance, violence_threshold, aversion=0.1):
        # Mesa‐required fields
        self.unique_id = unique_id
        self.model     = model
        self.pos       = None

        # Agent state
        self.ethnicity          = ethnicity
        self.grievance          = grievance
        self.violence_threshold = violence_threshold
        self.aversion           = aversion

        # Personal memory of last 5 interactions
        self.memory = deque(maxlen=5)

    def step(self):
        self.interact()
        self.update_internal_state()
        self.move()

    def interact(self):
        # 1) get neighbors
        cells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=self.model.vision
        )
        nbrs = [a for cell in cells for a in self.model.grid.get_cell_list_contents(cell)]
        out = [a for a in nbrs if a.ethnicity != self.ethnicity]
        if not out:
            return
        partner = random.choice(out)

        # 2) determine outcome
        sum_g      = self.grievance + partner.grievance
        p_violence = min(sum_g / 2, 1.0)
        if random.random() < p_violence:
            interaction = "violent"
            self.grievance    = min(self.grievance    + self.model.alpha, 1)
            partner.grievance = min(partner.grievance + self.model.alpha, 1)
        else:
            interaction = "neutral"
            self.grievance    = max(self.grievance    - self.model.beta, 0)
            partner.grievance = max(partner.grievance - self.model.beta, 0)

        # 3) record BOTH in model log (for cell) and in each agent’s personal memory
        self.model.record_interaction(interaction, self.pos)
        self.memory.append(interaction)
        partner.memory.append(interaction)

    def update_internal_state(self):
        # decay grievance
        self.grievance *= self.model.decay

        # majority updates threshold from personal memory
        if self.ethnicity == "majority" and self.memory:
            v = self.memory.count("violent") / len(self.memory)
            n = self.memory.count("neutral") / len(self.memory)
            delta = -self.model.alpha * v * self.violence_threshold \
                    + self.model.beta  * n * (1 - self.violence_threshold)
            self.violence_threshold = min(max(self.violence_threshold + delta, 0), 1)

    def move(self):
        cells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=1
        )
        empty = [cell for cell in cells if not self.model.grid.get_cell_list_contents(cell)]
        if not empty:
            return

        # score each candidate by cell‐level violence log
        candidates = [self.pos] + empty
        def violence_score(cell):
            return sum(1 for i in self.model.interactions_log.get(cell, []) if i == "violent")
        best = min(candidates, key=violence_score)

        # move toward most peaceful with prob aversion, else random
        if best != self.pos and random.random() < self.aversion:
            self.model.grid.move_agent(self, best)
        elif random.random() < (1 - self.aversion):
            self.model.grid.move_agent(self, random.choice(empty))
