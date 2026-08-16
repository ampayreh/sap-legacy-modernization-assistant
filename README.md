# SAP Legacy Modernization Assistant

Reads SAP ECC legacy configuration patterns and maps them against S/4HANA Simplification Items, producing a modernization delta report with citations to official SAP documentation.

## What It Does

The analyzer takes a YAML file describing a legacy SAP ECC system — active modules, custom code inventory, table reads, interface landscape, output management setup — and identifies which S/4HANA Simplification Items affect it. The output is a prioritized migration delta report: what breaks, what replaces it, and the recommended remediation sequence.

```
┌──────────────────────────────────────────────────────────────┐
│  Legacy Config (YAML)                                        │
│  Modules, custom code, tables, interfaces, forms             │
└──────────────────────────┬───────────────────────────────────┘
                           │
                    analyzer.py
                           │
┌──────────────────────────▼───────────────────────────────────┐
│  Claude (Sonnet via Anthropic API)                            │
│                                                              │
│  System prompt:                                              │
│    SAP S/4HANA migration specialist role                     │
│                                                              │
│  Tool: lookup_simplification_items(query, module?)           │
│    → searches curated Simplification Item dataset            │
│    → returns ID, summary, legacy indicators, migration       │
│      action, help.sap.com URL                                │
│                                                              │
│  The model makes 5-10 tool calls per analysis, searching     │
│  by table name, module code, and feature name to find all    │
│  relevant items before generating the report.                │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│  Delta Report (Markdown or JSON)                             │
│                                                              │
│  - Executive summary + finding count by severity             │
│  - Findings by priority (critical / high / medium / low)     │
│    with specific config elements, effort estimates,          │
│    and help.sap.com citation links                           │
│  - Custom code impact assessment                             │
│  - Migration sequence recommendation                        │
│  - Risk register                                             │
└──────────────────────────────────────────────────────────────┘
```

## Quickstart

```bash
git clone https://github.com/ampayreh/sap-legacy-modernization-assistant.git
cd sap-legacy-modernization-assistant
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...

# Run on the GBI example config
python analyzer.py --config examples/gbi-legacy-config.yaml

# Write report to file
python analyzer.py --config examples/gbi-legacy-config.yaml --output report.md

# JSON output (includes metrics)
python analyzer.py --config examples/gbi-legacy-config.yaml --format json

# Dry run: parse config, print summary, no API call
python analyzer.py --config examples/gbi-legacy-config.yaml --dry-run
```

## Project Structure

```
sap-legacy-modernization-assistant/
├── analyzer.py                 # Main CLI (Claude API + tool use)
├── simplification_items.py     # Curated Simplification Item dataset (~25 items)
├── requirements.txt            # Python dependencies (anthropic, pyyaml)
├── DECISIONS.md                # Documented architectural decisions
├── examples/
│   └── gbi-legacy-config.yaml  # Example config: SAP GBI training company
└── README.md
```

## Simplification Item Dataset

The `simplification_items.py` file contains ~25 curated Simplification Items covering the major S/4HANA migration impact areas:

| Module | Area | Items |
|--------|------|:-----:|
| FI-AA | Asset Accounting (new engine, ANLC/ANLP removal) | 1 |
| FI-GL | General Ledger (ACDOCA, universal journal) | 2 |
| FI-AP/AR | Payables/Receivables (BSIK/BSAD removal) | 2 |
| CO | Controlling (COEP/COBK removal, CO-PA) | 2 |
| MM | Material Master, Inventory, Purchasing | 3 |
| SD | Output Management, Credit Management, Billing | 3 |
| PP | Production Planning, MRP Live | 2 |
| PM | Plant Maintenance | 1 |
| WM/EWM | Warehouse Management migration | 1 |
| BC | Custom Code, Data Migration | 2 |
| GTS | Global Trade Services | 1 |
| QM | Quality Management | 1 |
| FIORI | Fiori Launchpad, UX migration | 1 |
| BTP | Clean Core, extensibility model | 1 |

Each item includes:
- **ID and title** matching SAP's Simplification Item Catalog
- **Impact level** (mandatory / recommended / optional)
- **Legacy indicators** — specific table names, transactions, and configuration patterns that signal exposure
- **Migration action** — concrete steps, not generic advice
- **URL** — link to the official SAP Help Portal page

No SAP documentation text is reproduced. The summaries are written from practitioner experience; the tool cites SAP's own source by link. See [DECISIONS.md](DECISIONS.md) §1 for the full rationale.

## Example Configuration

The `examples/gbi-legacy-config.yaml` file describes a legacy SAP ECC 6.0 system based on SAP's [Global Bike Inc. (GBI)](https://community.sap.com/topics/university-alliances) training company — a fictional bicycle manufacturer used worldwide in SAP University Alliances programs.

The example exercises the analyzer across 10+ modules with realistic legacy patterns:
- Classic GL (GLT0, not new GL)
- Classic Asset Accounting (ANLC/ANLP engine)
- Classic Warehouse Management (LE-WM)
- SAPscript print forms
- No Business Partner configured
- No Material Ledger activated
- 47 custom Z-programs with zero automated test coverage
- Modifications to standard SAP code

This is a teaching configuration, not a real system. See [DECISIONS.md](DECISIONS.md) §4.

## How It Works

1. **Parse:** `analyzer.py` loads the YAML config and produces a structured summary
2. **Analyze:** Sends the summary to Claude with the `lookup_simplification_items` tool
3. **Search:** Claude makes multiple targeted tool calls — by table name (`BSEG`, `ANLC`), module code (`FI`, `MM`), feature name (`warehouse`, `asset accounting`) — to find all relevant Simplification Items
4. **Report:** Claude generates a prioritized delta report with specific references to the legacy config's custom programs, tables, and configuration, plus help.sap.com citation links for each finding

The tool-use loop is logged to stdout so you can see which searches the model makes and how many items match.

## What This Does Not Do

- **Not connected to a live SAP system.** The input is a YAML file, not an RFC/BAPI connection. In a production deployment, a preprocessing step would export system metadata (from SAP Readiness Check, Custom Code Migration Worklist, or SCMON usage data) into this format.
- **Not a complete Simplification Item catalogue.** The curated dataset covers ~25 items across 14 modules. A production deployment would need 200+ items. The architecture supports this: add entries to the Python list, or replace `search_simplification_items()` with an API call to SAP's Best Practice Explorer.
- **Not a substitute for SAP Readiness Check.** The SAP Readiness Check analyzes your actual system (transports, usage data, custom code scan) at a depth this tool cannot match from a YAML description. This tool is useful for early-phase assessment before system access is available, or as a structured conversation starter.
- **Not a migration execution tool.** The output is an assessment document, not a migration script. A qualified SAP consultant must validate findings and execute migration activities.

## Author

**Graeme Tobias Ampeire** — MSIS Candidate, UW Foster School of Business (2026)
SAP-certified Enterprise Architect | 12+ years digital transformation across Africa, Europe, and the US
