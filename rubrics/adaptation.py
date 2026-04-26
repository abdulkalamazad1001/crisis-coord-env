from typing import Dict, Any

class AdaptationRubric:
    """Scores the agent's ability to respond to dynamic events."""
    
    def __init__(self, weight: float = 0.15):
        self.weight = weight

    def __call__(self, state: Dict[str, Any], action: Dict[str, Any], next_state: Dict[str, Any]) -> float:
        score = 0
        
        # Reward for SURVEYING when new events occur or in high-damage areas
        if action.get("action_type") == "SURVEY":
            loc_id = action.get("location_id")
            if next_state["locations"][loc_id]["infrastructure_damage"] > 0.4:
                score += 10
        
        # Penalty for persistent active events not being addressed (e.g., road_block)
        for event in next_state["active_events"]:
            if event == "road_block":
                # Check if search_rescue teams are working on it (simplified)
                sar_deployed = any(t["type"] == "search_rescue" and t["status"] == "deployed" 
                                 for t in next_state["teams"].values())
                if not sar_deployed:
                    score -= 5
                    
        return score * self.weight
