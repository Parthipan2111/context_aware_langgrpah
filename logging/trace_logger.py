import requests

def trace_logger_node(state):
    if state["execution_trace"]:
        last_log = state["execution_trace"][-1]
        print(f"[TRACE LOG] {last_log}")
        try:
            requests.post("http://localhost:8000/ws-log", json={"log": last_log})
        except:
            pass
    return state
