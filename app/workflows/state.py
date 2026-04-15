from typing import TypedDict, Optional, List


class AgentState(TypedDict, total=False):
    task: str
    task_type: Optional[str]
    difficulty: Optional[str]
    output_type: Optional[str]
    objective: Optional[str]
    subtasks: Optional[List[str]]
    success_criteria: Optional[str]
    research_notes: Optional[str]
    final_answer: Optional[str]
    review_notes: Optional[str]
    review_status: Optional[str]
    improved_answer: Optional[str]
    execution_trace: Optional[List[str]]