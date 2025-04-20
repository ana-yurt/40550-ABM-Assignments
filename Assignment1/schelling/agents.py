from mesa import Agent

class SchellingAgent(Agent):
    ## Initiate agent instance, inherit model trait from parent class
    def __init__(self, model, agent_type, lower_threshold, upper_threshold):
        super().__init__(model)
        ## Set agent type
        self.type = agent_type
        ## Set personal tolerance threshold
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    ## Define basic decision rule
    def move(self):
        ## Get list of neighbors within range of sight
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore = True, radius = self.model.radius, include_center = False)
        ## Count neighbors of same type as self
        similar_neighbors = len([n for n in neighbors if n.type == self.type])
        ## If an agent has any neighbors (to avoid division by zero), calculate share of neighbors of same type
        if (valid_neighbors := len(neighbors)) > 0:
            share_alike = similar_neighbors / valid_neighbors
        else:
            share_alike = 0
        
        
        # Decision Rule: agent is satisfied only if share_alike within [lower, upper]
        if self.lower_threshold <= share_alike <= self.upper_threshold:
            self.model.happy += 1
            return

        # Agent is unhappy: attempt to move
        empties = list(self.model.grid.empties)
        if not empties:
            return
        # Try a random empty spot
        new_pos = self.random.choice(empties)
        new_neighbors = self.model.grid.get_neighbors(
            new_pos, moore=True, radius=self.model.radius, include_center=False
        )
        same_new = len([n for n in new_neighbors if n.type == self.type])
        total_new = len(new_neighbors)
        new_share = same_new / total_new if total_new > 0 else 0

        # Apply Decision Rule: move only if new_share within tolerance range
        if self.lower_threshold <= new_share <= self.upper_threshold:
            self.model.grid.move_agent(self, new_pos)
 
