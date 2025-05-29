# agents.py
from mesa import Agent
import random

class EthnicAgent(Agent):
    def __init__(self, unique_id, model, ethnicity, grievance, violence_threshold):
        # Required Mesa attrs
        self.unique_id = unique_id
        self.model     = model
        self.pos       = None

        self.ethnicity          = ethnicity
        self.grievance          = grievance
        self.violence_threshold = violence_threshold
        self.aversion           = 0.1

    def step(self):
        self.interact()
        self.update_internal_state()
        self.move()

    def interact(self):
        # 1) Get neighboring cells and flatten to agents
        cell_list = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=self.model.vision
        )
        nbrs = []
        for cell in cell_list:
            nbrs.extend(self.model.grid.get_cell_list_contents(cell))

        # 2) Pick a random out‐group neighbor
        out = [a for a in nbrs if a.ethnicity != self.ethnicity]
        if not out:
            return
        partner = random.choice(out)

        # 3) Combined grievance drives violence probability
        sum_g = self.grievance + partner.grievance       # range [0,2]
        p_violence = min(sum_g / 2, 1.0)                # normalized to [0,1]

        # 4) Stochastic interaction
        if random.random() < p_violence:
            interaction = "violent"
            # both gain grievance by α
            self.grievance    = min(self.grievance    + self.model.alpha, 1)
            partner.grievance = min(partner.grievance + self.model.alpha, 1)
        else:
            interaction = "neutral"
            # both lose grievance by β
            self.grievance    = max(self.grievance    - self.model.beta, 0)
            partner.grievance = max(partner.grievance - self.model.beta, 0)

        # 5) Log it
        self.model.record_interaction(interaction, self.pos)
        # TODO: instead of log a cell (which will update too many times for each agent near that cell, 
        # and potentially cause the quadratic pattern in which neutral interactions push influence
        #      log the interaction per agent (memory)


    def update_internal_state(self):
        # decay grievance
        self.grievance *= self.model.decay
        
        # adjust majority thresholds by recent violence/neutral mix
        recent = self.model.get_recent_interactions(self.pos)
        if recent and self.ethnicity == "majority":
            v = recent.count("violent") / len(recent)
            n = recent.count("neutral") / len(recent)
             # harder to decrease if threshold is already low
            delta = -self.model.alpha * v * (self.violence_threshold) + self.model.beta * n * (1-self.violence_threshold)
           

            self.violence_threshold = min(max(self.violence_threshold + delta, 0), 1)

            
    def move(self):
        # 1) get empty neighbor cells
        nbrs = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=1
        )
        empty = [cell for cell in nbrs
                 if not self.model.grid.get_cell_list_contents(cell)]
        if not empty:
            return

        # 2) for each candidate (including staying put), compute "violence score" =
        #    number of violent interactions logged at that cell
        candidates = [self.pos] + empty
        def violence_score(cell):
            return sum(1 for i in self.model.interactions_log.get(cell, [])
                       if i == "violent")

        # 3) pick the cell with lowest violence_score
        best_cell = min(candidates, key=violence_score)

        # 4) with probability `aversion`, move to best_cell; otherwise stay or move randomly
        if best_cell != self.pos and random.random() < self.aversion:
            self.model.grid.move_agent(self, best_cell)
        elif empty:
            # fallback random move with probability (1 − aversion)
            
            self.model.grid.move_agent(self, random.choice([self.pos]+empty))

