# ModernizeIQ: Refined Features, Requirements & Ecosystem Improvement Roadmap

> **Ecosystem Vision Statement**: *"Not a box, but an ecosystem."*  
> ModernizeIQ is an enterprise-grade mainframe-to-distributed workload modernization assessment platform. It enables enterprise architects, cloud consultants, and engineering leads to evaluate the complexity, cloud readiness, inter-dependencies, and risks involved in transitioning legacy IBM z/OS workloads toward modern distributed architectures—specifically comparing **Red Hat OpenShift Container Platform (OCP)** against **Linux Virtual Machine (VM) Rehosting**.

---

## 1. Executive Summary & Industry Context

In modern enterprise IT, mainframe migrations fail primarily due to three systemic blind spots:
1. **Hidden Coupling & Shared Data Gravity**: Overlooked shared copybooks, uncoordinated VSAM record-level locks, and multi-resource Two-Phase Commits (2PC) that crash distributed microservices.
2. **Binary Biases ("Containerize Everything" vs "Rehost Everything")**: Blindly attempting to containerize conversational CICS programs with stateful terminal locks, or unnecessarily rehosting stateless computational batch jobs that could run cheaply as ephemeral Kubernetes Jobs.
3. **Black-Box Legacy Knowledge**: Lack of semantic understanding of what business logic actually resides inside 50-year-old COBOL programs.

ModernizeIQ solves these challenges by combining **deep static AST analysis**, **384-dimensional dense semantic embeddings (`all-MiniLM-L6-v2`)**, an **explainable multi-criteria decision engine**, and **interactive HTML5 visual analytics**.

---

## 2. Refined Requirements Specification

### 2.1 Functional Requirements (FR)

| ID | Capability Area | Requirement Description | Verification Metric / Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **FR-1** | **Multi-Dialect Artifact Ingestion** | Ingest and parse diverse mainframe artifacts: COBOL-85/Enterprise COBOL, JCL jobs/procs, BMS 3270 maps, DB2 DDL schemas, VSAM cluster definitions, and RACF/SAF security definitions. | Parsers process fixed/variable length punch-card formats, ignore sequence margins, and extract 100% of declared programs, copybooks, steps, tables, and files without crashing. |
| **FR-2** | **8-Dimensional Architectural Scoring** | Score portfolios across 8 standardized architectural vectors: Business Logic Modularity, Program Coupling, Data Persistence, Online UI/CICS, Batch JCL, Security/Identity, Transactional Integrity, and Operational NFRs. | Normalized 0–100 dimensional ratings accompanied by quantitative defect metrics (e.g., Cyclomatic Complexity > 20, ALTER count, dead paragraphs). |
| **FR-3** | **Twelve-Factor Cloud Native Audit** | Benchmark mainframe application behavior against the 12-Factor App methodology for container fitness. | Explicit compliance flags for Stateless Processes (VI), Config in Environment (III), Port Binding (VII), Concurrency (VIII), and Disposability (IX). |
| **FR-4** | **Dense Semantic Embeddings & Bounded Contexts** | Ingest procedure division paragraph semantics into `all-MiniLM-L6-v2` dense vectors (384-dim) and apply dimensionality reduction (PCA/t-SNE) for visual domain clustering. | Generates 2D coordinates `(x, y)` and automatically partitions monolithic codebases into coherent microservice domain candidates. |
| **FR-5** | **Platform Decision Engine (OCP vs. VM)** | Evaluate hard blockers and trade-offs to recommend Red Hat OpenShift (OCP), Linux VM Rehosting, or Hybrid Coexistence with clear logical explanations. | Deterministic scoring matrix balancing statefulness, locking, security exits, and latency SLAs; outputs formal Michael Nygard-format ADRs. |
| **FR-6** | **Dependency Graph & Blast Radius Simulation** | Construct an enterprise knowledge graph capturing all directional relationships (CALL, EXECUTES, READS, WRITES, BINDS, AUTHORIZES). | Interactive graph computing upstream and downstream blast radius percentage and immediate impact lists upon selecting any node. |
| **FR-7** | **Migration Wave Planning & Sequencing** | Automatically group applications and programs into phased migration waves based on dependency depth, cycle breaking, and data gravity. | Produces a sequenced cutover plan (Wave 1: Foundation/Decoupled, Wave 2: Core Domain, Wave 3: Stateful Monoliths) with risk burndown metrics. |
| **FR-8** | **Interactive Visual Reporting** | Deliver standalone, self-contained HTML5 single-page visualization dashboards and downloadable executive dossiers. | 100% offline-capable, responsive dashboard featuring D3/Canvas physics graphs, Chart.js radar charts, and interactive simulators. |
| **FR-9** | **RESTful API & Integration Layer** | Expose all assessment, graph query, and decision engine capabilities via high-performance OpenAPI-documented REST endpoints. | FastAPI backend supporting programmatic portfolio submission and JSON payload consumption by external CI/CD pipelines. |
| **FR-10** | **CLI Tooling & Developer Ergonomics** | Provide an intuitive CLI (`modernizeiq`) for local terminal execution, batch processing, and live dashboard serving. | Commands: `analyze`, `serve`, `export-adr`, `batch-evaluate` with clear console outputs and exit status codes. |

---

### 2.2 Non-Functional Requirements (NFR)

| ID | Dimension | Target Specification |
| :--- | :--- | :--- |
| **NFR-1** | **Scan Performance & Scalability** | Capable of parsing and analyzing > 25,000 Lines of Code (LOC) per second on standard developer workstations (8-core CPU, 16GB RAM). |
| **NFR-2** | **Air-Gapped & Offline Security** | Zero external API calls required for core parsing, analysis, embedding projection, or dashboard rendering. Critical for financial/defense mainframe assets. |
| **NFR-3** | **Zero Data Exfiltration** | Sensitive customer business logic and proprietary DDL remain strictly within the local execution perimeter. |
| **NFR-4** | **Deterministic & Explainable Outputs** | Every recommendation, penalty, and score must be traceable to explicit lines of code, catalog entries, or configuration parameters. |
| **NFR-5** | **Extensibility & Modularity** | Clean plugin architecture allowing new parsers (e.g. PL/I, Assembler, IMS DB) and custom enterprise scoring rules without touching core engines. |
| **NFR-6** | **Zero-Dependency Visual Artifacts** | Output dashboards must be single-file HTML5 capable of opening directly in any modern browser without requiring node.js, web servers, or npm installs. |

---

## 3. Feature Refinement Analysis: Current State vs. Target State

| Ecosystem Component | Current ModernizeIQ Implementation | Refined Target State (Enterprise Gold Standard) | Priority |
| :--- | :--- | :--- | :---: |
| **COBOL AST Parser** | Regex-based AST identifying `DIVISION`, `PARAGRAPH`, `EXEC CICS`, `EXEC SQL`, `CALL`, `COPY`, `ALTER`. | Full grammar parsing tracking variable-level data flow, condition branching, and dynamic call targets (`CALL WS-PROG-NAME`). | High |
| **JCL Parser** | Extracts `EXEC PGM`, `DD DSN`, `DISP`, `COND`, and utility programs (`IDCAMS`, `SORT`). | Parses nested `PROC` expansion, symbolic parameter substitution (`&ENV`), and catalog-managed GDG base definitions. | Medium |
| **Semantic AI Engine** | 384-dimensional dense semantic embedding engine using `all-MiniLM-L6-v2` with deterministic PCA 2D projection and keyword-based cluster labeling. | Dynamic cluster naming via automated TF-IDF keyword extraction or local LLM summarization; auto-generates draft OpenAPI/REST DTO interfaces. | High |
| **Platform Decision Engine** | Rule-based scoring comparing OCP vs Linux VM with hard blocker detection and Nygard ADR generation. | Adds financial TCO/FinOps modeling (MIPS pricing vs cloud vCPU/RAM), migration complexity person-month estimation, and carbon footprint reduction estimates. | High |
| **Dependency & Graph Engine** | In-memory graph constructing `GraphNode` and `GraphEdge` with blast radius calculation. | Topological wave planning algorithm with Tarjan's cycle-breaking heuristic to output executable Phase 1/2/3 migration waves. | High |
| **Visual Dashboard** | Interactive HTML5 Canvas physics graph, Chart.js radar & scatter charts, interactive blast radius selector. | Node search/filter by risk, dark/light theme toggle, interactive migration Gantt chart, and one-click PDF/CSV export. | Medium |
| **API & CLI** | FastAPI backend with `/api/analyze` and CLI commands for `analyze` and `serve`. | Multi-portfolio comparison endpoint, asynchronous background task queuing for large repos, and webhook notifications on scan completion. | Low |

---

## 4. Deep Gap Analysis: What Needs Improvement

### 4.1 Parser & AST Depth
- **Dynamic Call Target Resolution**: COBOL programs often use `CALL WS-SUBPROGRAM` where the program name is dynamically assigned at runtime.
  - *Improvement*: Implement static string propagation and data-flow tracking within `WORKING-STORAGE` to resolve dynamic subprogram names, or support ingesting CICS transaction trace logs (`SMF 110`) to resolve dynamic targets.
- **Nested JCL Catalog Procedures (`PROCs`)**: Real-world mainframe JCL frequently references cataloged procedures (`EXEC PROC=MYPROC`) with parameter overrides.
  - *Improvement*: Add a PROC resolution repository so steps within PROCs are expanded into the execution tree.
- **Copybook Data Lineage & Variable-Level Blast Radius**: Current coupling analysis tracks copybook usage at the program level.
  - *Improvement*: Extract individual 01-level and 05-level record fields (`ACCOUNT-BALANCE`, `CREDIT-LIMIT`) to show column-level data lineage across programs.
- **Support for Secondary Legacy Dialects**:
  - *Improvement*: Add parser stubs for PL/I, Assembler (BAL/HLASM), Natural/Adabas, and IMS DB/DC hierarchies.

### 4.2 Architectural Scoring & Heuristics
- **Configurable Scoring Weights**: Currently, dimensional weights are hardcoded.
  - *Improvement*: Introduce configurable YAML/JSON profiles (e.g., `profiles/fintech_high_throughput.yaml`, `profiles/batch_heavy_reporting.yaml`) allowing architects to adjust penalties for specific industries.
- **Halstead Complexity & Maintainability Index (MI)**:
  - *Improvement*: Augment McCabe's Cyclomatic Complexity with Halstead volume, operator/operand counts, and the standard SEI Maintainability Index formula ($171 - 5.2 \times \ln(V) - 0.23 \times G - 16.2 \times \ln(\text{LOC})$).
- **Code Smell Catalog**:
  - *Improvement*: Specifically flag "God Paragraphs" (> 500 LOC in a single paragraph), "Dead Code Islands" (unreachable paragraphs with no `PERFORM` or `GO TO`), and "Spaghetti Branching" (excessive backward `GO TO` jumps).

### 4.3 Semantic AI Domain Decomposition (`all-MiniLM-L6-v2`)
- **Automated Cluster Title Synthesis**:
  - *Improvement*: Instead of static heuristic names, extract the top TF-IDF keywords or n-grams from each cluster's member programs to automatically generate business domain titles (e.g., *"Foreign Exchange Clearing Domain"*, *"Fee Calculation Subsystem"*).
- **Draft OpenAPI Contract Generator**:
  - *Improvement*: For each identified microservice domain cluster, automatically inspect CICS `DFHCOMMAREA` or linkage sections and generate a draft `openapi.yaml` REST spec or Java Quarkus DTO class.

### 4.4 Target Platform Decision Engine & Migration Economics
- **MIPS to vCPU Sizing & FinOps TCO Calculator**:
  - *Improvement*: Add an economic model calculating current mainframe operational cost (e.g., $1,800–$4,500 per MIPS/year) versus projected cloud hosting costs on AWS/Azure/GCP (EC2 vs OpenShift ROSA/ARO worker nodes).
- **Automated Migration Wave Sorter**:
  - *Improvement*: Implement a topological dependency sort that automatically groups all portfolio artifacts into:
    - **Wave 1 (Quick Wins / Decoupled)**: Zero inbound dependencies, purely relational data, stateless logic.
    - **Wave 2 (Core Business Engines)**: Intermediate coupling, moderate batch orchestration.
    - **Wave 3 (Anchor Monoliths)**: Heavy shared VSAM locks, complex 2PC, custom security exits.

### 4.5 Visual Dashboard & User Experience (UX/UI)
- **Graph Filter and Search Controls**:
  - *Improvement*: In the Canvas physics graph, add a live text search box to instantly focus on any node, plus filter toggles to show/hide specific artifact types (e.g. toggle off Copybooks or DB2 Tables to view only the program-to-program call graph).
- **Side-by-Side Modernization Code Preview**:
  - *Improvement*: Add a tab in the dashboard that displays a legacy COBOL paragraph side-by-side with a modern refactored target equivalent (e.g., Java Quarkus, Python FastAPI, or Go microservice).
- **Export Capabilities**:
  - *Improvement*: Enable one-click client-side export of the full assessment dossier to PDF and CSV, as well as exporting migration tasks directly into Jira-compatible CSV format.

### 4.6 Enterprise Integration & Production Hardening
- **CI/CD Quality Gate Action**:
  - *Improvement*: Provide a GitHub Action / GitLab CI runner that fails builds if a mainframe modernization PR introduces new container anti-patterns (e.g. new `ALTER` statements or new conversational CICS state).
- **Containerized Air-Gapped Deployment**:
  - *Improvement*: Package ModernizeIQ into a single hardened OCI container image (Docker/Podman) with pre-cached model weights for instant zero-network deployment inside customer air-gapped data centers.

---

## 5. Prioritized Engineering Roadmap

```
PHASE 1: Immediate Hackathon Polish (Day 1 - 2)
  ├── 1.1 Configurable Domain Weighting Profiles (Fintech vs Batch vs Monolith)
  ├── 1.2 Automated Migration Wave Sequencing Engine (Topological Wave 1/2/3)
  ├── 1.3 Graph Search & Type Filtering in Interactive Dashboard
  └── 1.4 Dynamic TF-IDF Domain Labeling for Semantic Clusters

PHASE 2: Advanced Capabilities (Post-Hackathon Q1)
  ├── 2.1 Dynamic COBOL Call Target Resolution via CICS Trace Ingestion
  ├── 2.2 FinOps TCO Sizing Calculator (MIPS to vCPU/Cloud Cost Savings)
  ├── 2.3 Draft OpenAPI Specification Generator for Domain Clusters
  └── 2.4 One-Click Jira / Azure DevOps Work Item Backlog Export

PHASE 3: Enterprise Ecosystem Platform (Q2 - Q3)
  ├── 3.1 Distributed Mainframe Repository Scanner (Git, SVN, Endeavor, Changeman)
  ├── 3.2 Dual-Run Canary Testing & Shadow Traffic Replay Simulator
  ├── 3.3 Assembler (BAL) and PL/I AST Parser Plugins
  └── 3.4 Enterprise RBAC, Multi-Tenancy & Audit Trail Compliance
```

---

## 6. Hackathon Presentation & Demo Strategy

To maximize judge engagement and demonstrate that ModernizeIQ is a true **ecosystem** rather than a simple script, present the story in 4 distinct acts:

1. **The Problem Statement**: Mainframe migrations fail because architects make blind guesses without seeing the hidden data gravity, conversational locks, and coupling.
2. **The Ingestion & Analysis**: Run ModernizeIQ live against contrasting portfolios (Core Banking vs. Policy Admin Monolith) via the CLI.
3. **The Logical Divergence**: Show how ModernizeIQ objectively recommends **Red Hat OpenShift (82% fit)** for Core Banking, but deliberately routes the Policy Admin Monolith to **Linux VM Rehosting (80% VM vs 53% OCP)** due to conversational CICS and VSAM locks, preventing a multi-million-dollar migration disaster.
4. **The Visual Climax**: Open the interactive HTML5 dashboard to demonstrate:
   - Real-time Canvas physics knowledge graph with drag-and-drop nodes.
   - Interactive blast radius simulator calculating downstream impact.
   - 2D semantic clustering scatter plot identifying microservice bounded contexts.
   - Formal downloadable Architecture Decision Record (ADR).
