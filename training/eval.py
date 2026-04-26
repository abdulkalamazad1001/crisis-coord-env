import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.crisis_env import CrisisEnv
from baselines.random_agent import RandomAgent
from baselines.greedy_agent import GreedyAgent
import json
import matplotlib.pyplot as plt
import numpy as np

def run_evaluation(num_episodes=5):
    env = CrisisEnv(config={"max_steps": 50})
    results = {"random": [], "greedy": [], "trained": []}
    
    location_ids = env.simulator.state["locations"].keys()
    team_ids = env.simulator.state["teams"].keys()
    
    for episode in range(num_episodes):
        # Random Agent
        obs = env.reset()
        agent = RandomAgent(location_ids, team_ids)
        total_reward = 0
        for _ in range(50):
            action = agent.act(obs)
            obs, reward, done, _ = env.step(action)
            total_reward += reward
        results["random"].append(total_reward)
        
        # Greedy Agent
        obs = env.reset()
        agent = GreedyAgent(team_ids)
        total_reward = 0
        for _ in range(50):
            action = agent.act(obs)
            obs, reward, done, _ = env.step(action)
            total_reward += reward
        results["greedy"].append(total_reward)
        
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(range(num_episodes), results["random"], label="Random Agent", marker='o')
    plt.plot(range(num_episodes), results["greedy"], label="Greedy Agent", marker='s')
    
    plt.title("Agent Performance Comparison")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.legend()
    plt.grid(True)
    
    # Ensure results directory exists
    os.makedirs("results/plots", exist_ok=True)
    plt.savefig("results/plots/reward_comparison.png")
    print("Evaluation plot saved to results/plots/reward_comparison.png")
    
    with open("results/metrics.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    run_evaluation()
