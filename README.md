# Ashok-AgentForge

Ashok-AgentForge is a multi-agent workflow application built with LangGraph and Streamlit. It simulates a realistic AI engineering workflow where a task moves through structured stages such as planning, research, writing, review, and conditional improvement.

## Features

- Multi-step LangGraph workflow
- Task analyzer tool for task classification
- Planner, Researcher, Writer, Reviewer, and Improver nodes
- Conditional routing based on review outcome
- Shared workflow state across all nodes
- Execution trace logging
- Persistent run memory with run ID and timestamp
- Streamlit dashboard with:
  - Current run view
  - Run history
  - Search and filters
  - Charts
  - Evaluation results
- Download support for run outputs and evaluation results

## Workflow Overview

The workflow follows this general path:

Task Input -> Planner -> Researcher -> Writer -> Reviewer

If review is approved:
Reviewer -> End

If review needs improvement:
Reviewer -> Improver -> End

## Project Structure

```text
Ashok-AgentForge/
├── app/
│   ├── agents/
│   ├── config/
│   ├── evaluation/
│   ├── memory/
│   ├── tools/
│   ├── ui/
│   ├── utils/
│   └── workflows/
├── data/
├── outputs/
├── tests/
├── notebooks/
├── main.py
├── requirements.txt
├── .env
├── .env.example
└── README.md

## Architecture Diagram

```mermaid
flowchart LR
    A[User Task] --> B[Planner Node]
    B --> C[Researcher Node]
    C --> D[Writer Node]
    D --> E[Reviewer Node]
    E -->|approved| F[End]
    E -->|needs_improvement| G[Improver Node]
    G --> F