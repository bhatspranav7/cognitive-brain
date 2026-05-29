import json
from collections import defaultdict

TRACE_FILE = "agent_traces.jsonl"

latencies = defaultdict(list)
counts = defaultdict(int)

with open(TRACE_FILE, "r") as f:
    for line in f:
        trace = json.loads(line)

        agent = trace["agent"]
        latency = trace["latency"]

        counts[agent] += 1
        latencies[agent].append(latency)

print("\n=== AGENT METRICS ===\n")

for agent in counts:
    avg_latency = sum(latencies[agent]) / len(latencies[agent])

    print(f"Agent: {agent}")
    print(f"Executions: {counts[agent]}")
    print(f"Average Latency: {avg_latency:.4f} sec")
    print()