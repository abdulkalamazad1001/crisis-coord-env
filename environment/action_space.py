import json
from typing import Dict, Any

class ActionSchema:
    """Defines the structured JSON action space for CrisisCoord."""
    
    SCHEMAS = {
        "ALLOCATE": {
            "type": "object",
            "properties": {
                "resource_type": {"type": "string", "enum": ["medical_supplies", "food_water", "vehicles"]},
                "location_id": {"type": "string"},
                "quantity": {"type": "integer", "minimum": 1}
            },
            "required": ["resource_type", "location_id", "quantity"]
        },
        "DEPLOY": {
            "type": "object",
            "properties": {
                "team_id": {"type": "string"},
                "location_id": {"type": "string"},
                "task": {"type": "string", "enum": ["triage", "search_rescue", "repair", "logistics"]}
            },
            "required": ["team_id", "location_id", "task"]
        },
        "SURVEY": {
            "type": "object",
            "properties": {
                "location_id": {"type": "string"}
            },
            "required": ["location_id"]
        },
        "PRIORITIZE": {
            "type": "object",
            "properties": {
                "location_id": {"type": "string"},
                "priority_level": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["location_id", "priority_level"]
        }
    }

    @staticmethod
    def validate_action(action_str: str) -> Dict[str, Any]:
        """Parses and validates an action string from the LLM."""
        try:
            # Extract JSON if it's wrapped in markers or text
            if "```json" in action_str:
                action_str = action_str.split("```json")[1].split("```")[0]
            elif "{" in action_str:
                action_str = action_str[action_str.find("{"):action_str.rfind("}")+1]
            
            action = json.loads(action_str)
            action_type = action.get("action_type")
            
            if action_type not in ActionSchema.SCHEMAS:
                raise ValueError(f"Unknown action type: {action_type}")
            
            # Simple validation (can be extended with jsonschema library if available)
            schema = ActionSchema.SCHEMAS[action_type]
            for req in schema["required"]:
                if req not in action:
                    raise ValueError(f"Missing required field: {req} for {action_type}")
            
            return action
        except Exception as e:
            return {"action_type": "INVALID", "error": str(e)}

    @staticmethod
    def get_prompt_instructions() -> str:
        """Returns the formatting instructions for the LLM."""
        return """
        Your actions must be valid JSON objects. Use the following formats:
        
        1. Allocate Resources:
        {"action_type": "ALLOCATE", "resource_type": "medical_supplies", "location_id": "A1", "quantity": 10}
        
        2. Deploy Team:
        {"action_type": "DEPLOY", "team_id": "medical_team_1", "location_id": "B2", "task": "triage"}
        
        3. Survey Location (Reveals hidden casualties/damage):
        {"action_type": "SURVEY", "location_id": "C3"}
        
        4. Prioritize:
        {"action_type": "PRIORITIZE", "location_id": "D4", "priority_level": 5}
        """
