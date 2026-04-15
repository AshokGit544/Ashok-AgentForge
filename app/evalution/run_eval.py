import pandas as pd
from pathlib import Path
from app.workflows.graph import build_graph


def run_evaluation():
    app = build_graph()

    test_tasks = [
        "Research and summarize the best way to build a realistic multi-agent AI project",
        "Build a simple implementation plan for a task management app",
        "Summarize how a planner researcher writer workflow works"
    ]

    results = []

    for task in test_tasks:
        result = app.invoke({"task": task})

        results.append({
            "task": task,
            "task_type": result.get("task_type"),
            "difficulty": result.get("difficulty"),
            "output_type": result.get("output_type"),
            "review_status": result.get("review_status"),
            "trace_steps": len(result.get("execution_trace", []))
        })

    df = pd.DataFrame(results)
    return df


def save_evaluation(df: pd.DataFrame):
    output_file = Path("outputs/eval_results.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"Evaluation results saved to: {output_file}")


if __name__ == "__main__":
    df = run_evaluation()
    print("Evaluation Results:")
    print(df.to_string(index=False))
    save_evaluation(df)