"""
SAP S/4HANA Simplification Item Reference Dataset

Each entry is a short factual note with a citation link to the official
SAP Help Portal (help.sap.com). No SAP proprietary text is reproduced —
only item IDs, one-line impact summaries written from practitioner
experience, and the canonical URL.

These items were curated from the publicly available Simplification Item
Catalog at help.sap.com/docs/SAP_S4HANA_ON-PREMISE. The catalog is
SAP's own public documentation for S/4HANA migration planning.
"""

SIMPLIFICATION_ITEMS = [
    # ── Financial Accounting (FI) ─────────────────────────────
    {
        "id": "FI-AA-001",
        "title": "New Asset Accounting (Migration to New Asset Accounting)",
        "module": "FI-AA",
        "area": "Asset Accounting",
        "impact": "mandatory",
        "summary": (
            "Classic Asset Accounting (ANLC/ANLP tables) is removed in S/4HANA. "
            "All fixed-asset data must migrate to the new Asset Accounting engine "
            "(ACDOCA-based). Parallel valuation areas that posted to separate "
            "ledgers now post to the universal journal. Custom reports reading "
            "ANLC/ANLP break and must be rewritten against ACDOCA."
        ),
        "legacy_indicators": [
            "ANLC table reads in custom reports",
            "ANLP table reads in custom reports",
            "Transaction AS91 (legacy data transfer)",
            "Parallel depreciation areas posting to APC/depreciation accounts only",
        ],
        "migration_action": "Run New Asset Accounting migration cockpit (transaction FINS_MIG_STATUS). Remap all custom reports from ANLC/ANLP to ACDOCA.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/asset-accounting",
    },
    {
        "id": "FI-GL-001",
        "title": "Universal Journal (ACDOCA) Replaces Classic GL Tables",
        "module": "FI-GL",
        "area": "General Ledger",
        "impact": "mandatory",
        "summary": (
            "The universal journal table ACDOCA replaces separate FI line item "
            "tables (BSEG, BSID, BSAD, BSIK, BSAK) and CO line item tables "
            "(COEP, COBK). All financial and controlling postings land in a "
            "single table. Custom code reading the classic tables must be "
            "redirected to ACDOCA or compatibility views (BSEG_ADD, etc.)."
        ),
        "legacy_indicators": [
            "Direct SELECT on BSEG, BSID, BSAD, BSIK, BSAK",
            "Direct SELECT on COEP, COBK",
            "Classic GL (GLT0) instead of new GL",
            "Custom totals tables replicated from BSEG",
        ],
        "migration_action": "Enable new GL if not already active. Redirect custom ABAP to ACDOCA or use CDS views. Run FAGLFLEXT migration if on classic totals.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/general-ledger-accounting",
    },
    {
        "id": "FI-GL-002",
        "title": "Business Partner Replaces Vendor/Customer Master",
        "module": "FI-GL",
        "area": "Master Data",
        "impact": "mandatory",
        "summary": (
            "Separate vendor master (LFA1/LFB1) and customer master (KNA1/KNB1) "
            "are replaced by the Business Partner (BP) model. Transactions XK01/XD01 "
            "(create vendor/customer) are replaced by BP transaction. All downstream "
            "processes referencing vendor/customer master directly must use the BP "
            "interface. CVI (Customer-Vendor Integration) synchronization must be "
            "configured before migration."
        ),
        "legacy_indicators": [
            "Transaction XK01/XK02/XK03 (vendor master)",
            "Transaction XD01/XD02/XD03 (customer master)",
            "Direct reads on LFA1, LFB1, KNA1, KNB1",
            "Custom vendor/customer creation programs",
        ],
        "migration_action": "Configure CVI synchronization. Run BP migration pre-check. Convert custom master data programs to BP API.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/business-partner",
    },
    {
        "id": "FI-AP-001",
        "title": "Accounts Payable Changes (BSIK/BSAK Removal)",
        "module": "FI-AP",
        "area": "Accounts Payable",
        "impact": "mandatory",
        "summary": (
            "Open/cleared AP line item tables BSIK and BSAK are removed. "
            "All AP line items are stored in ACDOCA. AP aging reports, payment "
            "proposal customizations, and vendor balance displays reading these "
            "tables directly must be redirected."
        ),
        "legacy_indicators": [
            "Custom AP aging reports reading BSIK/BSAK",
            "Payment proposal programs with direct table access",
            "Custom vendor balance reports",
        ],
        "migration_action": "Redirect to ACDOCA or use compatibility views. Test all AP reporting and payment proposal customizations.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/accounts-payable",
    },
    {
        "id": "FI-AR-001",
        "title": "Accounts Receivable Changes (BSID/BSAD Removal)",
        "module": "FI-AR",
        "area": "Accounts Receivable",
        "impact": "mandatory",
        "summary": (
            "Open/cleared AR line item tables BSID and BSAD are removed. "
            "Customer credit management, dunning customizations, and AR aging "
            "reports reading these tables must be redirected to ACDOCA."
        ),
        "legacy_indicators": [
            "Custom AR aging reports reading BSID/BSAD",
            "Credit management programs with direct table access",
            "Custom dunning reports reading line item tables",
        ],
        "migration_action": "Redirect to ACDOCA or compatibility views. Evaluate migration to SAP Credit Management (FIN-FSCM-CR).",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/accounts-receivable",
    },
    # ── Controlling (CO) ──────────────────────────────────────
    {
        "id": "CO-001",
        "title": "CO Line Items in Universal Journal",
        "module": "CO",
        "area": "Controlling",
        "impact": "mandatory",
        "summary": (
            "CO line item tables (COEP, COBK, COSP, COSS) are replaced by "
            "ACDOCA. CO-FI reconciliation is eliminated because both live in "
            "the same table. Custom CO reports and allocations reading these "
            "tables must be redirected."
        ),
        "legacy_indicators": [
            "Direct SELECT on COEP, COBK, COSP, COSS",
            "Custom cost center reports reading totals tables",
            "Manual CO-FI reconciliation processes",
            "Custom allocation cycle reports",
        ],
        "migration_action": "Redirect custom reports to ACDOCA. Remove CO-FI reconciliation jobs. Test allocation cycles end-to-end.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/controlling",
    },
    {
        "id": "CO-PA-001",
        "title": "Profitability Analysis Simplification",
        "module": "CO-PA",
        "area": "Profitability Analysis",
        "impact": "recommended",
        "summary": (
            "Costing-based CO-PA (tables CE1xxxx, CE2xxxx, CE3xxxx, CE4xxxx) "
            "can be replaced by account-based CO-PA stored in ACDOCA. This "
            "eliminates the separate CO-PA data flow and enables real-time "
            "profitability reporting. Existing costing-based operating concerns "
            "and value fields require redesign."
        ),
        "legacy_indicators": [
            "Costing-based CO-PA operating concern active",
            "Custom value fields in CO-PA",
            "Reports reading CE1xxxx/CE2xxxx tables",
            "PA transfer structures and assignment rules",
        ],
        "migration_action": "Evaluate migration to account-based CO-PA. Redesign value fields as GL accounts or characteristics. Test profitability reports.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/profitability-analysis",
    },
    # ── Materials Management (MM) ─────────────────────────────
    {
        "id": "MM-001",
        "title": "Material Master Simplification",
        "module": "MM",
        "area": "Material Master",
        "impact": "mandatory",
        "summary": (
            "Material number length extended from 18 to 40 characters. "
            "Material type simplification merges some standard types. "
            "Custom material types and material number generation logic "
            "must be reviewed. MARA/MARC/MARD tables remain but some "
            "fields are deprecated."
        ),
        "legacy_indicators": [
            "Material number length assumptions in custom code (CHAR18)",
            "Custom material types based on deprecated standard types",
            "Custom number range logic for material numbers",
            "Hard-coded material number length in interfaces",
        ],
        "migration_action": "Run custom code analysis for material number length. Review custom material types against simplified list. Update interfaces.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/material-master",
    },
    {
        "id": "MM-IM-001",
        "title": "Inventory Management Simplification",
        "module": "MM-IM",
        "area": "Inventory Management",
        "impact": "mandatory",
        "summary": (
            "Material document tables MKPF/MSEG receive structural changes. "
            "The material ledger becomes mandatory (even if not using actual "
            "costing). Stock value reporting shifts from MBEW to ACDOCA for "
            "financial values. Custom inventory reports must be reviewed."
        ),
        "legacy_indicators": [
            "Custom inventory reports reading MBEW for stock values",
            "Material ledger not activated",
            "Custom goods movement programs",
            "Reports combining MKPF/MSEG with financial tables",
        ],
        "migration_action": "Activate material ledger. Redirect stock value reporting to ACDOCA. Test all goods movement scenarios.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/inventory-management",
    },
    {
        "id": "MM-PUR-001",
        "title": "Purchasing Document Changes",
        "module": "MM-PUR",
        "area": "Purchasing",
        "impact": "optional",
        "summary": (
            "Purchase order and contract document flow tables receive minor "
            "structural changes. Vendor evaluation shifts to Business Partner "
            "model (see FI-GL-002). Custom procurement workflows using classic "
            "vendor master fields require updates."
        ),
        "legacy_indicators": [
            "Custom procurement reports using LFA1 vendor fields",
            "Vendor evaluation programs using classic master",
            "ME21N enhancements reading vendor-specific fields",
        ],
        "migration_action": "Update procurement customizations to use BP fields. Test vendor evaluation and procurement workflows.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/purchasing",
    },
    # ── Sales and Distribution (SD) ───────────────────────────
    {
        "id": "SD-001",
        "title": "Output Management Migration",
        "module": "SD",
        "area": "Output Management",
        "impact": "recommended",
        "summary": (
            "Classic output determination (NACE/NAST) can be replaced by "
            "BRF+ (Business Rule Framework plus) based output management. "
            "Existing NACE condition records, SAPscript forms, and SmartForms "
            "continue to work but are on maintenance path. Adobe Forms with "
            "BRF+ output management is the strategic direction."
        ),
        "legacy_indicators": [
            "NACE output condition records for sales documents",
            "SAPscript print programs (RSTXLPDF, etc.)",
            "Custom SmartForms for invoices/delivery notes",
            "Output type customization in SPRO",
        ],
        "migration_action": "Evaluate migration timeline for output management. Convert SAPscript to Adobe Forms. Configure BRF+ rules for critical output types.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/output-management",
    },
    {
        "id": "SD-CM-001",
        "title": "Credit Management Migration",
        "module": "SD-CM",
        "area": "Credit Management",
        "impact": "recommended",
        "summary": (
            "Classic SD credit management (VKM1/VKM3) can be replaced by "
            "SAP Credit Management (FIN-FSCM-CR), which provides real-time "
            "credit exposure calculation and integration with the universal "
            "journal. Classic credit management continues to work but is not "
            "enhanced."
        ),
        "legacy_indicators": [
            "VKM1/VKM3 credit management active",
            "Custom credit check user exits (LVKMPFZ1)",
            "Credit limit maintenance via FD32",
            "Custom credit exposure reports",
        ],
        "migration_action": "Evaluate migration to FIN-FSCM-CR. Map existing credit rules to new framework. Test credit check integration with order processing.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/credit-management",
    },
    {
        "id": "SD-BIL-001",
        "title": "Billing Document Changes",
        "module": "SD-BIL",
        "area": "Billing",
        "impact": "mandatory",
        "summary": (
            "Billing document accounting integration changes with the universal "
            "journal. Revenue recognition moves to ACDOCA. Custom billing "
            "programs that post directly to FI tables (BKPF/BSEG) must use "
            "the new posting interface."
        ),
        "legacy_indicators": [
            "Custom billing programs posting to BKPF/BSEG",
            "Revenue recognition customizations reading classic GL",
            "Custom invoice split logic",
        ],
        "migration_action": "Update custom billing programs to new posting API. Test revenue recognition end-to-end. Verify invoice output with new accounting entries.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/billing",
    },
    # ── Production Planning (PP) ──────────────────────────────
    {
        "id": "PP-001",
        "title": "Production Order Changes",
        "module": "PP",
        "area": "Production Planning",
        "impact": "optional",
        "summary": (
            "Production order confirmations integrate with ACDOCA for cost "
            "posting. The material ledger (now mandatory) affects actual "
            "costing of production orders. Custom production reporting reading "
            "AUFK/AFKO/AFPO tables is largely unaffected, but cost-related "
            "fields may shift."
        ),
        "legacy_indicators": [
            "Custom production cost reports reading COBK/COEP",
            "Actual costing not activated",
            "Custom production order status reports",
        ],
        "migration_action": "Activate actual costing in material ledger. Redirect cost reports from COEP to ACDOCA. Test production order lifecycle.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/production",
    },
    {
        "id": "PP-MRP-001",
        "title": "MRP and Demand Management Changes",
        "module": "PP-MRP",
        "area": "MRP",
        "impact": "optional",
        "summary": (
            "MRP Live (transaction MD01N) replaces classic MRP (MD01/MD02) as "
            "the strategic direction. MRP Live runs on HANA-optimized logic "
            "with significantly faster execution. Classic MRP continues to work "
            "but does not benefit from HANA optimization."
        ),
        "legacy_indicators": [
            "MD01/MD02 used for MRP runs",
            "Custom MRP user exits (EXIT_SAPLMD01_*)",
            "Custom planned order processing logic",
        ],
        "migration_action": "Evaluate MRP Live adoption. Test custom MRP exits with MRP Live. Compare planning results between classic and MRP Live.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/mrp",
    },
    # ── Plant Maintenance (PM) ────────────────────────────────
    {
        "id": "PM-001",
        "title": "Maintenance Order and Notification Changes",
        "module": "PM",
        "area": "Plant Maintenance",
        "impact": "optional",
        "summary": (
            "Maintenance order cost integration moves to ACDOCA. Equipment "
            "and functional location master data is largely unchanged. Custom "
            "maintenance reports reading cost tables must be redirected."
        ),
        "legacy_indicators": [
            "Custom maintenance cost reports reading COEP",
            "Custom notification workflows",
            "Equipment master enhancements",
        ],
        "migration_action": "Redirect cost reports to ACDOCA. Test maintenance order lifecycle including cost settlement.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/plant-maintenance",
    },
    # ── Warehouse Management ──────────────────────────────────
    {
        "id": "WM-001",
        "title": "Warehouse Management to EWM Migration",
        "module": "WM/EWM",
        "area": "Warehouse Management",
        "impact": "mandatory",
        "summary": (
            "Classic Warehouse Management (WM, LE-WM) is removed in S/4HANA "
            "2025 and later. It must be replaced by Embedded EWM (Extended "
            "Warehouse Management) or decentralized EWM. Stock management, "
            "transfer orders, and warehouse structure must be migrated. This "
            "is one of the most complex simplification items for warehouse- "
            "intensive companies."
        ),
        "legacy_indicators": [
            "LE-WM active (warehouse management)",
            "Transfer orders (LT01/LT02)",
            "Warehouse structure configuration (LS01-LS04)",
            "Custom RF (radio frequency) programs",
            "Custom WM interfaces for warehouse automation",
        ],
        "migration_action": "Evaluate embedded vs. decentralized EWM. Run EWM migration cockpit. Redesign warehouse structure. Rewrite RF programs for EWM.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/warehouse-management",
    },
    # ── Basis / Cross-Application ─────────────────────────────
    {
        "id": "BC-001",
        "title": "Custom Code Adaptation for S/4HANA",
        "module": "BC",
        "area": "Basis / Custom Code",
        "impact": "mandatory",
        "summary": (
            "S/4HANA removes or replaces ~340 database tables. All custom ABAP "
            "code (reports, enhancements, interfaces, forms) must be scanned "
            "using the Custom Code Migration Worklist (transaction SYCM or the "
            "SAP Readiness Check). Code that reads removed tables, uses obsolete "
            "function modules, or depends on deprecated data models must be "
            "adapted before migration."
        ),
        "legacy_indicators": [
            "Large custom ABAP codebase (Z* programs, Y* includes)",
            "Custom reports reading any table listed in Simplification Items",
            "Obsolete function module calls",
            "Custom code not covered by automated testing",
        ],
        "migration_action": "Run Custom Code Migration Worklist or SAP Readiness Check. Prioritize by usage frequency. Adapt, test, and transport in waves.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/custom-code-migration",
    },
    {
        "id": "BC-002",
        "title": "Data Migration and Sizing",
        "module": "BC",
        "area": "Basis / Data Migration",
        "impact": "mandatory",
        "summary": (
            "ACDOCA consolidates data from multiple source tables, but the "
            "total data footprint may increase during migration due to "
            "denormalization. HANA column-store compression typically reduces "
            "the final footprint, but peak migration requires headroom. "
            "Historical data archiving should be evaluated before migration."
        ),
        "legacy_indicators": [
            "Large BSEG table (>100M records)",
            "No data archiving strategy",
            "Multiple fiscal year variants",
            "High volume of CO postings",
        ],
        "migration_action": "Run sizing report. Evaluate data archiving for historical periods. Plan migration downtime based on data volume estimates.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/data-management",
    },
    # ── Global Trade Services ─────────────────────────────────
    {
        "id": "GTS-001",
        "title": "Global Trade Services Integration Changes",
        "module": "GTS",
        "area": "Trade Compliance",
        "impact": "optional",
        "summary": (
            "SAP GTS integration with S/4HANA uses the same RFC-based "
            "architecture but benefits from the Business Partner model for "
            "sanctioned party screening. Companies using embedded trade "
            "compliance may evaluate migration to standalone GTS or SAP "
            "Global Trade Services, edition for SAP HANA."
        ),
        "legacy_indicators": [
            "Embedded trade compliance (LE-SLL)",
            "Custom screening programs using vendor/customer master",
            "Export control classification in material master",
        ],
        "migration_action": "Update screening programs to use BP model. Evaluate standalone GTS if not already deployed. Test compliance document flow.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/global-trade",
    },
    # ── Quality Management (QM) ───────────────────────────────
    {
        "id": "QM-001",
        "title": "Quality Management Integration Changes",
        "module": "QM",
        "area": "Quality Management",
        "impact": "optional",
        "summary": (
            "QM inspection lots and quality notifications are largely unchanged "
            "in S/4HANA. The primary impact is indirect: quality cost postings "
            "move to ACDOCA, and vendor/customer references in quality records "
            "shift to the Business Partner model."
        ),
        "legacy_indicators": [
            "Quality cost reports reading COEP",
            "Vendor quality scoring using LFA1 fields",
            "Custom QM-PP integration reports",
        ],
        "migration_action": "Update cost reports to ACDOCA. Update vendor references to BP. Test inspection lot processing end-to-end.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/quality-management",
    },
    # ── SAP Fiori / UX ────────────────────────────────────────
    {
        "id": "FIORI-001",
        "title": "Fiori Launchpad and Transaction Migration",
        "module": "FIORI",
        "area": "User Experience",
        "impact": "recommended",
        "summary": (
            "S/4HANA's primary user interface is SAP Fiori. While SAP GUI "
            "transactions remain functional, SAP's strategic direction is "
            "Fiori apps for all new development. Organizations should plan a "
            "phased Fiori rollout starting with high-frequency transactions "
            "(purchase orders, sales orders, journal entries, approvals)."
        ),
        "legacy_indicators": [
            "100% SAP GUI usage",
            "No Fiori launchpad deployed",
            "Custom SAP GUI transactions with dynpro logic",
            "Custom BSP applications for web access",
        ],
        "migration_action": "Deploy Fiori launchpad. Identify top 20 transactions by usage frequency. Activate corresponding Fiori apps. Plan custom app development for remaining gaps.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/fiori",
    },
    # ── BTP Integration ───────────────────────────────────────
    {
        "id": "BTP-001",
        "title": "Clean Core and BTP Extension Model",
        "module": "BTP",
        "area": "Extensibility",
        "impact": "recommended",
        "summary": (
            "S/4HANA's Clean Core principle moves custom extensions from the "
            "ABAP stack to SAP BTP (Business Technology Platform). Side-by-side "
            "extensions on BTP using CAP (Cloud Application Programming Model) "
            "replace in-system modifications. Organizations with heavy "
            "customization should evaluate which extensions to refactor to BTP "
            "vs. keep as key-user extensibility."
        ),
        "legacy_indicators": [
            "Modifications to SAP standard code (SMOD/CMOD)",
            "Custom ABAP programs that modify standard behavior",
            "Heavy use of implicit enhancements",
            "Custom interfaces built on RFC/BAPI",
        ],
        "migration_action": "Inventory all modifications. Classify as keep/refactor/retire. Design BTP extension architecture for refactored items. Implement API-based integration.",
        "url": "https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/latest/clean-core",
    },
]


def search_simplification_items(query: str, module: str = None) -> list[dict]:
    """Search the Simplification Item dataset by keyword and/or module.

    Args:
        query: Free-text search term (matched against id, title, summary,
               area, and legacy_indicators).
        module: Optional module code filter (e.g. "FI-AA", "MM", "CO").
               Matches on prefix, so "FI" matches "FI-AA", "FI-GL", etc.

    Returns:
        List of matching Simplification Items (full records).
    """
    results = []
    query_lower = query.lower() if query else ""

    for item in SIMPLIFICATION_ITEMS:
        # Module filter
        if module:
            item_mod = item["module"].upper()
            filter_mod = module.upper()
            # Match on module hierarchy boundary: "FI" matches "FI", "FI-AA",
            # "FI-GL" but not "FIORI". The separator is "-".
            if item_mod != filter_mod and not item_mod.startswith(filter_mod + "-"):
                continue

        # Text search across multiple fields
        if query_lower:
            searchable = " ".join([
                item["id"],
                item["title"],
                item["summary"],
                item["area"],
                " ".join(item["legacy_indicators"]),
                item["migration_action"],
            ]).lower()

            if query_lower not in searchable:
                continue

        results.append(item)

    return results


# Expose as a Claude tool definition
SIMPLIFICATION_ITEM_TOOL = {
    "name": "lookup_simplification_items",
    "description": (
        "Search the SAP S/4HANA Simplification Item reference dataset. "
        "Each item describes a change between SAP ECC and S/4HANA: what "
        "is removed, what replaces it, and what legacy patterns indicate "
        "exposure. Use this to find relevant simplification items for a "
        "given legacy configuration pattern."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Search term. Matches against item ID, title, summary, "
                    "area, legacy indicators, and migration actions. Examples: "
                    "'BSEG', 'asset accounting', 'vendor master', 'warehouse'."
                ),
            },
            "module": {
                "type": "string",
                "description": (
                    "Optional SAP module code filter. Matches on prefix: "
                    "'FI' matches FI-AA, FI-GL, FI-AP, FI-AR. "
                    "'MM' matches MM, MM-IM, MM-PUR. "
                    "Omit to search all modules."
                ),
            },
        },
        "required": ["query"],
    },
}
