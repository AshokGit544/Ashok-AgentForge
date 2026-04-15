from app.tools.task_analyzer import task_analyzer_tool


def planner_node(state):
    task = state["task"]
    analysis = task_analyzer_tool(task)
    trace = state.get("execution_trace", [])

    return {
        "task_type": analysis["task_type"],
        "difficulty": analysis["difficulty"],
        "output_type": analysis["output_type"],
        "objective": f"Complete the task: {task}",
        "subtasks": [
            "Understand the task clearly",
            "Break the task into smaller steps",
            "Collect useful research points",
            "Prepare a final response"
        ],
        "success_criteria": (
            f"The final answer should be clear, structured, and suitable for output type "
            f"'{analysis['output_type']}'."
        ),
        "execution_trace": trace + ["planner_node completed"]
    }


def researcher_node(state):
    task = state["task"]
    task_type = state["task_type"]
    difficulty = state["difficulty"]
    output_type = state["output_type"]
    objective = state["objective"]
    subtasks = state["subtasks"]
    success_criteria = state["success_criteria"]
    trace = state.get("execution_trace", [])

    research_notes = f"""
- Task: {task}
- Task Type: {task_type}
- Difficulty: {difficulty}
- Output Type: {output_type}
- Objective: {objective}
- Subtasks:
  - {subtasks[0]}
  - {subtasks[1]}
  - {subtasks[2]}
  - {subtasks[3]}
- Success Criteria: {success_criteria}
- A structured workflow makes agent systems easier to understand and maintain.
- Shared state helps each node build on previous work.
""".strip()

    return {
        "research_notes": research_notes,
        "execution_trace": trace + ["researcher_node completed"]
    }


def writer_node(state):
    task = state["task"]
    task_type = state["task_type"]
    difficulty = state["difficulty"]
    output_type = state["output_type"]
    objective = state["objective"]
    subtasks = state["subtasks"]
    success_criteria = state["success_criteria"]
    research_notes = state["research_notes"]
    trace = state.get("execution_trace", [])

    final_answer = f"""
Final Response

Task:
{task}

Task Type:
{task_type}

Difficulty:
{difficulty}

Output Type:
{output_type}

Objective:
{objective}

Subtasks:
- {subtasks[0]}
- {subtasks[1]}
- {subtasks[2]}
- {subtasks[3]}

Success Criteria:
{success_criteria}

Research Notes:
{research_notes}

Conclusion:
This task was processed through a structured planner -> researcher -> writer workflow with tool-assisted task analysis.
""".strip()

    return {
        "final_answer": final_answer,
        "execution_trace": trace + ["writer_node completed"]
    }


def reviewer_node(state):
    trace = state.get("execution_trace", [])

    try:
        task = state.get("task", "")
        final_answer = state.get("final_answer", "")
        success_criteria = state.get("success_criteria", "")
        task_type = state.get("task_type", "")
        difficulty = state.get("difficulty", "")

        checks_passed = []
        checks_failed = []

        # 1. Blocked: task missing completely
        if not task.strip():
            review_status = "blocked"

            review_notes = """
Review Summary:
- Review Status: blocked
- Reason:
  - Task input is empty, so the workflow cannot proceed safely.
""".strip()

            return {
                "review_notes": review_notes,
                "review_status": review_status,
                "execution_trace": trace + [f"reviewer_node completed with status: {review_status}"]
            }

        # 2. Rejected: task extremely vague
        if len(task.strip().split()) < 2:
            review_status = "rejected"

            review_notes = f"""
Review Summary:
- Review Status: rejected
- Reason:
  - Task is too vague or too short to produce a reliable result.
- Task Received:
  - {task}
""".strip()

            return {
                "review_notes": review_notes,
                "review_status": review_status,
                "execution_trace": trace + [f"reviewer_node completed with status: {review_status}"]
            }

        # 3. Normal validation checks
        if len(task.strip().split()) >= 3:
            checks_passed.append("Task is specific enough")
        else:
            checks_failed.append("Task is somewhat vague and needs improvement")

        if "Task Type:" in final_answer:
            checks_passed.append("Task Type section found")
        else:
            checks_failed.append("Task Type section missing")

        if "Success Criteria:" in final_answer:
            checks_passed.append("Success Criteria section found")
        else:
            checks_failed.append("Success Criteria section missing")

        if "Conclusion:" in final_answer:
            checks_passed.append("Conclusion section found")
        else:
            checks_failed.append("Conclusion section missing")

        if len(final_answer.strip()) >= 50:
            checks_passed.append("Final answer length is acceptable")
        else:
            checks_failed.append("Final answer is too short")

        # 4. Decide status
        if len(checks_failed) >= 3:
            review_status = "rejected"
        elif len(checks_failed) > 0:
            review_status = "needs_improvement"
        elif task_type == "research_execution" and difficulty == "high":
            review_status = "pending_review"
        else:
            review_status = "approved"

        passed_text = "\n  - ".join(checks_passed) if checks_passed else "None"
        failed_text = "\n  - ".join(checks_failed) if checks_failed else "None"

        review_notes = f"""
Review Summary:
- Review Status: {review_status}
- Checks Passed:
  - {passed_text}
- Checks Failed:
  - {failed_text}
- Success Criteria Used:
{success_criteria}
""".strip()

        return {
            "review_notes": review_notes,
            "review_status": review_status,
            "execution_trace": trace + [f"reviewer_node completed with status: {review_status}"]
        }

    except Exception as e:
        review_status = "error"

        review_notes = f"""
Review Summary:
- Review Status: error
- Reason:
  - Reviewer failed with exception: {str(e)}
""".strip()

        return {
            "review_notes": review_notes,
            "review_status": review_status,
            "execution_trace": trace + [f"reviewer_node completed with status: {review_status}"]
        }


def review_router(state):
    status = state["review_status"]

    if status == "needs_improvement":
        return "improver"

    return "end"


def improver_node(state):
    final_answer = state.get("final_answer", "")
    review_notes = state.get("review_notes", "")
    trace = state.get("execution_trace", [])

    improved_answer = f"""
Improved Response

Original Final Answer:
{final_answer}

Improvement Notes Applied:
{review_notes}

Improved Version:
Task Type: updated if needed
Success Criteria: reinforced
Conclusion: ensured

Improved Conclusion:
The answer was reviewed and revised based on reviewer feedback.
""".strip()

    return {
        "improved_answer": improved_answer,
        "execution_trace": trace + ["improver_node completed"]
    }