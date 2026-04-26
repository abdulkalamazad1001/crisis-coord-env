from typing import Dict, Any
import numpy as np

class FairnessRubric:
    """Anti-gaming: Penalizes ignoring remote or high-damage locations."""
    
    def __init__(self, weight: float = 0.2):
        self.weight = weight

    def __call__(self, state: Dict[str, Any], action: Dict[str, Any], next_state: Dict[str, Any]) -> float:
        # Calculate variance in resource allocation/coverage across locations
        coverages = []
        for loc_id, loc in next_state["locations"].items():
            # Coverage = (Medical Supplies + Teams) / (Casualties + 1)
            med_teams = len([t for t in loc["active_teams"] if next_state["teams"][t]["type"] == "medical"])
            coverage = (loc["resources_allocated"]["medical_supplies"] + med_teams * 10) / (loc["casualty_count"] + 1)
            coverages.append(coverage)
        
        # High variance means some areas are being ignored -> Penalty
        variance = np.var(coverages)
        penalty = -variance * 5
        
        # Also check for locations with high damage but zero resources
        neglected_penalty = 0
        for loc_id, loc in next_state["locations"].items():
            if loc["infrastructure_damage"] > 0.5 and len(loc["active_teams"]) == 0:
                neglected_penalty -= 10
                
        return (penalty + neglected_penalty) * self.weight
