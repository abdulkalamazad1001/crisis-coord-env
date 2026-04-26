import gradio as gr
import sys
import os

# Add project root to path
# __file__ is CrisisCoordEnv/spaces/crisis-coord/app.py
# dirname(__file__) is CrisisCoordEnv/spaces/crisis-coord
# dirname(dirname(__file__)) is CrisisCoordEnv/spaces
# dirname(dirname(dirname(__file__))) is CrisisCoordEnv
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from environment.crisis_env import CrisisEnv
import json

# Global environment instance for the session
env = CrisisEnv()

def run_step(action_str):
    global env
    obs, reward, done, info = env.step(action_str)
    
    # Format the observation for better display
    display_obs = f"Step: {obs['step']}\n\n"
    display_obs += "=== COMMANDER'S SUMMARY ===\n"
    display_obs += obs['summary']
    
    if done:
        display_obs += "\n\nEPISODE COMPLETE"
        env = CrisisEnv() # Reset for next run
        
    return display_obs, f"Last Reward: {reward:.2f}", json.dumps(info, indent=2)

def reset_env():
    global env
    env = CrisisEnv()
    obs = env.reset()
    display_obs = f"Step: {obs['step']}\n\n"
    display_obs += "=== COMMANDER'S SUMMARY ===\n"
    display_obs += obs['summary']
    return display_obs, "Reward: 0.00", "{}"

with gr.Blocks(title="CrisisCoord Command Center") as demo:
    gr.Markdown("# 🚑 CrisisCoord Command Center")
    gr.Markdown("Coordinate disaster response across multiple districts. Use JSON actions to allocate resources and deploy teams.")
    
    with gr.Row():
        with gr.Column():
            action_input = gr.Textbox(
                label="Action (JSON)", 
                placeholder='{"action_type": "SURVEY", "location_id": "L1"}',
                lines=5,
                value='{"action_type": "SURVEY", "location_id": "L1"}'
            )
            with gr.Row():
                run_btn = gr.Button("Execute Action", variant="primary")
                reset_btn = gr.Button("Reset Scenario")
            
        with gr.Column():
            obs_output = gr.Textbox(label="Current Observation", lines=15)
            with gr.Row():
                reward_output = gr.Label(label="Reward Signal")
                metric_output = gr.Code(label="Step Metrics", language="json")

    run_btn.click(
        run_step, 
        inputs=[action_input], 
        outputs=[obs_output, reward_output, metric_output]
    )
    
    reset_btn.click(
        reset_env,
        outputs=[obs_output, reward_output, metric_output]
    )

if __name__ == "__main__":
    demo.launch()
