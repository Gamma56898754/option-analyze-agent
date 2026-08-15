from langgraph.graph import END, START, StateGraph

from agent.llm_agent import LLMAgent
from graph.nodes import OptionGraphNodes
from graph.state import OptionAgentState
from graph.routing import (
    route_after_validation,
    route_after_short_term_memory,
    route_after_analysis,
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
        "parse_request",
        nodes.parse_request_node
    )

    builder.add_node(
        "validate_request",
        nodes.validate_request_node
    )

    builder.add_node(
        "validation_failed",
        nodes.validation_failed_node
    )

    builder.add_node(
        "run_analysis",
        nodes.run_analysis_node
    )

    builder.add_node(
        "format_result",
        nodes.format_result_node
    )

    builder.add_node(
        "generate_answer",
        nodes.generate_answer_node
    )

    builder.add_node(
        "update_short_term_memory",
        nodes.update_short_term_memory_node
    )

    builder.add_node(
        "summarize_conversation",
        nodes.summarize_conversation_node
    )

    builder.add_node(
        "analysis_failed",
        nodes.analysis_failed_node
    )

    builder.add_edge(
        START,
        "parse_request"
    )

    builder.add_edge(
        "parse_request",
        "validate_request"
    )

    builder.add_conditional_edges(
        "validate_request",
        route_after_validation,
        {
            "run_analysis": "run_analysis",
            "explain_existing": "generate_answer",
            "invalid": "validation_failed",
        }
    )

    builder.add_edge(
        "validation_failed",
        END
    )

    builder.add_conditional_edges(
        "run_analysis",
        route_after_analysis,
        {
            "success": "format_result",
            "failed": "analysis_failed",
        }
    )

    builder.add_edge(
        "analysis_failed",
        "update_short_term_memory"
    )

    builder.add_edge(
        "format_result",
        "generate_answer"
    )

    builder.add_edge(
        "generate_answer",
        "update_short_term_memory"
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