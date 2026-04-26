import random
from typing import Dict, Any

class DisasterSimulator:
    """Core logic for simulating disaster progression."""
    
    def __init__(self, num_locations: int = 5):
        self.num_locations = num_locations
        self.state = self.initialize_world()

    def initialize_world(self) -> Dict[str, Any]:
        """Creates the initial state for a new disaster scenario."""
        locations = {}
        for i in range(self.num_locations):
            loc_id = f"L{i+1}"
            locations[loc_id] = {
                "name": f"District {i+1}",
                "population": random.randint(1000, 5000),
                "casualty_count": random.randint(50, 200),
                "infrastructure_damage": random.uniform(0.1, 0.5),
                "communication_status": "stable",
                "resources_allocated": {"medical_supplies": 0, "food_water": 0, "vehicles": 0},
                "active_teams": []
            }
            
        return {
            "locations": locations,
            "global_resources": {
                "medical_supplies": 1000,
                "food_water": 5000,
                "vehicles": 20,
                "hospital_beds": 100
            },
            "teams": {
                "med_1": {"type": "medical", "status": "idle", "location": "base"},
                "med_2": {"type": "medical", "status": "idle", "location": "base"},
                "sar_1": {"type": "search_rescue", "status": "idle", "location": "base"},
                "log_1": {"type": "logistics", "status": "idle", "location": "base"}
            },
            "current_step": 0,
            "active_events": []
        }

    def update(self):
        """Advances the simulation by one time step."""
        self.state["current_step"] += 1
        
        for loc_id, loc in self.state["locations"].items():
            # Casuality count increases if not enough medical supplies or teams
            medical_coverage = loc["resources_allocated"]["medical_supplies"]
            med_teams = len([t for t in loc["active_teams"] if self.state["teams"][t]["type"] == "medical"])
            
            if med_teams == 0 or medical_coverage < loc["casualty_count"]:
                # Natural decay/worsening
                loc["casualty_count"] += random.randint(1, 5)
            else:
                # Improvement
                loc["casualty_count"] = max(0, loc["casualty_count"] - random.randint(2, 8))
                loc["resources_allocated"]["medical_supplies"] -= 2 # Consumption
                
            # Infrastructure decay
            if "aftershock" in self.state["active_events"]:
                loc["infrastructure_damage"] = min(1.0, loc["infrastructure_damage"] + 0.05)
                
        # Random Event Generation
        if random.random() < 0.1:
            event = random.choice(["aftershock", "comms_failure", "road_block"])
            if event not in self.state["active_events"]:
                self.state["active_events"].append(event)
        elif random.random() < 0.2 and self.state["active_events"]:
            self.state["active_events"].pop(0) # Event cleared

    def apply_action(self, action: Dict[str, Any]):
        """Modifies the state based on agent action."""
        action_type = action.get("action_type")
        
        if action_type == "ALLOCATE":
            loc_id = action.get("location_id")
            res_type = action.get("resource_type")
            qty = action.get("quantity")
            
            if self.state["global_resources"].get(res_type, 0) >= qty:
                self.state["global_resources"][res_type] -= qty
                self.state["locations"][loc_id]["resources_allocated"][res_type] += qty
                
        elif action_type == "DEPLOY":
            team_id = action.get("team_id")
            loc_id = action.get("location_id")
            
            if team_id in self.state["teams"]:
                self.state["teams"][team_id]["status"] = "deployed"
                self.state["teams"][team_id]["location"] = loc_id
                if team_id not in self.state["locations"][loc_id]["active_teams"]:
                    self.state["locations"][loc_id]["active_teams"].append(team_id)
