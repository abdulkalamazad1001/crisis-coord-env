import random
import json
from environment.action_space import ActionSchema

class RandomAgent:
    """Selects valid actions uniformly at random."""
    
    def __init__(self, location_ids, team_ids):
        self.location_ids = list(location_ids)
        self.team_ids = list(team_ids)
        self.action_types = ["ALLOCATE", "DEPLOY", "SURVEY", "PRIORITIZE"]

    def act(self, obs):
        action_type = random.choice(self.action_types)
        loc_id = random.choice(self.location_ids)
        
        if action_type == "ALLOCATE":
            return json.dumps({
                "action_type": "ALLOCATE",
                "resource_type": random.choice(["medical_supplies", "food_water", "vehicles"]),
                "location_id": loc_id,
                "quantity": random.randint(1, 20)
            })
        elif action_type == "DEPLOY":
            return json.dumps({
                "action_type": "DEPLOY",
                "team_id": random.choice(self.team_ids),
                "location_id": loc_id,
                "task": random.choice(["triage", "search_rescue", "repair", "logistics"])
            })
        elif action_type == "SURVEY":
            return json.dumps({
                "action_type": "SURVEY",
                "location_id": loc_id
            })
        else: # PRIORITIZE
            return json.dumps({
                "action_type": "PRIORITIZE",
                "location_id": loc_id,
                "priority_level": random.randint(1, 5)
            })
