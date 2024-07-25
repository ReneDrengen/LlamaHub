from typing import Optional

from .events import StopEvent
from .decorators import StepConfig
from .utils import get_steps_from_class


def draw_all_possible_flows(
    workflow,
    filename: str = "workflow_all_flows.html",
    notebook: bool = False,
) -> None:
    """Draws all possible flows of the workflow."""
    from pyvis.network import Network

    net = Network(directed=True, height="750px", width="100%")

    # Add the nodes + edge for stop events
    net.add_node(
        StopEvent.__name__,
        label=StopEvent.__name__,
        color="#FFA07A",
        shape="ellipse",
    )
    net.add_node("_done", label="_done", color="#ADD8E6", shape="box")
    net.add_edge(StopEvent.__name__, "_done")

    # Add nodes from all steps
    for step_name, step_func in get_steps_from_class(workflow).items():
        step_config: Optional[StepConfig] = getattr(step_func, "__step_config", None)
        if step_config is None:
            continue

        net.add_node(
            step_name, label=step_name, color="#ADD8E6", shape="box"
        )  # Light blue for steps

        for event_type in step_config.accepted_events:
            net.add_node(
                event_type.__name__,
                label=event_type.__name__,
                color="#90EE90",
                shape="ellipse",
            )  # Light green for events

    # Add edges from all steps
    for step_name, step_func in get_steps_from_class(workflow).items():
        step_config: Optional[StepConfig] = getattr(step_func, "__step_config", None)

        if step_config is None:
            continue

        for return_type in step_config.return_types:
            if return_type != type(None):
                net.add_edge(step_name, return_type.__name__)

        for event_type in step_config.accepted_events:
            net.add_edge(event_type.__name__, step_name)

    net.show(filename, notebook=notebook)


def draw_most_recent_execution(
    workflow,
    filename: str = "workflow_recent_execution.html",
    notebook: bool = False,
) -> None:
    """Draws the most recent execution of the workflow."""
    from pyvis.network import Network

    net = Network(directed=True, height="750px", width="100%")

    # Add nodes and edges based on execution history
    for i, (step, event) in enumerate(workflow._accepted_events):
        event_node = f"{event}_{i}"
        step_node = f"{step}_{i}"
        net.add_node(
            event_node, label=event, color="#90EE90", shape="ellipse"
        )  # Light green for events
        net.add_node(
            step_node, label=step, color="#ADD8E6", shape="box"
        )  # Light blue for steps
        net.add_edge(event_node, step_node)

        if i > 0:
            prev_step_node = f"{workflow._accepted_events[i - 1][0]}_{i - 1}"
            net.add_edge(prev_step_node, event_node)

    net.show(filename, notebook=notebook)
