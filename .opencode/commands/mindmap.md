---
description: Visualize target assets and findings as a graph
agent: build
---

# Autonomous Mindmap

Target or notes:
$ARGUMENTS

Generate a knowledge-graph JSON of assets/findings from the learning engine.

## Steps

1. `python -c "from learning_engine import engine; import json; print(json.dumps(engine.stats()))"`.
2. Export the graph:
   `python -c "from learning_engine import engine; from learning_engine.graph.builder import save_graph; save_graph(engine.export_graph(), 'writeups/metadata/graph.json')"`.
3. Optional: render nodes/edges with your preferred tool (the JSON is
   `{nodes: [{id, kind, key}], edges: [{from, to, kind}]}`).
4. For target trees, `scripts/index.sh` already emits
   `testing/<root>/index.md` summaries.

## Output

- `writeups/metadata/graph.json` — cross-target view of classes/signals/lessons.
- `testing/<root>/index.md` — per-target asset view.