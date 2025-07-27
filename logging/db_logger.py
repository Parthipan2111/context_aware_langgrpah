def db_logger_node(state):
    try:
        log_record = {
            "user_input": state["user_input"],
            "intent": state["intent"],
            "trace": state["execution_trace"]
        }
        print(f"📥 [DB LOG] {log_record}")
    except Exception as e:
        print(f"DB logging failed: {e}")
    return state
