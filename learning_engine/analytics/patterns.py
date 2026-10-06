"""Analytics: aggregate findings/triage into per-class patterns and lessons."""

from __future__ import annotations

import json

from ..core.storage import Database
from ..scoring.engine import weight_for


def per_class_stats(db: Database) -> list[dict]:
    """Per-vuln-class aggregates: counts, fp_rate, top signals, lesson candidates."""
    findings = db.rows("SELECT * FROM findings ORDER BY id")
    verdicts: dict[str, list[str]] = {}
    for t in db.rows("SELECT finding_id, verdict FROM triage ORDER BY id"):
        verdicts.setdefault(t["finding_id"], []).append(t["verdict"])

    by_class: dict[str, dict] = {}
    signal_occurrence: dict[str, dict[str, int]] = {}
    for f in findings:
        c = f["vuln_class"]
        agg = by_class.setdefault(
            c,
            {
                "vuln_class": c,
                "count": 0,
                "confirmed": 0,
                "false_positive": 0,
                "unverified": 0,
                "avg_confidence": 0.0,
                "top_signals": [],
                "targets": set(),
                "lessons": [],
                "conf_sums": 0.0,
            },
        )
        agg["count"] += 1
        agg["conf_sums"] += float(f["confidence"])
        agg["targets"].add(f["target"])
        signals = json.loads(f["signals"] or "{}")
        for key in signals:
            signal_occurrence.setdefault(c, {}).setdefault(key, 0)
            signal_occurrence[c][key] += 1
        v = (verdicts.get(f["finding_id"]) or ["unverified"])[-1]
        agg[v] += 1

    out: list[dict] = []
    for c, agg in by_class.items():
        n = max(1, agg["count"])
        agg["avg_confidence"] = round(agg["conf_sums"] / n, 3)
        fp = agg["false_positive"]
        agg["fp_rate"] = round(fp / n, 4)
        signals = signal_occurrence.get(c, {})
        agg["top_signals"] = sorted(signals, key=lambda k: (-signals[k], -weight_for(k)))[:10]
        agg["targets"] = sorted(agg["targets"])
        del agg["conf_sums"]
        out.append(agg)
    out.sort(key=lambda a: (-a["count"], a["vuln_class"]))
    return out


def fp_pattern_candidates(db: Database, min_occurrences: int = 2) -> list[dict]:
    """Signal keys co-occurring with false_positive verdicts, as FP patterns."""
    rows = db.rows(
        """
        SELECT f.vuln_class, f.signals, f.title
        FROM findings f
        JOIN triage t ON t.finding_id = f.finding_id
        WHERE t.verdict = 'false_positive'
        ORDER BY t.id
        """
    )
    signal_hits: dict[tuple[str, str], int] = {}
    for r in rows:
        for key in json.loads(r["signals"] or "{}"):
            signal_hits[(r["vuln_class"], key)] = signal_hits.get((r["vuln_class"], key), 0) + 1
    return [
        {"vuln_class": c, "signal": key, "occurrences": n}
        for (c, key), n in sorted(signal_hits.items(), key=lambda kv: -kv[1])
        if n >= min_occurrences
    ]


def signal_heatmap(db: Database) -> dict:
    """Per-class signal occurrence counts: {vuln_class: {signal: count}}."""
    out: dict[str, dict[str, int]] = {}
    for f in db.rows("SELECT vuln_class, signals FROM findings"):
        for key in json.loads(f["signals"] or "{}"):
            out.setdefault(f["vuln_class"], {}).setdefault(key, 0)
            out[f["vuln_class"]][key] += 1
    return {c: dict(sorted(sig.items(), key=lambda kv: -kv[1])) for c, sig in out.items()}


def highest_signal_surfaces(db: Database, limit: int = 10) -> list[dict]:
    """Top vuln-class surfaces by count, then avg confidence, then fp_rate."""
    classes = per_class_stats(db)
    ranked = sorted(
        classes,
        key=lambda c: (-c["count"], -c["avg_confidence"], c["fp_rate"]),
    )
    return ranked[:limit]


def duplicate_heavy_patterns(db: Database, min_occurrences: int = 2) -> list[dict]:
    """(vuln_class, signal) pairs whose latest triage verdict is unverified
    (duplicates/informative map to unverified) — pattern to avoid or refine."""
    rows = db.rows(
        """
        SELECT f.vuln_class, f.signals
        FROM findings f
        JOIN triage t ON t.finding_id = f.finding_id
        WHERE t.id = (SELECT max(t2.id) FROM triage t2 WHERE t2.finding_id = f.finding_id)
          AND t.verdict = 'unverified'
        """
    )
    hits: dict[tuple[str, str], int] = {}
    for r in rows:
        for key in json.loads(r["signals"] or "{}"):
            hits[(r["vuln_class"], key)] = hits.get((r["vuln_class"], key), 0) + 1
    return [
        {"vuln_class": c, "signal": key, "occurrences": n}
        for (c, key), n in sorted(hits.items(), key=lambda kv: -kv[1])
        if n >= min_occurrences
    ]


def target_summary(db: Database, target: str) -> dict:
    """Per-class findings + signals for one target."""
    rows = db.rows(
        "SELECT * FROM findings WHERE target = ? ORDER BY id", (target,)
    )
    by_class: dict[str, dict] = {}
    for f in rows:
        agg = by_class.setdefault(f["vuln_class"], {"count": 0, "findings": [], "signals": {}})
        agg["count"] += 1
        agg["findings"].append({"finding_id": f["finding_id"], "title": f["title"],
                                "severity": f["severity"], "confidence": f["confidence"]})
        for key in json.loads(f["signals"] or "{}"):
            agg["signals"][key] = agg["signals"].get(key, 0) + 1
    return {"target": target, "classes": by_class,
            "total_findings": len(rows)}