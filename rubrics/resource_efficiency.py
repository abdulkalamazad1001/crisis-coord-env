from typing import Dict, Any

class ResourceEfficiencyRubric:
    """Measures how well resources are allocated and waste minimized."""
    
    def __init__(self, weight: float = 0.25):
        self.weight = weight

    def __call__(self, state: Dict[str, Any], action: Dict[str, Any], next_state: Dict[str, Any]) -> float:
        # Penalty for over-allocating resources beyond population needs
        waste_penalty = 0
        for loc_id, loc in next_state["locations"].items():
            excess = loc["resources_allocated"]["medical_supplies"] - (loc["population"] * 0.1)
            if excess > 0:
                waste_penalty -= (excess * 0.05)
                
        # Bonus for efficient delivery (using logistics teams)
        logistics_bonus = 0
        if action.get("action_type") == "DEPLOY":
            team_id = action.get("team_id")
            if next_state["teams"].get(team_id, {}).get("type") == "logistics":
                logistics_bonus += 5
                
        return (waste_penalty + logistics_bonus) * self.weight
