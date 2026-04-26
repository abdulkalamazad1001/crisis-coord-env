from typing import Dict, Any, List

class ObservationManager:
    """Manages partial observability and the discovery process."""
    
    def __init__(self, world_state: Dict[str, Any]):
        self.world_state = world_state
        self.discovered_locations: List[str] = []
        # Key info that is hidden until surveyed
        self.hidden_fields = ["casualty_count", "infrastructure_damage", "secondary_hazards"]

    def reveal_location(self, location_id: str):
        """Adds a location to the discovered list."""
        if location_id not in self.discovered_locations:
            self.discovered_locations.append(location_id)

    def get_observation(self) -> Dict[str, Any]:
        """Filters the world state to return only discovered or non-hidden information."""
        obs = {
            "locations": {},
            "resources": self.world_state.get("global_resources", {}),
            "teams": self.world_state.get("teams", {}),
            "step": self.world_state.get("current_step", 0),
            "events": self.world_state.get("active_events", [])
        }
        
        for loc_id, loc_data in self.world_state.get("locations", {}).items():
            loc_obs = {
                "name": loc_data.get("name"),
                "population": loc_data.get("population"),
                "communication_status": loc_data.get("communication_status")
            }
            
            # Only reveal hidden fields if location has been surveyed
            if loc_id in self.discovered_locations:
                for field in self.hidden_fields:
                    loc_obs[field] = loc_data.get(field)
                loc_obs["surveyed"] = True
            else:
                for field in self.hidden_fields:
                    loc_obs[field] = "UNKNOWN (Requires SURVEY)"
                loc_obs["surveyed"] = False
                
            obs["locations"][loc_id] = loc_obs
            
        return obs

    def get_state_summary(self) -> str:
        """Generates a compressed text summary for the LLM context window."""
        obs = self.get_observation()
        summary = [f"Step {obs['step']} Simulation State:"]
        
        for loc_id, loc in obs["locations"].items():
            status = "SURVEYED" if loc["surveyed"] else "UNSURVEYED"
            summary.append(f"- Location {loc_id} ({loc['name']}): Population {loc['population']}, Status: {status}")
            if loc["surveyed"]:
                summary.append(f"  Casualties: {loc['casualty_count']}, Damage: {loc['infrastructure_damage']}")
        
        active_events = obs.get("events", [])
        if active_events:
            summary.append(f"ALERT: Active Events: {', '.join(active_events)}")
            
        return "\n".join(summary)
