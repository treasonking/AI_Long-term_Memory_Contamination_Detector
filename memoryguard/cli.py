"""Command line interface for MemoryGuard-AI."""

from __future__ import annotations

import argparse

from memoryguard.agent_simulator import run_before_after_test
from memoryguard.evaluation import evaluate_samples
from memoryguard.quarantine import quarantine_memory
from memoryguard.report_generator import generate_before_after_report, generate_scan_report
from memoryguard.scanner import load_memory_db, scan_memory_db


DEFAULT_MEMORY_PATH = "data/memory_db.json"
DEFAULT_RULE_PATH = "policies/memory_rules.yaml"
DEFAULT_CLEAN_PATH = "data/clean_memory_samples.json"
DEFAULT_POISONED_PATH = "data/poisoned_memory_samples.json"
DEFAULT_QUARANTINE_PATH = "quarantine/quarantine_store.json"


def _add_memory_rules_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--memory", default=DEFAULT_MEMORY_PATH, help="Path to memory_db.json")
    parser.add_argument("--rules", default=DEFAULT_RULE_PATH, help="Path to memory_rules.yaml")


def run_scan(memory: str, rules: str) -> list:
    results = scan_memory_db(memory, rules)
    print(f"Scanned {len(results)} memories.")
    print(f"Critical: {sum(1 for result in results if result.risk_level == 'CRITICAL')}")
    print(f"High risk: {sum(1 for result in results if result.risk_level == 'HIGH_RISK')}")
    print(f"Suspicious: {sum(1 for result in results if result.risk_level == 'SUSPICIOUS')}")
    print(f"Safe: {sum(1 for result in results if result.risk_level == 'SAFE')}")
    return results


def run_quarantine(memory: str, rules: str, out: str) -> dict:
    results = scan_memory_db(memory, rules)
    summary = quarantine_memory(memory, results, out)
    print(
        "Quarantine complete: "
        f"{summary['quarantined']} quarantined, "
        f"{summary['marked_suspicious']} marked suspicious."
    )
    return summary


def run_report(memory: str, rules: str) -> dict:
    results = scan_memory_db(memory, rules)
    memories = load_memory_db(memory)
    scan_report = generate_scan_report(results, memories)
    evaluation_report = evaluate_samples(memory, rules)
    print(f"Generated {scan_report}")
    print(f"Generated {evaluation_report['report_path']}")
    return {"scan_report": scan_report, "evaluation_report": evaluation_report["report_path"]}


def run_simulate(
    clean_memory: str = DEFAULT_CLEAN_PATH,
    poisoned_memory: str = DEFAULT_POISONED_PATH,
    quarantined_memory: str = DEFAULT_MEMORY_PATH,
) -> str:
    result = run_before_after_test(clean_memory, poisoned_memory, quarantined_memory)
    report_path = generate_before_after_report(result)
    print(f"Generated {report_path}")
    return report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="memoryguard",
        description="Detect and quarantine poisoned long-term memories in LLM agents.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan memory entries")
    _add_memory_rules_args(scan_parser)

    quarantine_parser = subparsers.add_parser("quarantine", help="Quarantine risky memory entries")
    _add_memory_rules_args(quarantine_parser)
    quarantine_parser.add_argument("--out", default=DEFAULT_QUARANTINE_PATH, help="Quarantine store path")

    report_parser = subparsers.add_parser("report", help="Generate scan and evaluation reports")
    _add_memory_rules_args(report_parser)

    simulate_parser = subparsers.add_parser("simulate", help="Generate before/after behavior report")
    simulate_parser.add_argument("--clean", default=DEFAULT_CLEAN_PATH, help="Clean memory sample path")
    simulate_parser.add_argument("--poisoned", default=DEFAULT_POISONED_PATH, help="Poisoned memory sample path")
    simulate_parser.add_argument("--quarantined", default=DEFAULT_MEMORY_PATH, help="Quarantined memory DB path")

    all_parser = subparsers.add_parser("all", help="Run scan, quarantine, report, and simulate")
    _add_memory_rules_args(all_parser)
    all_parser.add_argument("--out", default=DEFAULT_QUARANTINE_PATH, help="Quarantine store path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        run_scan(args.memory, args.rules)
    elif args.command == "quarantine":
        run_quarantine(args.memory, args.rules, args.out)
    elif args.command == "report":
        run_report(args.memory, args.rules)
    elif args.command == "simulate":
        run_simulate(args.clean, args.poisoned, args.quarantined)
    elif args.command == "all":
        run_scan(args.memory, args.rules)
        run_quarantine(args.memory, args.rules, args.out)
        run_report(args.memory, args.rules)
        run_simulate(DEFAULT_CLEAN_PATH, DEFAULT_POISONED_PATH, args.memory)
    else:
        parser.error(f"Unknown command: {args.command}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
