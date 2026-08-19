# Architectural Decisions

Non-obvious choices in this codebase, with rationale.

---

## 1. Citation-based corpus, not embedded text

**Chosen:** The Simplification Item dataset (`simplification_items.py`) stores
item IDs, one-line practitioner-written summaries, and `help.sap.com` URLs. The
analyzer's output cites these references by link. No SAP documentation text is
reproduced as retrievable chunks.

**Rejected:** Downloading SAP's Simplification List PDFs, chunking the text,
embedding it, and building a RAG pipeline over it.

**Why:**

1. **IP clarity.** SAP's Simplification List is proprietary documentation hosted
   publicly for customer reference. The redistribution rights are ambiguous.
   Embedding the full text as vector chunks creates a derived copy. Citing by ID
   and linking to the canonical source does not.

2. **Accuracy.** Simplification Items are dense, cross-referencing documents
   where a single paragraph may reference three table names, two transaction
   codes, and a migration cockpit. Chunk-and-retrieve over this content is
   high-recall but low-precision: the top-k results will return adjacent
   paragraphs about unrelated items that happen to share a table name. The
   curated dataset sidesteps this by using practitioner knowledge to write
   targeted summaries that match against actual configuration patterns.

3. **Maintainability.** SAP publishes a new Simplification List with each
   S/4HANA release. A RAG pipeline requires re-downloading, re-chunking, and
   re-embedding. The curated dataset requires updating individual entries — a
   targeted edit, not a pipeline re-run.

The tradeoff: the curated dataset covers ~25 items. A production deployment
would need 200+. The architecture supports this growth (add entries to the list,
or replace the search function with an API call to SAP's Best Practice Explorer),
but this repository demonstrates the pattern, not the full catalogue.

---

## 2. YAML configuration input, not ABAP code parsing

**Chosen:** The analyzer reads a structured YAML file describing the legacy
system's configuration: what modules are active, what custom code exists, what
tables are read, what interfaces are in place.

**Rejected:** Parsing raw ABAP source code or SAP transport files.

**Why:**

1. **Access.** Real SAP systems are behind corporate firewalls. ABAP source code
   is proprietary to each customer. A tool that requires raw ABAP input cannot
   be demonstrated publicly without exposing client code. A YAML configuration
   file can be constructed from a system audit without including any proprietary
   source.

2. **Signal density.** An SAP ECC system with 50 Z-programs may have 50,000
   lines of ABAP. The information the analyzer needs — which tables are read,
   which transactions are used, which exits are implemented — is 50 lines of
   structured data. Feeding 50,000 lines of ABAP into a context window to
   extract 50 lines of facts is the wrong tool for the job.

3. **Composability.** The YAML format is straightforward to generate from SAP's
   own analysis tools (Custom Code Migration Worklist, SAP Readiness Check, SCMON
   usage data). A real deployment would have a preprocessing step that exports
   system metadata into this format, not a human writing YAML by hand.

---

## 3. Tool use for Simplification Item lookup, not inline context

**Chosen:** The analyzer exposes a `lookup_simplification_items` tool via
Claude's tool-use capability. The model makes multiple targeted searches
during analysis rather than receiving the full dataset upfront.

**Rejected:** Embedding all 25 items in the system prompt.

**Why:**

1. **Scalability pattern.** 25 items fit in a system prompt. 200 do not (at
   ~500 tokens each, 200 items = 100K tokens of context). The tool-use pattern
   works at both scales without architecture changes.

2. **Selective retrieval.** The model searches by module, table name, or feature
   name and gets back only the relevant items. This produces more precise
   findings than scanning a wall of text, and the tool calls are logged for
   observability.

3. **Demonstrable integration.** The tool-use loop — send tool definitions,
   handle `tool_use` stop reason, execute the tool, return results — is a real
   implementation of the Claude tool-use pattern, not a stub. This is the same
   pattern used in the ScopingAgent orchestrator and the LMMSmartClinicAI
   formulary search.

---

## 4. GBI as the example configuration, not real client data

**Chosen:** The example configuration (`examples/gbi-legacy-config.yaml`) is
based on SAP's Global Bike Inc. (GBI) training company.

**Rejected:** Using configuration data from a real client engagement or from
institutional SAP systems.

**Why:**

1. **GBI is SAP's own public reference.** It is used worldwide in SAP University
   Alliances programs. Its structural elements (company codes US00/DE00, plants
   in Dallas and Heidelberg, bicycle manufacturing) are well-known and do not
   belong to any single institution.

2. **No client exposure.** Using real client configuration data — even
   "anonymized" — risks leaking system architecture details that could
   fingerprint the client. GBI is a teaching company; its configuration is
   designed to be shared.

3. **Realistic coverage.** GBI's training setup covers FI, CO, MM, SD, PP, PM,
   and WM — enough modules to exercise the analyzer's simplification item
   matching across the major S/4HANA impact areas. The example configuration
   adds realistic legacy patterns (classic GL, classic asset accounting, classic
   WM, SAPscript forms) that a GBI training system would exhibit if it had been
   running as an ECC production instance for 15 years.

---

## 5. Single-pass analysis, not multi-step pipeline

**Chosen:** The analyzer makes one Claude API call (with a tool-use loop) that
reads the full configuration and produces the complete report.

**Rejected:** A multi-step pipeline (as used in ScopingAgent) where separate
calls analyze each module independently and a final call synthesizes.

**Why:** The input is small (~2KB of structured YAML summarized to ~3KB of text)
and the output is a single document. The ScopingAgent pipeline is justified by
its 340KB of skill prompts and multi-step workflow; this analyzer has one task
with one input. Adding pipeline complexity for a single-document generation
would be overengineering, and the tool-use loop already provides the multi-turn
interaction needed (the model makes 5–10 tool calls to search for relevant items
before generating the report).


---

## 6. Grounding fix: the tool returning zero matches must not trigger a fallback to training-data citations

**Context:** Discovered by adversarial testing, not code review. Ran the
analyzer against a config in a module area (HR/Payroll) entirely absent from
the curated 23-item dataset. The result: the model explicitly announced it
would "supplement with expert knowledge," fabricated four plausible-looking
SAP Note numbers and `help.sap.com` citation URLs (one containing a literal
`xxxxxx` placeholder), and then stated in the report itself: **"No findings
have been fabricated or extrapolated beyond documented SAP sources."** That
claim was false — verified by comparing byte-for-byte response bodies: the
fabricated URLs, and a control URL made of pure gibberish, all returned the
identical generic SPA-shell response (`help.sap.com` serves that shell for
any path under `/docs/`, with any real/fake distinction handled client-side
by JavaScript, not HTTP status). A curl `200` on this domain proves nothing
about whether the specific page exists.

**Why this matters more than a typical hallucination:** this repo's entire
value proposition — stated in its own README and in `simplification_items.py`'s
docstring — is "citations to official SAP documentation," specifically
*because* redistributing SAP's proprietary Simplification List text was
ruled out (see Decision 1). Citation-by-link is the whole grounding
mechanism. A fabricated citation defeats that mechanism silently, and
`help.sap.com`'s SPA routing means the fabrication cannot be caught by any
automated link-check — a fabricated citation looks exactly as "valid" (HTTP
200) as a real one.

**Fix:** Added an explicit grounding rule to `SYSTEM_PROMPT`: every
Simplification Item ID, SAP Note number, and citation URL must come verbatim
from a `lookup_simplification_items` tool result — never invented, never
recalled from training data, never "supplemented" even when the model is
confident it's accurate, because SAP Note numbers and doc URLs cannot be
verified from memory and a fabricated citation in a compliance-relevant
report is worse than an honest gap. Added a required "Dataset Coverage Gaps"
report section: when searches return zero results for a configuration area,
the report must name the gap and recommend consulting SAP's official
catalogue or a qualified consultant — not generate a finding.

**Verified:** re-ran the same adversarial HR/Payroll config after the fix.
Every citation URL in the output was cross-checked against the curated
dataset's literal strings — 100% traced to real dataset entries. The model
still searched exhaustively (27 tool calls, casting a wide net across
adjacent modules before conceding) but, on finding nothing, produced an
honest "Dataset Coverage Gaps" section naming HCM/Payroll, PA-infotype
access, and the Oracle→HANA/AIX platform gap explicitly, instead of
fabricating findings for them.

**Also corrected:** an earlier claim in this audit that "all 23 curated
dataset URLs resolve" (verified via HTTP status) is not real verification,
for the same SPA-routing reason above — it only confirms the URLs don't hard
404, not that they're the correct or even an existing specific page. That
claim has been walked back rather than left standing uncorrected.
