from typing import Dict, Any

class LivesSavedRubric:
    """Calculates reward based on lives saved and penalty for casualties."""
    
    def __init__(self, weight: float = 0.4):
        self.weight = weight

    def __call__(self, state: Dict[str, Any], action: Dict[str, Any], next_state: Dict[str, Any]) -> float:
        total_casualties_before = sum(loc["casualty_count"] for loc in state["locations"].values())
        total_casualties_after = sum(loc["casualty_count"] for loc in next_state["locations"].values())
        
        lives_saved = total_casualties_before - total_casualties_after
        
        # Reward for saving lives, penalty for remaining casualties
        reward = (lives_saved * 10) - (total_casualties_after * 0.1)
        
        return reward * self.weight
