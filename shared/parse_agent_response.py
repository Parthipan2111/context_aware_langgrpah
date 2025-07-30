import json
import re

def parse_agent_response (final_output):
    """
    Parse the agent response
    """
    slot_parsed = {}
    agent_response = ""
     # Remove the triple backticks and optional json specifier
    fenced = re.sub(r"^```json|```$", "", final_output.strip(), flags=re.MULTILINE)
    fenced = fenced.strip().strip('`').strip()

    try:
        parsed = json.loads(fenced)
        slot_parsed = parsed.get("slots", {})
        agent_response = parsed.get("agent_response", [])
        print("Slots:", slot_parsed)
        print("Response:", agent_response)
    except json.JSONDecodeError:
    # If JSON decoding fails, fallback to using the raw output
        slot_parsed = {}
        agent_response = [final_output]
        print("Model did not return valid JSON:", final_output)
    return slot_parsed,agent_response