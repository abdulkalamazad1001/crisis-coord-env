import sys
import os
import json
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from trl import GRPOConfig, GRPOTrainer
from environment.crisis_env import CrisisEnv
from environment.action_space import ActionSchema
from rubrics.lives_saved import LivesSavedRubric
from rubrics.fairness import FairnessRubric
from rubrics.resource_efficiency import ResourceEfficiencyRubric
from rubrics.adaptation import AdaptationRubric

# ── Disaster scenario prompts ──────────────────────────────────────────────────
SCENARIO_PROMPTS = [
    (
        "You are an emergency operations commander. A major earthquake has struck. "
        "District L1 has 80 casualties and is surveyed. Districts L2-L5 are unknown. "
        "You have 4 teams and 1000 medical supplies. "
        "Output a single JSON action: SURVEY, DEPLOY, ALLOCATE, or PRIORITIZE."
    ),
    (
        "You are an emergency operations commander. A flood is active. "
        "District L3 has 150 casualties and critical infrastructure damage. "
        "Districts L1, L2, L4, L5 are unsurveyed. You have med_1 idle at base. "
        "Output a single JSON action to maximise lives saved."
    ),
    (
        "You are an emergency operations commander. Step 10 of a pandemic response. "
        "All districts are surveyed. L2 and L4 have the highest casualties. "
        "You have 200 medical supplies left. sar_1 and log_1 are idle. "
        "Output a single JSON action to prioritise the most critical area."
    ),
    (
        "You are an emergency operations commander. An aftershock just hit. "
        "L5 infrastructure damage is now 0.9. No teams are deployed to L5. "
        "You have med_2 idle. Output a JSON action to respond to the aftershock."
    ),
]

TRAIN_DATASET = [{"prompt": p} for p in SCENARIO_PROMPTS]


# ── Real reward function ───────────────────────────────────────────────────────
rubrics = [
    LivesSavedRubric(weight=0.4),
    FairnessRubric(weight=0.2),
    ResourceEfficiencyRubric(weight=0.25),
    AdaptationRubric(weight=0.15),
]


def reward_fn(prompts, completions, **kwargs):
    """
    Executes each LLM completion in a fresh CrisisEnv instance and scores it
    using all 4 composable rubrics.
    """
    rewards = []

    for prompt, completion in zip(prompts, completions):
        try:
            env = CrisisEnv()
            obs = env.reset()

            # Snapshot state BEFORE
            state_before = copy.deepcopy(env.state())

            # Parse the action the LLM generated
            action = ActionSchema.validate_action(completion)

            # Execute in the environment
            next_obs, env_reward, done, info = env.step(completion)

            # Snapshot state AFTER
            state_after = env.state()

            # Score using all rubrics
            total = 0.0
            for rubric in rubrics:
                try:
                    total += rubric(state_before, action, state_after)
                except Exception:
                    pass

            # Hard penalty for invalid / unparsable actions
            if action["action_type"] == "INVALID":
                total -= 5.0

            rewards.append(float(total))

        except Exception as e:
            # Never crash the training loop; give a negative reward for failures
            rewards.append(-10.0)

    return rewards


# ── Training ──────────────────────────────────────────────────────────────────
def train():
    model_id = "Qwen/Qwen2.5-0.5B-Instruct"  # Small & fast; swap to 7B for full run

    training_args = GRPOConfig(
        output_dir="./results",
        learning_rate=5e-6,
        num_train_epochs=1,
        per_device_train_batch_size=4,
        num_generations=4,
    )

    trainer = GRPOTrainer(
        model=model_id,
        reward_funcs=[reward_fn],
        args=training_args,
        train_dataset=TRAIN_DATASET,
    )

    print("Starting GRPO training on CrisisCoord environment...")
    trainer.train()
    print("Training complete. Results saved to ./results/")


if __name__ == "__main__":
    train()
