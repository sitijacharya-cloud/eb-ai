# Estimation Comparison Tool - User Guide

## Overview

The Estimation Comparison Tool analyzes the accuracy of AI-generated project estimations by comparing them against actual (template) estimations across 5 key dimensions:

1. **Total Hours Comparison** - Accuracy of overall effort prediction
2. **Platform Coverage** - Identification of required platforms
3. **User Role Coverage** - Identification of user types
4. **Epic Coverage** - Identification of major features (with fuzzy matching)
5. **Task Coverage** - Granularity and completeness of task breakdown

## Installation

### Prerequisites

```bash
# System requirement for PDF generation (optional)
# macOS:
brew install wkhtmltopdf

# Ubuntu/Debian:
sudo apt-get install wkhtmltopdf

# Windows:
# Download from https://wkhtmltopdf.org/downloads.html
```

### Install Dependencies

```bash
cd "/Users/ebpearls/Desktop/Ai estimation"
pip install -r requirements.txt
```

Key dependencies:
- `markdown` - Markdown to HTML conversion
- `pdfkit` - HTML to PDF conversion
- `tabulate` - Table formatting
- `python-dateutil` - Date utilities

## Usage

### Basic Usage

```bash
python backend/scripts/compare_estimates.py \
  --actual gradetime_template.json \
  --predicted grade_estimation.json
```

This will generate:
- `comparison_report.md` - Markdown report
- `comparison_report.pdf` - PDF report (if dependencies available)

### Advanced Usage

```bash
# Custom output filename
python backend/scripts/compare_estimates.py \
  --actual gradetime_template.json \
  --predicted grade_estimation.json \
  --output my_custom_report

# Adjust fuzzy matching threshold (default: 0.75)
python backend/scripts/compare_estimates.py \
  --actual gradetime_template.json \
  --predicted grade_estimation.json \
  --threshold 0.85

# Skip PDF generation (Markdown only)
python backend/scripts/compare_estimates.py \
  --actual gradetime_template.json \
  --predicted grade_estimation.json \
  --no-pdf
```

### Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--actual` | ✅ Yes | - | Path to actual estimation JSON (template) |
| `--predicted` | ✅ Yes | - | Path to predicted estimation JSON (AI-generated) |
| `--output` | ❌ No | `comparison_report` | Output filename (without extension) |
| `--threshold` | ❌ No | `0.75` | Fuzzy matching threshold for epic names (0.0-1.0) |
| `--no-pdf` | ❌ No | `False` | Skip PDF generation |

## Understanding the Report

### 1. Total Hours Comparison

Shows how accurate the AI's overall time estimation is:

```
✅ ACCURATE      - Within ±10% of actual hours
⚠️ UNDERESTIMATED - 10-20% below actual hours
❌ OVERESTIMATED  - More than 20% above/below actual hours
```

**Example:**
```
Actual Hours:    500
Predicted Hours: 475
Difference:      -25 (-5.00%)
Status:          ✅ ACCURATE
```

### 2. Platform Coverage

Measures how well the AI identified required platforms (Flutter, API, CMS, etc.):

```
Coverage % = (Matched Platforms / Total Actual Platforms) × 100
```

**Example:**
```
Actual Platforms:    3 (Flutter, API, CMS)
Predicted Platforms: 2 (Flutter, API)
Coverage:            66.67%
Missing:             CMS
```

### 3. User Role Coverage

Measures identification of user types (Student, Teacher, Admin, etc.):

```
Coverage % = (Matched Roles / Total Actual Roles) × 100
```

**Example:**
```
Actual Roles:    3 (Student, Teacher, Admin)
Predicted Roles: 4 (Student, Teacher, Parent, Admin)
Coverage:        100.00%
Extra:           Parent
```

### 4. Epic Coverage

Measures identification of major features using fuzzy string matching:

- **Exact Match**: Same name (case-insensitive)
- **Fuzzy Match**: Similar name (similarity ≥ threshold)

**Example:**
```
Actual Epic:    "User Authentication"
Predicted Epic: "User Authentication & Authorization"
Match Type:     FUZZY
Similarity:     0.83
```

### 5. Task Coverage & Granularity

Analyzes task breakdown completeness and detail level:

- **Coverage**: How many tasks were identified per epic
- **Granularity**: Level of task detail (more/less/similar)

**Example:**
```
Epic: User Authentication
Actual Tasks:    5
Predicted Tasks: 3
Coverage:        60.00%
Granularity:     📉 LESS_GRANULAR (AI broke into fewer tasks)
```

## Fuzzy Matching Explained

The tool uses **fuzzy string matching** to handle variations in epic naming:

### How It Works

1. **Exact Match First**: Tries case-insensitive exact match
2. **Fuzzy Match**: Calculates similarity ratio using difflib.SequenceMatcher
3. **Threshold**: Only accepts matches above threshold (default 0.75)

### Threshold Values

| Threshold | Description | Example Match |
|-----------|-------------|---------------|
| `1.0` | Perfect match only | "Login" = "Login" |
| `0.9` | Very similar | "User Login" ≈ "User Login System" |
| `0.75` | Similar (default) | "Authentication" ≈ "User Authentication" |
| `0.6` | Loosely similar | "Profile" ≈ "User Profile Management" |
| `0.5` | Very loose | "Settings" ≈ "App Configuration" |

### Choosing a Threshold

- **Higher (0.8-1.0)**: Stricter matching, fewer false positives, more "missing" epics
- **Default (0.75)**: Balanced - catches common variations
- **Lower (0.5-0.7)**: Looser matching, more matches, potential false positives

**Recommendation**: Start with default `0.75`, adjust based on results.

## Report Sections

### Overall Coverage Score

Average of all 4 coverage metrics (excludes hours):

```
Overall Score = (Platform Coverage + User Role Coverage + Epic Coverage + Task Coverage) / 4
```

Status indicators:
- ✅ **Good** (≥80%): System is performing well
- ⚠️ **Moderate** (50-79%): Needs improvement
- ❌ **Poor** (<50%): Significant issues

### Key Findings

Automatically generated insights:
- Hours estimation accuracy assessment
- Best performing coverage area
- Area needing most improvement
- Specific recommendations

## File Structure

```
backend/
├── app/
│   └── utils/
│       └── comparison_utils.py      # Core comparison logic
└── scripts/
    └── compare_estimates.py         # CLI script

test_comparison.py                    # Unit tests
comparison_report.md                  # Generated Markdown report
comparison_report.pdf                 # Generated PDF report (optional)
```

## Troubleshooting

### Issue: "Module not found: comparison_utils"

**Solution**: Ensure you're running from the workspace root:
```bash
cd "/Users/ebpearls/Desktop/Ai estimation"
python backend/scripts/compare_estimates.py ...
```

### Issue: "PDF generation skipped"

**Cause**: Missing `pdfkit` or `wkhtmltopdf`

**Solution**:
```bash
# Install pdfkit
pip install pdfkit

# Install wkhtmltopdf
# macOS:
brew install wkhtmltopdf

# Ubuntu:
sudo apt-get install wkhtmltopdf
```

Or use `--no-pdf` flag to skip PDF generation.

### Issue: "Invalid JSON file"

**Cause**: Malformed JSON estimation file

**Solution**: Validate JSON structure:
```bash
python -m json.tool your_file.json
```

Required structure:
```json
{
  "epics": [
    {
      "name": "Epic Name",
      "user_types": ["Role1", "Role2"],
      "tasks": [
        {
          "name": "Task Name",
          "efforts": {
            "Platform1": 5,
            "Platform2": 3
          }
        }
      ]
    }
  ]
}
```

## Examples

### Example 1: Compare Two Estimations

```bash
python backend/scripts/compare_estimates.py \
  --actual gradetime_template.json \
  --predicted grade_estimation.json \
  --output gradetime_comparison
```

**Output:**
```
📂 Loading actual estimation: gradetime_template.json
📂 Loading predicted estimation: grade_estimation.json
🔍 Performing comparison analysis...
  ⏱️  Comparing total hours...
  🖥️  Comparing platform coverage...
  👥 Comparing user role coverage...
  📋 Comparing epic coverage...
  ✅ Comparing task coverage...
📝 Generating report...
✅ Markdown report saved: gradetime_comparison.md
✅ PDF report saved: gradetime_comparison.pdf

✅ Comparison complete!
📊 Overall Coverage Score: 85.25%
```

### Example 2: Strict Epic Matching

```bash
python backend/scripts/compare_estimates.py \
  --actual nuc_template.json \
  --predicted NUC_estimation.json \
  --threshold 0.9 \
  --output nuc_strict_comparison
```

This uses a stricter 0.9 threshold, requiring 90% similarity for epic matches.

### Example 3: Quick Markdown Report

```bash
python backend/scripts/compare_estimates.py \
  --actual wedmap_template.json \
  --predicted wedmap_estimation.json \
  --no-pdf \
  --output wedmap_quick
```

Generates only Markdown report (faster, no PDF dependencies needed).

## Integration with Workflow

### Recommended Workflow

1. **Generate Estimation**: Use AI system to create estimation
2. **Run Comparison**: Compare against template/actual
3. **Analyze Report**: Review coverage scores and findings
4. **Iterate**: Adjust prompts/agents based on weak areas
5. **Re-test**: Generate new estimation and compare again

### Automated Testing

```bash
#!/bin/bash
# test_all_projects.sh

projects=("gradetime" "nuc" "wedmap")

for project in "${projects[@]}"; do
    echo "Testing $project..."
    python backend/scripts/compare_estimates.py \
        --actual "${project}_template.json" \
        --predicted "${project}_estimation.json" \
        --output "reports/${project}_comparison"
done

echo "All comparisons complete! Check reports/ directory"
```

## API Usage (Programmatic)

You can also use the comparison utilities directly in Python:

```python
from backend.app.utils.comparison_utils import (
    extract_platforms,
    extract_epics,
    compare_epics,
    fuzzy_match_epics
)
import json

# Load data
with open('actual.json') as f:
    actual = json.load(f)
with open('predicted.json') as f:
    predicted = json.load(f)

# Extract and compare
actual_epics = extract_epics(actual)
predicted_epics = extract_epics(predicted)
result = compare_epics(actual_epics, predicted_epics, threshold=0.75)

print(f"Coverage: {result['coverage_percentage']:.2f}%")
print(f"Matched: {result['matched_count']}")
print(f"Missing: {result['missing_count']}")
```

## Best Practices

### For Accurate Comparisons

1. **Use Consistent JSON Structure**: Ensure both files follow the same format
2. **Start with Default Threshold**: Use 0.75, adjust if needed
3. **Review Fuzzy Matches**: Check if fuzzy matches are legitimate
4. **Consider Context**: 100% coverage isn't always necessary (extra features may be valid)
5. **Track Over Time**: Compare multiple iterations to measure improvement

### For Meaningful Results

1. **Use Real Templates**: Compare against actual project estimations, not synthetic data
2. **Test Multiple Projects**: Single comparison may not be representative
3. **Focus on Patterns**: Look for consistent coverage gaps across projects
4. **Balance Metrics**: Don't optimize for one metric at the expense of others
5. **Document Findings**: Keep notes on what works and what doesn't

## Version Information

- **Tool Version**: 1.0.0
- **Created**: January 12, 2026
- **Compatible with**: Estimation System v3.0.0
- **Python Version**: 3.8+

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the generated report's "Key Findings" for automatic insights
3. Examine the Markdown report for detailed breakdowns
4. Run `test_comparison.py` to verify installation

## Changelog

### v1.0.0 (2026-01-12)
- Initial release
- 5 comparison dimensions
- Fuzzy epic matching
- Markdown and PDF report generation
- CLI interface with arguments
- Comprehensive documentation
