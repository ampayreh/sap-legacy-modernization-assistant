#!/usr/bin/env python3
"""
SAP Legacy Modernization Analyzer

Reads a YAML-formatted SAP ECC legacy configuration and produces a
modernization delta report identifying S/4HANA simplification item
impacts, required migration actions, and a prioritized remediation plan.

The analyzer uses Claude's tool-use capability to look up relevant
Simplification Items from a curated reference dataset. Each finding
in the report links to the official SAP Help Portal documentation.

Usage:
    python analyzer.py --config examples/gbi-legacy-config.yaml
    python analyzer.py --config examples/gbi-legacy-config.yaml --output report.md
    python analyzer.py --config examples/gbi-legacy-config.yaml --format json

Environment:
    ANTHROPIC_API_KEY  — required
    MODEL_ID           — model to use (default: claude-sonnet-4-20250514)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from simplification_items import (
    SIMPLIFICATION_ITEM_TOOL,
    search_simplification_items,
)


MODEL_ID = os.environ.get("MODEL_ID", "claude-sonnet-4-20250514")
MAX_TOOL_ROUNDS = 10


# ── Configuration Parser ──────────────────────────────────

def load_config(path: str) -> dict:
    """Load and validate a YAML legacy configuration file."""
    config_path = Path(path)
    if not config_path.exists():
        print(f"Error: config file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        print("Error: config file must be a YAML mapping", file=sys.stderr)
        sys.exit(1)

    return config


def summarize_config(config: dict) -> str:
    """Produce a structured text summary of the legacy config for the prompt."""
    lines = []

    # System info
    sys_info = config.get("system", {})
    lines.append("## System Overview")
    lines.append(f"- Version: {sys_info.get('version', 'Unknown')}")
    lines.append(f"- Database: {sys_info.get('database', 'Unknown')}")
    lines.append(f"- OS: {sys_info.get('os', 'Unknown')}")
    lines.append("")

    # Company codes
    ccs = config.get("company_codes", [])
    if ccs:
        lines.append("## Company Codes")
        for cc in ccs:
            lines.append(
                f"- {cc['code']} ({cc['name']}): "
                f"country={cc.get('country')}, "
                f"currency={cc.get('currency')}, "
                f"CoA={cc.get('chart_of_accounts')}"
            )
        lines.append("")

    # Plants
    plants = config.get("plants", [])
    if plants:
        lines.append("## Plants")
        for p in plants:
            wm = "Classic WM active" if p.get("wm_active") else "No WM"
            lines.append(f"- {p['plant']} ({p['name']}): {wm}")
        lines.append("")

    # Financial accounting
    fa = config.get("financial_accounting", {})
    if fa:
        lines.append("## Financial Accounting")
        gl = fa.get("general_ledger", {})
        lines.append(f"- General Ledger: {gl.get('type', 'unknown')} GL")
        lines.append(f"- Document Splitting: {gl.get('document_splitting', False)}")

        aa = fa.get("asset_accounting", {})
        lines.append(f"- Asset Accounting Engine: {aa.get('engine', 'unknown')}")
        for da in aa.get("depreciation_areas", []):
            lines.append(f"  - Area {da['area']}: {da['name']} ({da.get('posting', 'unknown')})")
        for rpt in aa.get("custom_reports", []):
            lines.append(f"  - Custom report: {rpt}")

        ap = fa.get("accounts_payable", {})
        for rpt in ap.get("custom_reports", []):
            lines.append(f"- AP custom report: {rpt}")

        ar = fa.get("accounts_receivable", {})
        for rpt in ar.get("custom_reports", []):
            lines.append(f"- AR custom report: {rpt}")
        cm = ar.get("credit_management", {})
        if cm:
            lines.append(f"- Credit Management: {cm.get('type', 'unknown')}")
            for ex in cm.get("custom_exits", []):
                lines.append(f"  - Custom exit: {ex}")

        md = fa.get("master_data", {})
        lines.append(f"- Vendor Master: {md.get('vendor_master', 'unknown')}")
        lines.append(f"- Customer Master: {md.get('customer_master', 'unknown')}")
        lines.append(f"- Business Partner configured: {md.get('business_partner', False)}")
        for prog in md.get("custom_programs", []):
            lines.append(f"  - Custom program: {prog}")
        lines.append("")

    # Controlling
    co = config.get("controlling", {})
    if co:
        lines.append("## Controlling")
        cca = co.get("cost_center_accounting", {})
        for rpt in cca.get("custom_reports", []):
            lines.append(f"- CCA custom report: {rpt}")
        copa = co.get("profitability_analysis", {})
        if copa:
            lines.append(f"- CO-PA type: {copa.get('type', 'unknown')}")
            lines.append(f"- Operating concern: {copa.get('operating_concern', 'unknown')}")
            for vf in copa.get("custom_value_fields", []):
                lines.append(f"  - Custom value field: {vf}")
        lines.append("")

    # Materials Management
    mm = config.get("materials_management", {})
    if mm:
        lines.append("## Materials Management")
        mat = mm.get("material_master", {})
        lines.append(f"- Material number length: {mat.get('number_length', 'unknown')}")
        for mt in mat.get("custom_material_types", []):
            lines.append(f"  - Custom material type: {mt}")
        inv = mm.get("inventory", {})
        lines.append(f"- Material Ledger: {'active' if inv.get('material_ledger') else 'not activated'}")
        lines.append(f"- Actual Costing: {'active' if inv.get('actual_costing') else 'not activated'}")
        for rpt in inv.get("custom_reports", []):
            lines.append(f"  - Custom report: {rpt}")
        lines.append("")

    # Sales & Distribution
    sd = config.get("sales_distribution", {})
    if sd:
        lines.append("## Sales and Distribution")
        om = sd.get("output_management", {})
        lines.append(f"- Output Management: {om.get('type', 'unknown')}")
        for form in om.get("forms", []):
            lines.append(f"  - Form: {form['name']} ({form.get('type', 'unknown')})")
        bil = sd.get("billing", {})
        for prog in bil.get("custom_programs", []):
            lines.append(f"  - Custom billing: {prog}")
        lines.append("")

    # Production Planning
    pp = config.get("production_planning", {})
    if pp:
        lines.append("## Production Planning")
        mrp = pp.get("mrp", {})
        lines.append(f"- MRP type: {mrp.get('type', 'unknown')}")
        for ex in mrp.get("custom_exits", []):
            lines.append(f"  - Custom exit: {ex}")
        po = pp.get("production_orders", {})
        for rpt in po.get("custom_reports", []):
            lines.append(f"  - Custom report: {rpt}")
        lines.append("")

    # Warehouse Management
    wm = config.get("warehouse_management", {})
    if wm:
        lines.append("## Warehouse Management")
        lines.append(f"- Type: {wm.get('type', 'unknown')}")
        for wh in wm.get("warehouses", []):
            lines.append(f"  - Warehouse {wh['warehouse']} at plant {wh['plant']}")
        for prog in wm.get("custom_programs", []):
            lines.append(f"  - Custom program: {prog}")
        lines.append("")

    # Custom Code
    cc = config.get("custom_code", {})
    if cc:
        lines.append("## Custom Code Inventory")
        lines.append(f"- Z programs: {cc.get('total_z_programs', 0)}")
        lines.append(f"- Z includes: {cc.get('total_z_includes', 0)}")
        lines.append(f"- Z function modules: {cc.get('total_z_function_modules', 0)}")
        lines.append(f"- Test coverage: {cc.get('abap_test_coverage', 'unknown')}")
        for mod in cc.get("modifications", []):
            lines.append(f"  - {mod['type']}: {mod['object']}")
        lines.append("")

    # Interfaces
    ifaces = config.get("interfaces", [])
    if ifaces:
        lines.append("## Interfaces")
        for iface in ifaces:
            lines.append(
                f"- {iface['name']}: {iface['type']} ({iface['direction']}) "
                f"— {iface.get('description', '')}"
            )
        lines.append("")

    # User Experience
    ux = config.get("user_experience", {})
    if ux:
        lines.append("## User Experience")
        lines.append(f"- Primary UI: {ux.get('primary_ui', 'unknown')}")
        lines.append(f"- Fiori Launchpad: {'deployed' if ux.get('fiori_launchpad') else 'not deployed'}")
        for app in ux.get("custom_bsp_apps", []):
            lines.append(f"  - Custom BSP: {app}")
        lines.append("")

    return "\n".join(lines)


# ── Claude Integration ────────────────────────────────────

SYSTEM_PROMPT = """You are an SAP S/4HANA migration specialist analyzing a legacy SAP ECC configuration.

Your task is to:
1. Read the legacy configuration carefully
2. Use the lookup_simplification_items tool to find ALL relevant Simplification Items that affect this configuration
3. Produce a comprehensive modernization delta report

For each area in the configuration, search for relevant simplification items using specific terms:
- Search for table names (BSEG, ANLC, COEP, etc.)
- Search for feature names (asset accounting, warehouse management, etc.)
- Search for module codes (FI, CO, MM, SD, etc.)
- Search for specific patterns mentioned (classic GL, vendor master, SAPscript, etc.)

Be thorough: make multiple searches to cover all areas of the configuration. Do not guess which items are relevant — use the tool.

After gathering all relevant simplification items, produce a delta report in this structure:

# SAP ECC to S/4HANA — Modernization Delta Report

## Executive Summary
Brief overview of the system, number of findings by severity, and key risks.

## Findings by Priority

### Critical (Migration Blockers)
Items that MUST be resolved before or during migration. Impact level: mandatory.

### High (Significant Rework)
Items that require substantial effort but are not blockers. Impact level: mandatory or recommended.

### Medium (Planned Migration)
Items that should be addressed but have workarounds. Impact level: recommended.

### Low (Future Optimization)
Items that are optional enhancements. Impact level: optional.

For each finding, include:
- **Simplification Item:** [ID] — [Title]
- **Module:** [module code]
- **What breaks:** specific items from the legacy config that are affected
- **Migration action:** concrete steps
- **Effort estimate:** T-shirt size (S/M/L/XL) with rationale
- **Reference:** [Title](URL) — link to SAP Help Portal

## Custom Code Impact Assessment
Summary of custom programs, reports, and enhancements that need adaptation.

## Migration Sequence Recommendation
Suggested order of migration activities with dependencies.

## Risk Register
Top risks with mitigation strategies.

Be specific: reference actual program names, table names, and configuration elements from the input. Do not produce generic advice."""


def analyze_config(client, config: dict) -> dict:
    """Run the analyzer: send config to Claude with tool use, return report + metrics."""
    config_summary = summarize_config(config)

    messages = [
        {
            "role": "user",
            "content": (
                "Analyze this SAP ECC legacy configuration and produce a "
                "modernization delta report for S/4HANA migration.\n\n"
                f"# Legacy Configuration\n\n{config_summary}"
            ),
        }
    ]

    tools = [SIMPLIFICATION_ITEM_TOOL]
    tool_calls_total = 0
    input_tokens_total = 0
    output_tokens_total = 0
    t0 = time.monotonic()

    for round_idx in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=16384,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=tools,
        )

        input_tokens_total += response.usage.input_tokens
        output_tokens_total += response.usage.output_tokens

        # Check if the model wants to use tools
        if response.stop_reason == "tool_use":
            # Process tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_total += 1
                    query = block.input.get("query", "")
                    module = block.input.get("module")

                    print(
                        f"  Tool call #{tool_calls_total}: "
                        f"lookup_simplification_items("
                        f"query={query!r}, module={module!r})",
                        flush=True,
                    )

                    results = search_simplification_items(query, module)

                    # Format results for the model
                    formatted = []
                    for item in results:
                        formatted.append({
                            "id": item["id"],
                            "title": item["title"],
                            "module": item["module"],
                            "impact": item["impact"],
                            "summary": item["summary"],
                            "legacy_indicators": item["legacy_indicators"],
                            "migration_action": item["migration_action"],
                            "url": item["url"],
                        })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(formatted, indent=2),
                    })

            # Append assistant response and tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Model is done — extract the final text
            break
    else:
        print(f"Warning: reached max tool rounds ({MAX_TOOL_ROUNDS})", file=sys.stderr)

    latency_ms = (time.monotonic() - t0) * 1000

    # Extract text from final response
    report_text = "\n".join(
        block.text for block in response.content if block.type == "text"
    )

    # Cost estimate (Sonnet pricing: $3/M input, $15/M output)
    cost_usd = input_tokens_total * 3e-6 + output_tokens_total * 15e-6

    metrics = {
        "model": MODEL_ID,
        "input_tokens": input_tokens_total,
        "output_tokens": output_tokens_total,
        "tool_calls": tool_calls_total,
        "latency_ms": round(latency_ms),
        "cost_usd": round(cost_usd, 4),
        "tool_rounds": round_idx + 1,
    }

    return {"report": report_text, "metrics": metrics}


# ── CLI ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SAP Legacy Modernization Analyzer — reads ECC config, "
        "produces S/4HANA migration delta report"
    )
    parser.add_argument(
        "--config", required=True,
        help="Path to YAML legacy configuration file"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse config and print summary without calling Claude"
    )
    args = parser.parse_args()

    # Validate API key
    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY must be set.", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = load_config(args.config)
    print(f"Loaded config: {args.config}", flush=True)

    if args.dry_run:
        print("\n--- Configuration Summary (dry run) ---\n")
        print(summarize_config(config))
        return

    # Run analysis
    import anthropic
    client = anthropic.Anthropic()
    print(f"Model: {MODEL_ID}")
    print("Analyzing...\n")

    result = analyze_config(client, config)

    # Output
    if args.format == "json":
        output_text = json.dumps(result, indent=2)
    else:
        output_text = result["report"]
        # Append metrics as a comment
        m = result["metrics"]
        output_text += (
            f"\n\n---\n\n"
            f"*Analysis run: model={m['model']}, "
            f"tokens={m['input_tokens']}in/{m['output_tokens']}out, "
            f"tool_calls={m['tool_calls']}, "
            f"latency={m['latency_ms']/1000:.1f}s, "
            f"cost=${m['cost_usd']:.4f}*\n"
        )

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"\nReport written to: {args.output}")
    else:
        print("\n" + output_text)

    # Print metrics summary
    m = result["metrics"]
    print(f"\n--- Metrics ---")
    print(f"Model: {m['model']}")
    print(f"Tokens: {m['input_tokens']} input, {m['output_tokens']} output")
    print(f"Tool calls: {m['tool_calls']} ({m['tool_rounds']} rounds)")
    print(f"Latency: {m['latency_ms']/1000:.1f}s")
    print(f"Est. cost: ${m['cost_usd']:.4f}")


if __name__ == "__main__":
    main()
