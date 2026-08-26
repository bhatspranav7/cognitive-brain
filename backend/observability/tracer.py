import json
from datetime import datetime

from backend import config


def trace_agent(agent_name, input_data, output_data, latency):
    trace = {
        "timestamp": str(datetime.now()),
        "agent": agent_name,
        "latency": round(latency, 4),
        "input": input_data,
        "output": output_data,
    }

    with open(config.TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace) + "\n")
