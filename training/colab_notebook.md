# CrisisCoord Training Notebook

This notebook demonstrates how to train a coordination agent for the CrisisCoord environment using Unsloth and HuggingFace TRL.

## 1. Install Dependencies
```python
!pip install gym numpy matplotlib openenv unsloth trl transformers accelerate
```

## 2. Clone Repository
```python
!git clone https://github.com/user/crisis-coord-env.git
%cd crisis-coord-env
```

## 3. Run Environment Baseline
```python
from environment.crisis_env import CrisisEnv
from baselines.greedy_agent import GreedyAgent

env = CrisisEnv()
obs = env.reset()
agent = GreedyAgent(env.simulator.state["teams"].keys())

for _ in range(50):
    action = agent.act(obs)
    obs, reward, done, info = env.step(action)
    if done: break

print(f"Final Total Casualties: {info['total_casualties']}")
```

## 4. Start Training
```python
!python training/train.py
```
