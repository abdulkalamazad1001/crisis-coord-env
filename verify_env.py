import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())

from environment.crisis_env import CrisisEnv
from baselines.random_agent import RandomAgent
from baselines.greedy_agent import GreedyAgent
import json

def run_verification():
    env = CrisisEnv(config={"max_steps": 50})
    obs = env.reset()
    
    location_ids = env.simulator.state["locations"].keys()
    team_ids = env.simulator.state["teams"].keys()
    
    print("--- Verifying Random Agent ---")
    agent = RandomAgent(location_ids, team_ids)
    total_reward = 0
    for _ in range(50):
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        if done: break
    print(f"Random Agent Total Reward: {total_reward:.2f}")
    
    obs = env.reset()
    print("\n--- Verifying Greedy Agent ---")
    agent = GreedyAgent(team_ids)
    total_reward = 0
    for _ in range(50):
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        if done: break
    print(f"Greedy Agent Total Reward: {total_reward:.2f}")
    print(f"Final Casualties: {info['total_casualties']}")

if __name__ == "__main__":
    run_verification()
