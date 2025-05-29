# model.py
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import EthnicAgent
from collections import defaultdict, deque


# helper function 
def overall_violence_level(model):
    interactions = [i for sublist in model.interactions_log.values() for i in sublist]
    return 0 if len(interactions) == 0 else sum(1 for i in interactions if i == "violent") / len(interactions)
def overall_interactions(model):
    interactions = [i for sublist in model.interactions_log.values() for i in sublist]
    return len(interactions) / 5

class EthnicViolenceModel(Model):
    def __init__(
        self,
        width=100,height=100, majority_pct=0.7, density=0.7,
        alpha=0.1,
        beta=0.1,
        decay=0.9,
        vision=2,
    ):
        super().__init__()
        self.width        = width
        self.height       = height
        self.majority_pct = majority_pct
        self.density      = density
        self.alpha        = alpha
        self.beta         = beta
        self.decay        = decay
        self.vision       = vision

        self.grid           = MultiGrid(width, height, torus=False)
        self.interactions_log = defaultdict(lambda: deque(maxlen=5))
        self.schedule_time    = 0

        # place exactly density*width*height agents, one per cell
        total_cells   = width * height
        n_agents      = int(self.density * total_cells)
        all_positions = [(x, y) for x in range(width) for y in range(height)]
        self.random.shuffle(all_positions)
        chosen_positions = all_positions[:n_agents]

        self.agent_list = []
        for uid, pos in enumerate(chosen_positions):
            ethnicity = "majority" if self.random.random() < self.majority_pct else "minority"
            # random but bounded: grievance in [0,0.5], threshold in [0.2,1.0]
            grievance = self.random.random() * 0.5
            violence_threshold = self.random.random() * 0.8 + 0.2
            agent = EthnicAgent(uid, self, ethnicity, grievance=grievance, violence_threshold=violence_threshold)
            self.grid.place_agent(agent, pos)
            self.agent_list.append(agent)


        self.datacollector = DataCollector(model_reporters={
            "Avg_Maj_Grievance": lambda m: sum(a.grievance for a in m.agent_list if a.ethnicity=="majority")/
                                          max(1, sum(1 for a in m.agent_list if a.ethnicity=="majority")),
            "Avg_Min_Grievance": lambda m: sum(a.grievance for a in m.agent_list if a.ethnicity=="minority")/
                                          max(1, sum(1 for a in m.agent_list if a.ethnicity=="minority")),
            "Avg_Maj_Threshold": lambda m: sum(a.violence_threshold for a in m.agent_list if a.ethnicity=="majority")/
                                           max(1, sum(1 for a in m.agent_list if a.ethnicity=="majority")),
            "Overall_Violence_Level": lambda m: (
                                        sum(i == "violent" for logs in m.interactions_log.values() for i in logs) /
                                        max(1, sum(len(logs) for logs in m.interactions_log.values()))
                                    ),

            "Overall_Interactions": overall_interactions,
        })
    def step(self):
        self.datacollector.collect(self)
        self.random.shuffle(self.agent_list)
        for a in self.agent_list:
            a.step()
  
        self.schedule_time += 1

    def record_interaction(self, interaction, pos):
        # this will auto-create a deque(maxlen=5) on first use
        self.interactions_log[pos].append(interaction)

    def get_recent_interactions(self, pos, radius=None):
        if radius is None:
            radius = self.vision
        cells = self.grid.get_neighborhood(pos, moore=True, include_center=True, radius=radius)
        recent = []
        for cell in cells:
            recent.extend(self.interactions_log[cell])  # each is already capped at length 5
        return recent
    