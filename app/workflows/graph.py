from langgraph.graph import StateGraph, END
from app.workflows.state import AgentState
from app.workflows.nodes import (
    planner_node,
    researcher_node,
    writer_node,
    reviewer_node,
    review_router,
    improver_node
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("improver", improver_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")

    graph.add_conditional_edges(
        "reviewer",
        review_router,
        {
            "end": END,
            "improver": "improver"
        }
    )

    graph.add_edge("improver", END)

    return graph.compile()