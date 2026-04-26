import sys
import os
import copy
from typing import Dict, Any, Tuple

from .world_state import DisasterSimulator
from .observation_space import ObservationManager
from .action_space import ActionSchema

# OpenEnv base class — fall back to a plain base if openenv is not installed
try:
    from openenv import Environment as OpenEnvBase
except ImportError:
    class OpenEnvBase:
        """Minimal fallback so the environment still runs without openenv installed."""
        pass

# Load rubrics
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rubrics.lives_saved import LivesSavedRubric
from rubrics.fairness import FairnessRubric
from rubrics.resource_efficiency import ResourceEfficiencyRubric
from rubrics.adaptation import AdaptationRubric


class CrisisEnv(OpenEnvBase):
    """
    OpenEnv-compliant environment for CrisisCoord Disaster Response Coordination.
    Inherits from openenv.Environment (with a gym-compatible fallback).
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_steps = self.config.get("max_steps", 100)

        # Composable rubrics — loaded here and used in _calculate_reward
        self.rubrics = [
            LivesSavedRubric(weight=0.4),
            FairnessRubric(weight=0.2),
            ResourceEfficiencyRubric(weight=0.25),
            AdaptationRubric(weight=0.15),
        ]

        self._init_world()

    # ------------------------------------------------------------------
    # OpenEnv / Gym API
    # ------------------------------------------------------------------

    def reset(self) -> Dict[str, Any]:
        """Resets the environment to a fresh disaster scenario."""
        self._init_world()
        return self._get_obs()

    def step(self, action_str: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Executes one time step in the environment."""
        # Snapshot state BEFORE the action for rubric calculation
        state_before = copy.deepcopy(self.simulator.state)

        # 1. Parse and validate action
        action = ActionSchema.validate_action(action_str)

        # 2. Apply action to simulator
        if action["action_type"] == "SURVEY":
            self.obs_manager.reveal_location(action.get("location_id"))
        elif action["action_type"] != "INVALID":
            self.simulator.apply_action(action)

        # 3. Advance world (natural decay, events)
        self.simulator.update()

        # 4. Snapshot state AFTER for rubric calculation
        state_after = self.simulator.state

        # 5. Composable reward from all rubrics
        reward = self._calculate_reward(state_before, action, state_after)

        obs = self._get_obs()
        done = self.simulator.state["current_step"] >= self.max_steps

        total_casualties = sum(
            loc["casualty_count"] for loc in state_after["locations"].values()
        )
        info = {
            "total_casualties": total_casualties,
            "action_valid": action["action_type"] != "INVALID",
        }

        return obs, reward, done, info

    def state(self) -> Dict[str, Any]:
        """Returns the full world state (privileged info for rubrics/training)."""
        return self.simulator.state

    def close(self):
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_world(self):
        self.simulator = DisasterSimulator()
        self.obs_manager = ObservationManager(self.simulator.state)

    def _get_obs(self) -> Dict[str, Any]:
        return {
            "summary": self.obs_manager.get_state_summary(),
            "full_observation": self.obs_manager.get_observation(),
            "step": self.simulator.state["current_step"],
        }

    def _calculate_reward(
        self,
        state_before: Dict[str, Any],
        action: Dict[str, Any],
        state_after: Dict[str, Any],
    ) -> float:
        """
        Composable reward: sum of all rubric scores.
        Each rubric takes (state_before, action, state_after).
        """
        total = 0.0
        for rubric in self.rubrics:
            try:
                total += rubric(state_before, action, state_after)
            except Exception:
                pass  # Rubric failure must never crash the environment

        # Hard penalty for invalid actions
        if action["action_type"] == "INVALID":
            total -= 5.0

        return total
