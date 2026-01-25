---
name: java-code-auditor
description: Java code quality auditor focused on code review assistance. Analyzes Java source code for quality issues, complexity problems, performance bottlenecks, and security vulnerabilities. Generates comprehensive HTML reports for code review workflows. Use when working with Java projects that need code quality assessment, complexity analysis, performance issue detection, security vulnerability scanning, or code review preparation.
---

# Java Code Auditor

## Overview

Enables comprehensive Java code quality analysis with focus on code review workflows, generating detailed HTML reports with actionable insights.

## Quick Start

Run complete audit on Java project:

```bash
python3 scripts/java-analyzer.py --project /path/to/java/project --output report.html
```

## Core Capabilities

### 1. Code Quality Analysis

**Purpose**: Identify code quality issues that impact maintainability and readability.

**Run analysis**:

```bash
python3 scripts/java-analyzer.py --quality --project /path/to/project
```

**Checks performed**:

- Naming convention violations
- Code duplication detection
- Method length violations
- Class size analysis
- Missing documentation

**Quality thresholds**: See [references/java-quality-rules.md](references/java-quality-rules.md)

### 2. Complexity Analysis

**Purpose**: Measure cognitive complexity to identify hard-to-maintain code.

**Run analysis**:

```bash
python3 scripts/complexity-checker.py --project /path/to/project --threshold 10
```

**Metrics calculated**:

- Cyclomatic complexity
- Cognitive complexity
- Nesting depth
- Parameter count

**Threshold definitions**: See [references/complexity-thresholds.md](references/complexity-thresholds.md)

### 3. Performance Analysis

**Purpose**: Detect performance bottlenecks and inefficient patterns.

**Run analysis**:

```bash
python3 scripts/java-analyzer.py --performance --project /path/to/project
```

**Issues detected**:

- Inefficient collection usage
- Unnecessary object creation
- Resource leaks
- Synchronization issues

### 4. Security Vulnerability Scan

**Purpose**: Identify common security issues in Java code.

**Run analysis**:

```bash
python3 scripts/java-analyzer.py --security --project /path/to/project
```

**Vulnerabilities checked**:

- SQL injection risks
- Path traversal
- Hardcoded secrets
- Weak cryptography
- Input validation issues

## Report Generation

### HTML Reports

**Generate comprehensive report**:

```bash
python3 scripts/html-reporter.py --input analysis_results.json --output report.html
```

**Report includes**:

- Executive summary
- Issue severity breakdown
- File-by-file analysis
- Trend analysis (historical data)
- Actionable recommendations

**Report template**: Located at [assets/report-template/](assets/report-template/)

## Workflow Integration

### Code Review Preparation

**Prepare for code review**:

```bash
# Run full analysis before PR
python3 scripts/java-analyzer.py --all --project . --output pr-review.html

# Focus on changed files only
python3 scripts/java-analyzer.py --diff --base main --head feature-branch
```

### CI/CD Integration

**GitHub Actions example**:

```yaml
- name: Java Code Audit
  run: |
    python3 .opencode/skill/java-code-auditor/scripts/java-analyzer.py \
      --project . \
      --output audit-report.html \
      --fail-on critical
```

## Customization

### Rule Configuration

**Customize quality rules** by editing:

- [references/java-quality-rules.md](references/java-quality-rules.md) - Quality standards
- [references/naming-conventions.md](references/naming-conventions.md) - Naming rules
- [references/complexity-thresholds.md](references/complexity-thresholds.md) - Complexity limits

### Report Styling

**Customize HTML reports** by modifying:

- [assets/report-template/style.css](assets/report-template/style.css)
- [assets/report-template/template.html](assets/report-template/template.html)

## Resources

### scripts/

Executable Python scripts for Java code analysis:

- `java-analyzer.py` - Main analysis orchestrator
- `complexity-checker.py` - Complexity analysis engine
- `duplicate-detector.py` - Code duplication detection
- `naming-validator.py` - Naming convention checker
- `html-reporter.py` - HTML report generator

### references/

Documentation and standards for Java code quality:

- `java-quality-rules.md` - Comprehensive quality standards and thresholds
- `naming-conventions.md` - Detailed Java naming conventions
- `complexity-thresholds.md` - Complexity metric definitions and limits
- `security-checks.md` - Security vulnerability patterns and detection rules

### assets/

Templates and styling for HTML reports:

- `report-template/template.html` - HTML report template
- `report-template/style.css` - Report styling
- `report-template/charts.js` - Interactive chart components
- `icons/` - Icons and images used in reports
