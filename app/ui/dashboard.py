import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
sys.path.append(str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
import altair as alt
import json
from app.workflows.graph import build_graph
from app.memory.run_memory import save_run, load_memory

st.set_page_config(
    page_title="Ashok-AgentForge",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Ashok-AgentForge")
st.subheader("Multi-Agent Research, Execution and Review Studio")

app = build_graph()


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

    chart = chart.configure(
        autosize=alt.AutoSizeParams(
            type="none",
            resize=False,
            contains="content"
        )
    )

    return chart


def render_run_details(run, section_title):
    st.markdown(f"### {section_title}")
    st.write("**Run ID:**", run.get("run_id", "N/A"))
    st.write("**Timestamp:**", run.get("timestamp", "N/A"))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Task Analysis")
        st.write("**Task:**", run.get("task"))
        st.write("**Task Type:**", run.get("task_type"))
        st.write("**Difficulty:**", run.get("difficulty"))
        st.write("**Output Type:**", run.get("output_type"))
        st.write("**Objective:**", run.get("objective"))

    with col2:
        st.markdown("#### Review Result")
        st.write("**Review Status:**", run.get("review_status"))
        st.write("**Success Criteria:**", run.get("success_criteria"))

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


if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "latest_error" not in st.session_state:
    st.session_state.latest_error = None


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

            memory_after_save = load_memory()
            if memory_after_save:
                st.session_state.latest_result = memory_after_save[-1]
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

memory = load_memory()
memory_df = pd.DataFrame(memory) if memory else pd.DataFrame()

st.sidebar.header("Run Metrics")

total_runs = len(memory)
approved_runs = sum(1 for run in memory if run.get("review_status") == "approved")
needs_improvement_runs = sum(1 for run in memory if run.get("review_status") == "needs_improvement")
last_task_type = memory[-1].get("task_type") if memory else "N/A"

st.sidebar.write("**Total Runs:**", total_runs)
st.sidebar.write("**Approved Runs:**", approved_runs)
st.sidebar.write("**Needs Improvement Runs:**", needs_improvement_runs)
st.sidebar.write("**Last Task Type:**", last_task_type)

st.sidebar.markdown("---")
st.sidebar.header("Filters")

review_options = ["All"]
task_type_options = ["All"]

if not memory_df.empty:
    if "review_status" in memory_df.columns:
        review_options += sorted(memory_df["review_status"].dropna().unique().tolist())
    if "task_type" in memory_df.columns:
        task_type_options += sorted(memory_df["task_type"].dropna().unique().tolist())

selected_review_status = st.sidebar.selectbox("Review Status", review_options)
selected_task_type = st.sidebar.selectbox("Task Type", task_type_options)
search_text = st.sidebar.text_input("Search Task Text")

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

tab1, tab2, tab3, tab4 = st.tabs([
    "Current Run",
    "Run History",
    "Charts",
    "Evaluation"
])

with tab1:
    if result:
        render_run_details(result, "Current Run")

        result_json = json.dumps(result, indent=2)
        st.download_button(
            label="Download Current Run",
            data=result_json,
            file_name="latest_run.json",
            mime="application/json"
        )
    else:
        st.info("Run a workflow to see the current result here.")

with tab2:
    st.markdown("## Run History")

    if not filtered_df.empty:
        history_csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Run History",
            data=history_csv,
            file_name="filtered_run_history.csv",
            mime="text/csv"
        )

        filtered_runs = list(reversed(filtered_df.to_dict(orient="records")))
        run_options = []

        for run in filtered_runs:
            label = f"{run.get('timestamp', 'No time')} | {run.get('run_id', 'N/A')} | {run.get('task', 'No task')}"
            run_options.append(label)

        selected_run_label = st.selectbox("Select a saved run to inspect", run_options)

        selected_run = None
        for run in filtered_runs:
            label = f"{run.get('timestamp', 'No time')} | {run.get('run_id', 'N/A')} | {run.get('task', 'No task')}"
            if label == selected_run_label:
                selected_run = run
                break

        if selected_run:
            render_run_details(selected_run, "Selected Saved Run")

            selected_run_json = json.dumps(selected_run, indent=2)

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button("Load Selected Run as Current Run"):
                    st.session_state.latest_result = selected_run
                    st.session_state.latest_error = None
                    st.success("Selected saved run loaded into Current Run tab.")

            with action_col2:
                st.download_button(
                    label="Download Selected Run",
                    data=selected_run_json,
                    file_name=f"selected_run_{selected_run.get('run_id', 'unknown')}.json",
                    mime="application/json"
                )

        st.markdown("### Latest Filtered Runs")
        latest_runs = filtered_runs[:5]

        for idx, run in enumerate(latest_runs, start=1):
            run_title = f"Run {idx}: {run.get('task', 'No task')}"
            run_time = run.get("timestamp", "No time")
            with st.expander(f"{run_title} | {run_time}"):
                st.write("**Run ID:**", run.get("run_id", "N/A"))
                st.write("**Timestamp:**", run.get("timestamp", "N/A"))
                st.write("**Task Type:**", run.get("task_type"))
                st.write("**Difficulty:**", run.get("difficulty"))
                st.write("**Output Type:**", run.get("output_type"))
                st.write("**Review Status:**", run.get("review_status"))
    else:
        st.info("No saved runs found for the selected filters.")

with tab3:
    st.markdown("## Workflow Charts")

    if not filtered_df.empty:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            review_chart = build_fixed_bar_chart(
                filtered_df,
                "review_status",
                "Review Status Distribution"
            )
            if review_chart is not None:
                st.altair_chart(
                    review_chart,
                    width=440,
                    height=340,
                    theme=None
                )

        with chart_col2:
            task_chart = build_fixed_bar_chart(
                filtered_df,
                "task_type",
                "Task Type Distribution"
            )
            if task_chart is not None:
                st.altair_chart(
                    task_chart,
                    width=440,
                    height=340,
                    theme=None
                )
    else:
        st.info("Run some workflows to generate charts.")

with tab4:
    st.markdown("## Evaluation Results")

    eval_file = Path("outputs/eval_results.csv")

    if eval_file.exists():
        eval_df = pd.read_csv(eval_file)
        st.dataframe(eval_df, use_container_width=True)

        csv_data = eval_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Evaluation Results",
            data=csv_data,
            file_name="eval_results.csv",
            mime="text/csv"
        )
    else:
        st.info("No evaluation file found yet. Run: python -m app.evaluation.run_eval")