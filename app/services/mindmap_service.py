from typing import Dict, List


def build_mindmap(
    actions: List[Dict[str, str]], topics: List[str]
) -> Dict[str, List[Dict[str, str]]]:
    """Construct minimal mind map structure until networkx integration is added."""
    nodes = [{"id": "root", "label": "Meeting Summary"}]
    links: List[Dict[str, str]] = []

    for index, topic in enumerate(topics, start=1):
        topic_id = f"topic-{index}"
        nodes.append({"id": topic_id, "label": topic})
        links.append({"source": "root", "target": topic_id})

    for idx, action in enumerate(actions, start=1):
        action_id = f"action-{idx}"
        label = action.get("task") or action.get("summary") or "Action"
        nodes.append({"id": action_id, "label": label})
        links.append({"source": "root", "target": action_id})

    return {"nodes": nodes, "links": links}
