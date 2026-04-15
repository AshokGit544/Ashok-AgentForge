def task_analyzer_tool(task: str) -> dict:
    task_lower = task.lower()

    has_research = "research" in task_lower or "summarize" in task_lower
    has_execution = "code" in task_lower or "build" in task_lower

    task_type = "general"
    difficulty = "medium"
    output_type = "text_report"

    if has_research and has_execution:
        task_type = "research_execution"
        output_type = "strategy_and_implementation_plan"
    elif has_research:
        task_type = "research"
        output_type = "structured_summary"
    elif has_execution:
        task_type = "execution"
        output_type = "implementation_plan"

    if len(task.split()) > 12:
        difficulty = "high"

    return {
        "task_type": task_type,
        "difficulty": difficulty,
        "output_type": output_type
    }