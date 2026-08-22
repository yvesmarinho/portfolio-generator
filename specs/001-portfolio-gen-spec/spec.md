# Feature Specification: Portfolio Generator CLI

**Feature Branch**: `001-portfolio-gen-spec`

**Created**: 2026-06-17

**Status**: Ready for Planning

**Input**: CLI tool for automated project cataloging — scans DevOps project directories and
generates a structured portfolio catalog with summaries, code metrics, technology stacks, and
version control metadata.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generate Complete Portfolio (Priority: P1)

A DevOps engineer has dozens of projects spread across a projects directory. They want a
comprehensive, up-to-date catalog of everything they've built — without manually writing
descriptions or counting files. They run a single command and get a structured file they can
share on their portfolio website or send to a recruiter.

**Why this priority**: Core value proposition. Without this, the tool has no purpose.

**Independent Test**: Run one command pointing at a directory containing 3 test projects.
Verify a catalog file is produced with an entry for each project, containing name, type,
primary language, and description.

**Acceptance Scenarios**:

1. **Given** a directory with 5 software projects, **When** the user runs the scan command with
   no extra options, **Then** a catalog file is created with one entry per project, each
   containing name, type, language, description, and last modified date.

2. **Given** a project without a README file, **When** the scan runs, **Then** the project entry
   includes a short AI-generated description and the source field reads "ai-generated".

3. **Given** a project with a README file, **When** the scan runs, **Then** the project entry
   uses the README content as the description source and the source field reads "readme".

4. **Given** a project with a very brief README (under 30 words), **When** the scan runs,
   **Then** AI assistance is used to supplement the description.

---

### User Story 2 — Handle Problem Projects Without Stopping (Priority: P2)

The engineer has 100+ projects, some of which are old experiments with corrupted files or
unusual encodings. When one project causes an error, they expect the tool to skip it, note
the problem, and continue cataloging the remaining 99+ projects.

**Why this priority**: Makes the tool reliable in real-world, messy environments. A tool
that crashes on the first corrupt project is unusable for large portfolios.

**Independent Test**: Run the scan on a directory that includes one intentionally broken project
(empty directory, binary-only, corrupted git). Verify the output includes all other projects
and produces a warning report listing the skipped project and reason.

**Acceptance Scenarios**:

1. **Given** a directory with 5 valid projects and 1 empty directory, **When** the scan runs,
   **Then** 5 projects appear in the catalog and the execution report notes 1 skipped project.

2. **Given** a project with no recognized files (binary-only), **When** the scan runs,
   **Then** the project is skipped, a warning appears in the terminal, and a problem report is
   saved to the problems log.

3. **Given** a project where git history is corrupted, **When** the scan runs, **Then** the
   project is included in the catalog with git fields empty and a note indicating git data
   was unavailable.

---

### User Story 3 — Preview Before Writing (Priority: P3)

Before generating a catalog file, the engineer wants to preview what would be produced — how
many projects would be detected, which ones would use AI for descriptions, and what the
output structure looks like — without actually writing any files.

**Why this priority**: Prevents surprises. Engineers want confidence before committing API calls
and file writes.

**Independent Test**: Run the scan with the preview flag on a directory with 3 projects.
Verify no files are created, the terminal shows a summary of what would be generated, and
the scan ends with a "dry-run complete" message.

**Acceptance Scenarios**:

1. **Given** a scan command run with the `--dry-run` flag, **When** the command completes,
   **Then** no catalog file is created and the terminal shows what would have been produced.

2. **Given** the preview output, **When** the engineer reviews it, **Then** they can see:
   how many projects were detected, which would use AI descriptions, and estimated file size.

---

### User Story 4 — Validate Existing Catalog (Priority: P4)

The engineer has a catalog file from a previous scan and wants to verify it is complete and
correctly structured before publishing it to their portfolio website.

**Why this priority**: Quality assurance for the output artifact. Useful when sharing or
publishing the portfolio.

**Independent Test**: Run the validate command on a known-good catalog file. Verify it passes.
Run it on a catalog with a missing required field. Verify it fails with a clear error message.

**Acceptance Scenarios**:

1. **Given** a valid catalog file, **When** the validate command runs, **Then** it exits
   successfully with a "catalog is valid" message.

2. **Given** a catalog file with a missing project name, **When** the validate command runs,
   **Then** it exits with an error listing the specific field and entry that failed validation.

---

### Edge Cases

- What happens when the target directory is empty (no projects)?
  → The tool produces an empty catalog file with zero entries and a warning.

- What happens when the target directory itself does not exist?
  → The tool exits immediately with a clear "directory not found" error before scanning anything.

- What happens when there are 500+ projects and the scan takes longer than expected?
  → A live progress bar shows scan status; the tool completes without timeout.

- What happens when the AI service is unavailable but projects need AI descriptions?
  → Projects that need AI descriptions are cataloged with an empty description and source
    "ai-unavailable"; the tool does not fail.

- What happens when the catalog output path already exists?
  → The tool warns the user and appends a timestamp suffix to avoid overwriting.

- What happens when the user runs the scan outside the allowed directory scope?
  → The tool refuses with a "path outside allowed scope" error before reading any files.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST scan a configurable target directory and produce a catalog entry for
  each immediate subdirectory that contains recognizable project files.

- **FR-002**: System MUST extract the following metadata for each project: name, inferred type,
  primary programming language, secondary languages, estimated file count, estimated total size,
  and last modification date.

- **FR-003**: System MUST detect version control metadata when available: current branch, last
  commit identifier, last commit date, commit author, and total commit count.

- **FR-004**: System MUST generate a project description by reading the project's README file
  when one is present and sufficiently detailed (above a configurable word threshold).

- **FR-005**: System MUST use an external AI service to generate project descriptions when:
  a README file is absent, or the README is shorter than a configurable word threshold,
  or the README is longer than a configurable length limit.

- **FR-006**: System MUST record the source of each project description ("readme", "ai-generated",
  or "filename") so users can audit how descriptions were produced.

- **FR-007**: System MUST produce a single structured catalog file conforming to a published schema,
  including a generation timestamp and total project count.

- **FR-008**: System MUST validate the produced catalog file against the published schema before
  reporting success.

- **FR-009**: System MUST skip individual projects that encounter errors during scanning, log the
  reason, and continue scanning remaining projects without interruption.

- **FR-010**: System MUST complete scanning 100 projects within 30 seconds under normal load.

- **FR-011**: System MUST respect a configurable limit on parallel processing workers to avoid
  overloading the host machine.

- **FR-012**: System MUST display real-time progress to the user during scanning (e.g., "scanning
  project X of Y").

- **FR-013**: System MUST support a preview mode where all analysis runs but no files are written.

- **FR-014**: System MUST refuse to process any directory path outside the configured allowed scope
  and exit with a clear error message.

- **FR-015**: System MUST provide a validate subcommand that checks an existing catalog file against
  the published schema and reports any violations.

- **FR-016**: System MUST allow the user to disable AI description generation via a command-line flag,
  in which case projects needing AI descriptions receive empty descriptions.

### Key Entities

- **Project**: A single software project — one immediate subdirectory of the target directory.
  Key attributes: name, path, inferred type, primary language, description, description source,
  metrics, version control info, technology list, last modified date.

- **Portfolio Catalog**: The complete output — a collection of project entries plus run metadata
  (generation date, total count, tool version).

- **Project Metrics**: Quantitative measurements for a single project: file count, estimated
  line count, size on disk.

- **Version Control Info**: Git metadata for a project: initialization status, branch, last commit
  hash, last commit date, last commit author, total commit count.

- **Execution Report**: A summary of what happened during a scan: projects processed, projects
  skipped, errors encountered, total time.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can catalog 100+ projects with a single command in under 30 seconds on
  a modern workstation.

- **SC-002**: A fresh installation is operational (clone → install → first scan) in under 2 minutes.

- **SC-003**: 90% or more of projects that have a README file receive an accurate description
  automatically, without manual editing.

- **SC-004**: The catalog file passes schema validation 100% of the time when produced by the tool.

- **SC-005**: Projects with missing, corrupted, or unreadable files are handled without crashing
  the tool; at least 95% of valid projects in the directory are still included.

- **SC-006**: A user who runs the tool in preview mode sees what would be generated — number of
  projects, AI usage estimate, output size estimate — with no files created.

- **SC-007**: Users can validate an existing catalog file in under 5 seconds and receive a clear
  pass/fail result with specific error locations when failing.

- **SC-008**: The tool's memory usage stays below a defined threshold even when scanning a
  directory with 200+ projects.

---

## Assumptions

- The target directory contains project subdirectories at a single depth level (not recursively
  nested sub-projects); deeper nesting is out of scope for v1.

- Users have an internet connection when AI description generation is enabled; the tool
  requires network access to call the AI service.

- AI credentials (API key) are pre-configured by the user before running the tool; the tool
  does not include a setup wizard for credentials in v1.

- Projects are expected to be development repositories (software projects, scripts, infrastructure
  configs); non-project directories (archive folders, empty directories) are either skipped or
  produce minimal catalog entries.

- The primary language detection accuracy is acceptable for the most common programming languages
  (Python, JavaScript, TypeScript, Bash, Go, Rust, Java, YAML/JSON config); exotic languages
  may fall back to "unknown".

- The tool runs on a single user's local machine; multi-user or server deployment is out of scope.

- Output format is JSON for v1; additional formats (HTML, Markdown, CSV) are secondary features
  not required for the MVP.
