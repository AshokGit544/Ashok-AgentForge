from app.workflows.graph import build_graph
from app.memory.run_memory import save_run

app = build_graph()

result = app.invoke({
    "task": "Research and summarize the best way to build a realistic multi-agent AI project"
})

save_run(result)

print("Final Workflow Output:")
print(result)

print("\nExecution Trace:")
for step in result.get("execution_trace", []):
    print("-", step)

print("\nRun saved to memory file: data/run_memory.json")