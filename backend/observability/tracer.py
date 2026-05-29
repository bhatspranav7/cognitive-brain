import json
import time
from datetime import datetime

TRACE_FILE = "agent_traces.jsonl"


def trace_agent(agent_name, input_data, output_data, latency):
    trace = {
        "timestamp": str(datetime.now()),
        "agent": agent_name,
        "latency": round(latency, 4),
        "input": input_data,
        "output": output_data
    }

    with open(TRACE_FILE, "a") as f:
        f.write(json.dumps(trace) + "\n")