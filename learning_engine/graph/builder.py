"""Graph builder: export findings as a JSON graph (targets/classes/signals/lessons)."""

from __future__ import annotations

import json

from ..core.storage import Database


def build_graph(db: Database) -> dict:
    """Nodes: targets, vuln_classes, signals, lessons. Edges connect them."""
    findings = db.rows("SELECT * FROM findings ORDER BY id")
    lessons = db.rows("SELECT * FROM lessons ORDER BY id")

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def _node(kind: str, key: str, **extra) -> str:
        nid = f"{kind}:{key}"
        nodes.setdefault(nid, {"id": nid, "kind": kind, "key": key, **extra})
        return nid

    for f in findings:
        t = _node("target", f["target"])
        c = _node("vuln_class", f["vuln_class"], severity=f["severity"])
        edges.append({"from": t, "to": c, "kind": "finding",
                      "finding_id": f["finding_id"], "title": f["title"]})
        for key in json.loads(f["signals"] or "{}"):
            s = _node("signal", key)
            edges.append({"from": c, "to": s, "kind": "signal"})

    for l in lessons:
        c = _node("vuln_class", l["vuln_class"])
        n = _node("lesson", l["lesson"][:64], support=l["support"])
        edges.append({"from": c, "to": n, "kind": "lesson"})

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "targets": sum(1 for n in nodes.values() if n["kind"] == "target"),
            "vuln_classes": sum(1 for n in nodes.values() if n["kind"] == "vuln_class"),
            "signals": sum(1 for n in nodes.values() if n["kind"] == "signal"),
            "lessons": sum(1 for n in nodes.values() if n["kind"] == "lesson"),
        },
    }


def save_graph(graph: dict, path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(graph, fh, indent=2, ensure_ascii=False)