import gym
from gym import spaces
import numpy as np
from typing import Dict, Any, Tuple
from .world_state import DisasterSimulator
from .observation_space import ObservationManager
from .action_space import ActionSchema

class CrisisEnv(gym.Env):
    """Main OpenEnv environment for CrisisCoord."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super(CrisisEnv, self).__init__()
        self.config = config or {}
        self.max_steps = self.config.get("max_steps", 100)
        
        # Initialize components
        self.simulator = DisasterSimulator()
        self.obs_manager = ObservationManager(self.simulator.state)
        
        # Gym Spaces (Simplified for OpenEnv compatibility)
        self.action_space = spaces.Text(min_length=0, max_length=1000)
        self.observation_space = spaces.Dict({
            "summary": spaces.Text(min_length=0, max_length=5000),
            "step": spaces.Discrete(101)
        })

    def reset(self) -> Dict[str, Any]:
        """Resets the environment to initial state."""
        self.simulator = DisasterSimulator()
        self.obs_manager = ObservationManager(self.simulator.state)
        return self._get_obs()

    def step(self, action_str: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Executes one time step in the environment."""
        # 1. Parse and validate action
        action = ActionSchema.validate_action(action_str)
        
        # 2. Apply action to simulator
        if action["action_type"] == "SURVEY":
            self.obs_manager.reveal_location(action.get("location_id"))
        elif action["action_type"] != "INVALID":
            self.simulator.apply_action(action)
            
        # 3. Update world state (Natural decay/events)
        self.simulator.update()
        
        # 4. Get observation and reward
        obs = self._get_obs()
        reward = self._calculate_reward(action)
        done = self.simulator.state["current_step"] >= self.max_steps
        
        # Add basic casualty info to info dict for metric tracking
        total_casualties = sum(loc["casualty_count"] for loc in self.simulator.state["locations"].values())
        info = {"total_casualties": total_casualties, "action_valid": action["action_type"] != "INVALID"}
        
        return obs, reward, done, info

    def _get_obs(self) -> Dict[str, Any]:
        """Internal helper to get formatted observation."""
        return {
            "summary": self.obs_manager.get_state_summary(),
            "full_observation": self.obs_manager.get_observation(),
            "step": self.simulator.state["current_step"]
        }

    def _calculate_reward(self, action: Dict[str, Any]) -> float:
        """Calculates a simple reward (to be replaced by composable rubrics)."""
        # For now, reward is negative of total casualties
        total_casualties = sum(loc["casualty_count"] for loc in self.simulator.state["locations"].values())
        reward = -total_casualties / 100.0
        
        # Penalty for invalid actions
        if action["action_type"] == "INVALID":
            reward -= 5.0
            
        return reward

    def state(self) -> Dict[str, Any]:
        """Returns the full world state (privileged info)."""
        return self.simulator.state

    def close(self):
        """Cleanup."""
        pass
