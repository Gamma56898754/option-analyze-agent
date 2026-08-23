from langgraph.graph import END, START, StateGraph

from agent.llm_agent import LLMAgent
from graph.nodes import OptionGraphNodes
from graph.state import OptionAgentState
from graph.routing import (
    route_after_validation,
    route_after_short_term_memory,
    route_after_analysis,
)
from graph.routing import (
    route_after_agent_decision,
    route_after_short_term_memory,
    route_after_tool_execution,
)


def build_option_graph(
    agent: LLMAgent,
    checkpointer=None,
):

    nodes = OptionGraphNodes(
    agent
    )

    builder = StateGraph(
        OptionAgentState
    )

    builder.add_node(
        "agent_decide",
        nodes.agent_decide_node
    )

    builder.add_node(
        "execute_tool_call",
        nodes.execute_tool_call_node
    )

    builder.add_node(
        "direct_answer",
        nodes.direct_answer_node
    )

    builder.add_node(
        "generate_answer",
        nodes.generate_answer_node
    )

    builder.add_node(
        "validation_failed",
        nodes.validation_failed_node
    )

    builder.add_node(
        "analysis_failed",
        nodes.analysis_failed_node
    )

    builder.add_node(
        "update_short_term_memory",
        nodes.update_short_term_memory_node
    )

    builder.add_node(
        "summarize_conversation",
        nodes.summarize_conversation_node
    )

    builder.add_edge(
        START,
        "agent_decide"
    )

    builder.add_conditional_edges(
        "agent_decide",
        route_after_agent_decision,
        {
            "tool_call": "execute_tool_call",
            "final_answer": "direct_answer",
        }
    )

    builder.add_conditional_edges(
        "execute_tool_call",
        route_after_tool_execution,
        {
            "success": "generate_answer",
            "invalid": "validation_failed",
            "failed": "analysis_failed",
        }
    )

    builder.add_edge(
        "generate_answer",
        "update_short_term_memory"
    )

    builder.add_edge(
        "direct_answer",
        "update_short_term_memory"
    )

    builder.add_edge(
        "analysis_failed",
        "update_short_term_memory"
    )

    builder.add_edge(
        "validation_failed",
        END
    )

    builder.add_conditional_edges(
        "update_short_term_memory",
        route_after_short_term_memory,
        {
            "summarize": "summarize_conversation",
            "end": END,
        }
    )

    builder.add_edge(
        "summarize_conversation",
        END
    )

    return builder.compile(
        checkpointer=checkpointer,
    )