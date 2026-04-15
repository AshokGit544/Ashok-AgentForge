import streamlit as st
import pandas as pd
import altair as alt
import json
from pathlib import Path
from app.workflows.graph import build_graph
from app.memory.run_memory import save_run, load_recent_memory

st.set_page_config(
    page_title="Ashok-AgentForge",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_app():
    return build_graph()


@st.cache_data
def get_recent_memory_data():
    return load_recent_memory(limit=15)


@st.cache_data
def get_eval_data():
    eval_file = Path("outputs/eval_results.csv")
    if eval_file.exists():
        return pd.read_csv(eval_file)
    return None


def clear_cached_data():
    get_recent_memory_data.clear()
    get_eval_data.clear()


def build_fixed_bar_chart(df, category_col, title):
    if df.empty or category_col not in df.columns:
        return None

    counts = (
        df[category_col]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )
    counts.columns = [category_col, "count"]

    max_count = int(counts["count"].max()) if not counts.empty else 0
    upper_limit = max(10, ((max_count + 1) // 2 + 1) * 2)
    tick_values = list(range(0, upper_limit + 1, 2))

    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{category_col}:N",
                sort="-y",
                title=category_col.replace("_", " ").title()
            ),
            y=alt.Y(
                "count:Q",
                title="Count",
                scale=alt.Scale(domain=[0, upper_limit], nice=False, zero=True),
                axis=alt.Axis(values=tick_values)
            )
        )
        .properties(
            title=title,
            width=420,
            height=320
        )
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True)
    )

    return chart


def render_run_details(run, section_title):
    st.markdown(f"### {section_title}")
    st.write(f"**Run ID:** {run.get('run_id', 'N/A')}")
    st.write(f"**Timestamp:** {run.get('timestamp', 'N/A')}")
    st.write(f"**Task:** {run.get('task', 'N/A')}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Task Analysis")
        st.write(f"**Task Type:** {run.get('task_type', 'N/A')}")
        st.write(f"**Difficulty:** {run.get('difficulty', 'N/A')}")
        st.write(f"**Output Type:** {run.get('output_type', 'N/A')}")
        st.write(f"**Objective:** {run.get('objective', 'N/A')}")

    with col2:
        st.markdown("#### Review Result")
        st.write(f"**Review Status:** {run.get('review_status', 'N/A')}")
        st.write(f"**Success Criteria:** {run.get('success_criteria', 'N/A')}")

    st.markdown("#### Subtasks")
    for item in run.get("subtasks", []):
        st.write("-", item)

    st.markdown("#### Research Notes")
    st.code(run.get("research_notes", ""), language="text")

    st.markdown("#### Final Answer")
    st.code(run.get("final_answer", ""), language="text")

    if run.get("improved_answer"):
        st.markdown("#### Improved Answer")
        st.code(run.get("improved_answer", ""), language="text")

    st.markdown("#### Review Notes")
    st.code(run.get("review_notes", ""), language="text")

    st.markdown("#### Execution Trace")
    for step in run.get("execution_trace", []):
        st.write("-", step)


st.title("Ashok-AgentForge")
st.subheader("Multi-Agent Research, Execution and Review Studio")

app = get_app()

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "latest_error" not in st.session_state:
    st.session_state.latest_error = None


# -------------------------
# Workflow Input
# -------------------------
st.markdown("## Workflow Input")

task = st.text_area(
    "Enter your task",
    value="Research and summarize the best way to build a multi-agent AI project",
    height=120
)

if st.button("Run Workflow"):
    if not task.strip():
        st.session_state.latest_error = "Task input cannot be empty."
        st.session_state.latest_result = None
    else:
        try:
            result = app.invoke({"task": task})
            save_run(result)

            clear_cached_data()
            recent_memory = get_recent_memory_data()

            if recent_memory:
                st.session_state.latest_result = recent_memory[-1]
            else:
                st.session_state.latest_result = result

            st.session_state.latest_error = None
            st.success("Workflow completed and saved")
        except Exception as e:
            st.session_state.latest_error = str(e)
            st.session_state.latest_result = None

result = st.session_state.latest_result
error_message = st.session_state.latest_error

if error_message:
    st.error(f"Workflow failed: {error_message}")

memory = get_recent_memory_data()
memory_df = pd.DataFrame(memory) if memory else pd.DataFrame()

# -------------------------
# Current Run
# -------------------------
st.markdown("---")
st.markdown("## Current Run")

if result:
    render_run_details(result, "Current Run Details")

    result_json = json.dumps(result, indent=2)
    st.download_button(
        label="Download Current Run",
        data=result_json,
        file_name="latest_run.json",
        mime="application/json"
    )
else:
    st.info("Run a workflow to see the current result here.")

# -------------------------
# Run Metrics
# -------------------------
st.markdown("---")
st.markdown("## Run Metrics")

total_runs = len(memory)
approved_runs = sum(1 for run in memory if run.get("review_status") == "approved")
needs_improvement_runs = sum(1 for run in memory if run.get("review_status") == "needs_improvement")
rejected_runs = sum(1 for run in memory if run.get("review_status") == "rejected")
pending_review_runs = sum(1 for run in memory if run.get("review_status") == "pending_review")

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.metric("Visible Runs", total_runs)
with metric_col2:
    st.metric("Approved", approved_runs)
with metric_col3:
    st.metric("Needs Improvement", needs_improvement_runs)
with metric_col4:
    st.metric("Rejected", rejected_runs)
with metric_col5:
    st.metric("Pending Review", pending_review_runs)

# -------------------------
# Filters
# -------------------------
st.markdown("---")
st.markdown("## Audit Filters")

review_options = ["All"]
task_type_options = ["All"]

if not memory_df.empty:
    if "review_status" in memory_df.columns:
        review_options += sorted(memory_df["review_status"].dropna().unique().tolist())
    if "task_type" in memory_df.columns:
        task_type_options += sorted(memory_df["task_type"].dropna().unique().tolist())

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_review_status = st.selectbox("Filter by Review Status", review_options)

with filter_col2:
    selected_task_type = st.selectbox("Filter by Task Type", task_type_options)

search_text = st.text_input("Search Task Text")

filtered_df = memory_df.copy()

if not filtered_df.empty:
    if selected_review_status != "All":
        filtered_df = filtered_df[filtered_df["review_status"] == selected_review_status]

    if selected_task_type != "All":
        filtered_df = filtered_df[filtered_df["task_type"] == selected_task_type]

    if search_text.strip():
        filtered_df = filtered_df[
            filtered_df["task"].fillna("").str.contains(search_text, case=False, na=False)
        ]

# -------------------------
# Run History
# -------------------------
st.markdown("---")
st.markdown("## Run History")

if not filtered_df.empty:
    history_csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Run History",
        data=history_csv,
        file_name="filtered_run_history.csv",
        mime="text/csv"
    )

    st.markdown("### Audit Table")
    display_columns = [
        col for col in [
            "run_id",
            "timestamp",
            "task",
            "task_type",
            "difficulty",
            "output_type",
            "review_status"
        ] if col in filtered_df.columns
    ]
    st.dataframe(filtered_df[display_columns], width="stretch")

    filtered_runs = list(reversed(filtered_df.to_dict(orient="records")))
    run_options = []

    for run in filtered_runs:
        label = f"{run.get('timestamp', 'No time')} | {run.get('run_id', 'N/A')} | {run.get('task', 'No task')}"
        run_options.append(label)

    selected_run_label = st.selectbox("Select Run ID / Task", run_options)

    selected_run = None
    for run in filtered_runs:
        label = f"{run.get('timestamp', 'No time')} | {run.get('run_id', 'N/A')} | {run.get('task', 'No task')}"
        if label == selected_run_label:
            selected_run = run
            break

    if selected_run:
        st.markdown("### Run Detail Viewer")
        render_run_details(selected_run, "Selected Run Details")

        selected_run_json = json.dumps(selected_run, indent=2)

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("Load Selected Run as Current Run"):
                st.session_state.latest_result = selected_run
                st.session_state.latest_error = None
                st.success("Selected saved run loaded into Current Run section.")

        with action_col2:
            st.download_button(
                label="Download Selected Run",
                data=selected_run_json,
                file_name=f"selected_run_{selected_run.get('run_id', 'unknown')}.json",
                mime="application/json"
            )
else:
    st.info("No saved runs found for the selected filters.")

# -------------------------
# Charts
# -------------------------
st.markdown("---")
st.markdown("## Charts")

if not filtered_df.empty:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        review_chart = build_fixed_bar_chart(
            filtered_df,
            "review_status",
            "Review Status Distribution"
        )
        if review_chart is not None:
            st.altair_chart(review_chart, width=440, height=340, theme=None)

    with chart_col2:
        task_chart = build_fixed_bar_chart(
            filtered_df,
            "task_type",
            "Task Type Distribution"
        )
        if task_chart is not None:
            st.altair_chart(task_chart, width=440, height=340, theme=None)
else:
    st.info("Run some workflows to generate charts.")

# -------------------------
# Evaluation Results
# -------------------------
st.markdown("---")
st.markdown("## Evaluation Results")

show_eval = st.checkbox("Show Evaluation Results", value=False)

if show_eval:
    eval_df = get_eval_data()

    if eval_df is not None:
        st.dataframe(eval_df, width="stretch")

        csv_data = eval_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Evaluation Results",
            data=csv_data,
            file_name="eval_results.csv",
            mime="text/csv"
        )
    else:
        st.info("No evaluation file found yet. Run: python -m app.evaluation.run_eval")