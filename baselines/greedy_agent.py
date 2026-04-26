import json

class GreedyAgent:
    """Always allocates resources to the most visible casualty count."""
    
    def __init__(self, team_ids):
        self.team_ids = list(team_ids)

    def act(self, obs):
        locations = obs["full_observation"]["locations"]
        
        # Filter for surveyed locations with casualties
        surveyed_locs = [
            (loc_id, loc_data) for loc_id, loc_data in locations.items() 
            if loc_data.get("surveyed") and loc_data.get("casualty_count", 0) > 0
        ]
        
        if not surveyed_locs:
            # If nothing surveyed, survey a random one
            unsurveyed = [loc_id for loc_id, loc_data in locations.items() if not loc_data.get("surveyed")]
            if unsurveyed:
                return json.dumps({"action_type": "SURVEY", "location_id": unsurveyed[0]})
            return json.dumps({"action_type": "PRIORITIZE", "location_id": "L1", "priority_level": 1})

        # Pick location with max casualties
        target_loc_id, target_loc_data = max(surveyed_locs, key=lambda x: x[1]["casualty_count"])
        
        # Deploy a medical team if available
        for team_id in self.team_ids:
            if obs["full_observation"]["teams"][team_id]["status"] == "idle":
                return json.dumps({
                    "action_type": "DEPLOY",
                    "team_id": team_id,
                    "location_id": target_loc_id,
                    "task": "triage"
                })
        
        # Otherwise, allocate medical supplies
        return json.dumps({
            "action_type": "ALLOCATE",
            "resource_type": "medical_supplies",
            "location_id": target_loc_id,
            "quantity": 50
        })
