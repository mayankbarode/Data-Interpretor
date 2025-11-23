from langgraph.graph import StateGraph, END
from app.state import AgentState
from app.agents.nodes import supervisor_node, planner_node, coder_node, executor_node, summarizer_node, debugger_node

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)
workflow.add_node("executor", executor_node)
workflow.add_node("debugger", debugger_node)

# Conditional edge function
def should_continue(state: AgentState):
    """Return the next node based on execution status."""
    error = state.get('error')
    retry_count = state.get('retry_count', 0)
    
    if error and retry_count < 3:
        return "debugger"
    return END

# Define edges
# For the chat flow: Planner -> Coder -> Executor -> (Debugger -> Executor) -> END
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "executor")
workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "debugger": "debugger",
        END: END
    }
)
workflow.add_edge("debugger", "executor")

# Set entry point
workflow.set_entry_point("planner")

# Compile
app_graph = workflow.compile()
