
# def router_node(state):
#     user_input = state['user_input']
    
#     intent = detect_intent(user_input)  # can be LLM or rule-based
    
#     # Attach intent to state
#     state["intent"] = intent
#     next_steps = []

#     if intent == "get_credit_advice":
#         next_steps = ["credit_score_agent", "user_profile_agent"]
#     elif intent == "check_balance":
#         next_steps = ["account_agent"]
#     elif intent == "block_card":
#         next_steps = ["card_agent"]
#     else:
#         next_steps = ["fallback_agent"]
    
#     state["next_agents"] = next_steps
#     return state
