#!/usr/bin/env python3
"""
Estimation Comparison CLI Tool

Compare actual vs predicted estimation JSON files across 5 dimensions:
1. Total Hours Comparison
2. Platform Coverage
3. User Role Coverage
4. Epic Coverage (with fuzzy matching)
5. Task Coverage (granularity analysis)

Usage:
     python backend/scripts/compare_estimates.py --actual wedmap_template.json --predicted "Wed Map_estimation.json" --output test_report
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Import comparison utilities
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))
from comparison_utils import (
    extract_platforms,
    extract_user_roles,
    extract_epics,
    calculate_total_hours,
    compare_total_hours,
    compare_platforms,
    compare_user_roles,
    compare_epics,
    compare_tasks,
    generate_status_emoji
)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse JSON estimation file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
    """
    path = Path(file_path)
    
    # If absolute path or file exists, use it
    if path.is_absolute() or path.exists():
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Otherwise, look in comparison folder at root
    comparison_folder = Path(__file__).parent.parent.parent / "comparison"
    comparison_path = comparison_folder / file_path
    
    if comparison_path.exists():
        with open(comparison_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"File not found: {file_path}\nSearched in: {comparison_path}")


def generate_markdown_report(
    actual_data: Dict[str, Any],
    predicted_data: Dict[str, Any],
    hours_comparison: Dict[str, Any],
    platform_comparison: Dict[str, Any],
    user_role_comparison: Dict[str, Any],
    epic_comparison: Dict[str, Any],
    task_comparison: Dict[str, Any],
    threshold: float
) -> str:
    """
    Generate comprehensive Markdown report.
    
    Args:
        actual_data: Actual estimation data
        predicted_data: Predicted estimation data
        hours_comparison: Hours comparison results
        platform_comparison: Platform comparison results
        user_role_comparison: User role comparison results
        epic_comparison: Epic comparison results
        task_comparison: Task comparison results
        threshold: Fuzzy matching threshold used
        
    Returns:
        Markdown formatted report
    """
    report_lines = []
    
    # Header
    report_lines.append("# Estimation Comparison Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Fuzzy Match Threshold:** {threshold}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 1. Total Hours Comparison
    report_lines.append("## 1. Total Hours Comparison")
    report_lines.append("")
    status_emoji = "✅" if abs(hours_comparison['difference_percentage']) < 10 else "⚠️" if abs(hours_comparison['difference_percentage']) < 20 else "❌"
    report_lines.append(f"**Status:** {status_emoji} {hours_comparison['status']}")
    report_lines.append("")
    report_lines.append("| Metric | Value |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| Actual Hours | {hours_comparison['actual_hours']} |")
    report_lines.append(f"| Predicted Hours | {hours_comparison['predicted_hours']} |")
    report_lines.append(f"| Difference | {hours_comparison['difference']:+d} ({hours_comparison['difference_percentage']:+.2f}%) |")
    report_lines.append("")
    
    # 2. Platform Coverage
    report_lines.append("## 2. Platform Coverage")
    report_lines.append("")
    platform_emoji = generate_status_emoji(platform_comparison['coverage_percentage'])
    report_lines.append(f"**Status:** {platform_emoji} {platform_comparison['coverage_percentage']:.2f}% Coverage")
    report_lines.append("")
    report_lines.append("| Metric | Count |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| Actual Platforms | {platform_comparison['total_actual']} |")
    report_lines.append(f"| Predicted Platforms | {platform_comparison['total_predicted']} |")
    report_lines.append(f"| Matched | {platform_comparison['matched_count']} |")
    report_lines.append("")
    
    if platform_comparison['matched']:
        report_lines.append("**✅ Matched Platforms:**")
        for platform in platform_comparison['matched']:
            report_lines.append(f"- {platform}")
        report_lines.append("")
    
    if platform_comparison['missing']:
        report_lines.append("**❌ Missing Platforms (in Actual but not Predicted):**")
        for platform in platform_comparison['missing']:
            report_lines.append(f"- {platform}")
        report_lines.append("")
    
    if platform_comparison['extra']:
        report_lines.append("**➕ Extra Platforms (in Predicted but not Actual):**")
        for platform in platform_comparison['extra']:
            report_lines.append(f"- {platform}")
        report_lines.append("")
    
    # 3. User Role Coverage
    report_lines.append("## 3. User Role Coverage")
    report_lines.append("")
    role_emoji = generate_status_emoji(user_role_comparison['coverage_percentage'])
    report_lines.append(f"**Status:** {role_emoji} {user_role_comparison['coverage_percentage']:.2f}% Coverage")
    report_lines.append("")
    report_lines.append("| Metric | Count |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| Actual User Roles | {user_role_comparison['total_actual']} |")
    report_lines.append(f"| Predicted User Roles | {user_role_comparison['total_predicted']} |")
    report_lines.append(f"| Matched | {user_role_comparison['matched_count']} |")
    report_lines.append("")
    
    if user_role_comparison['matched']:
        report_lines.append("**✅ Matched User Roles:**")
        for role in user_role_comparison['matched']:
            report_lines.append(f"- {role}")
        report_lines.append("")
    
    if user_role_comparison['missing']:
        report_lines.append("**❌ Missing User Roles (in Actual but not Predicted):**")
        for role in user_role_comparison['missing']:
            report_lines.append(f"- {role}")
        report_lines.append("")
    
    if user_role_comparison['extra']:
        report_lines.append("**➕ Extra User Roles (in Predicted but not Actual):**")
        for role in user_role_comparison['extra']:
            report_lines.append(f"- {role}")
        report_lines.append("")
    
    # 4. Epic Coverage
    report_lines.append("## 4. Epic Coverage")
    report_lines.append("")
    epic_emoji = generate_status_emoji(epic_comparison['coverage_percentage'])
    report_lines.append(f"**Status:** {epic_emoji} {epic_comparison['coverage_percentage']:.2f}% Coverage")
    report_lines.append("")
    report_lines.append("| Metric | Count |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| Actual Epics | {epic_comparison['total_actual']} |")
    report_lines.append(f"| Predicted Epics | {epic_comparison['total_predicted']} |")
    report_lines.append(f"| Matched (Total) | {epic_comparison['matched_count']} |")
    report_lines.append(f"| Matched (Exact) | {epic_comparison['exact_matches']} |")
    report_lines.append(f"| Matched (Fuzzy) | {epic_comparison['fuzzy_matches']} |")
    report_lines.append(f"| Missing | {epic_comparison['missing_count']} |")
    report_lines.append(f"| Extra | {epic_comparison['extra_count']} |")
    report_lines.append("")
    
    if epic_comparison['matched']:
        report_lines.append("**✅ Matched Epics:**")
        report_lines.append("")
        report_lines.append("| Actual Epic | Predicted Epic | Match Type | Similarity |")
        report_lines.append("|-------------|----------------|------------|------------|")
        for actual_epic, predicted_epic, similarity, match_type in epic_comparison['matched']:
            sim_display = f"{similarity:.2f}" if match_type == 'FUZZY' else "1.00"
            report_lines.append(f"| {actual_epic['name']} | {predicted_epic['name']} | {match_type} | {sim_display} |")
        report_lines.append("")
    
    if epic_comparison['missing']:
        report_lines.append("**❌ Missing Epics (in Actual but not Predicted):**")
        for epic in epic_comparison['missing']:
            mandatory = " [MANDATORY]" if epic.get('is_mandatory') else ""
            report_lines.append(f"- {epic['name']}{mandatory}")
        report_lines.append("")
    
    if epic_comparison['extra']:
        report_lines.append("**➕ Extra Epics (in Predicted but not Actual):**")
        for epic in epic_comparison['extra']:
            report_lines.append(f"- {epic['name']}")
        report_lines.append("")
    
    # 5. Task Coverage
    report_lines.append("## 5. Task Coverage & Granularity")
    report_lines.append("")
    task_emoji = generate_status_emoji(task_comparison['overall_task_coverage'])
    report_lines.append(f"**Status:** {task_emoji} {task_comparison['overall_task_coverage']:.2f}% Overall Coverage")
    report_lines.append("")
    report_lines.append("| Metric | Value |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| Avg Actual Tasks per Epic | {task_comparison['avg_actual_tasks']:.2f} |")
    report_lines.append(f"| Avg Predicted Tasks per Epic | {task_comparison['avg_predicted_tasks']:.2f} |")
    report_lines.append(f"| Granularity Difference | {task_comparison['granularity_difference_percentage']:+.2f}% |")
    report_lines.append("")
    
    if task_comparison['epic_task_details']:
        report_lines.append("**Epic-by-Epic Task Analysis:**")
        report_lines.append("")
        report_lines.append("| Epic Name | Actual Tasks | Predicted Tasks | Coverage | Granularity |")
        report_lines.append("|-----------|--------------|-----------------|----------|-------------|")
        for detail in task_comparison['epic_task_details']:
            granularity_emoji = "📊" if detail['granularity'] == "SIMILAR" else "📉" if detail['granularity'] == "LESS_GRANULAR" else "📈"
            report_lines.append(
                f"| {detail['epic_name']} | "
                f"{detail['actual_task_count']} | "
                f"{detail['predicted_task_count']} | "
                f"{detail['coverage_percentage']:.2f}% | "
                f"{granularity_emoji} {detail['granularity']} |"
            )
        report_lines.append("")
    
    # Summary
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Overall Summary")
    report_lines.append("")
    
    # Calculate overall score
    scores = [
        platform_comparison['coverage_percentage'],
        user_role_comparison['coverage_percentage'],
        epic_comparison['coverage_percentage'],
        task_comparison['overall_task_coverage']
    ]
    overall_score = sum(scores) / len(scores)
    overall_emoji = generate_status_emoji(overall_score)
    
    report_lines.append(f"**Overall Coverage Score:** {overall_emoji} {overall_score:.2f}%")
    report_lines.append("")
    report_lines.append("| Dimension | Coverage |")
    report_lines.append("|-----------|----------|")
    report_lines.append(f"| Platform Coverage | {platform_comparison['coverage_percentage']:.2f}% |")
    report_lines.append(f"| User Role Coverage | {user_role_comparison['coverage_percentage']:.2f}% |")
    report_lines.append(f"| Epic Coverage | {epic_comparison['coverage_percentage']:.2f}% |")
    report_lines.append(f"| Task Coverage | {task_comparison['overall_task_coverage']:.2f}% |")
    report_lines.append("")
    
    # Key findings
    report_lines.append("### Key Findings")
    report_lines.append("")
    
    # Hours accuracy
    hours_diff_abs = abs(hours_comparison['difference_percentage'])
    if hours_diff_abs < 10:
        report_lines.append(f"✅ **Hours estimation is highly accurate** ({hours_diff_abs:.2f}% difference)")
    elif hours_diff_abs < 20:
        report_lines.append(f"⚠️ **Hours estimation is moderately accurate** ({hours_diff_abs:.2f}% difference)")
    else:
        report_lines.append(f"❌ **Hours estimation needs improvement** ({hours_diff_abs:.2f}% difference)")
    report_lines.append("")
    
    # Best and worst coverage
    coverage_items = [
        ("Platforms", platform_comparison['coverage_percentage']),
        ("User Roles", user_role_comparison['coverage_percentage']),
        ("Epics", epic_comparison['coverage_percentage']),
        ("Tasks", task_comparison['overall_task_coverage'])
    ]
    sorted_coverage = sorted(coverage_items, key=lambda x: x[1], reverse=True)
    
    report_lines.append(f"✅ **Best Coverage:** {sorted_coverage[0][0]} ({sorted_coverage[0][1]:.2f}%)")
    report_lines.append(f"❌ **Needs Improvement:** {sorted_coverage[-1][0]} ({sorted_coverage[-1][1]:.2f}%)")
    report_lines.append("")
    
    return "\n".join(report_lines)


def save_markdown_report(report_content: str, output_path: str) -> Path:
    """
    Save Markdown report to file.
    
    Args:
        report_content: Markdown content
        output_path: Output file path (without extension)
        
    Returns:
        Path to saved file
    """
    output_file = Path(f"{output_path}.md")
    output_file.write_text(report_content, encoding='utf-8')
    print(f"✅ Markdown report saved: {output_file}")
    return output_file


def save_pdf_report(markdown_content: str, output_path: str) -> Path:
    """
    Convert Markdown to PDF and save.
    
    Args:
        markdown_content: Markdown content
        output_path: Output file path (without extension)
        
    Returns:
        Path to saved PDF file
    """
    try:
        import markdown
        import pdfkit
        
        # Convert Markdown to HTML
        html = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code']
        )
        
        # Add basic CSS styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                hr {{
                    border: 0;
                    border-top: 2px solid #3498db;
                    margin: 30px 0;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Convert to PDF
        output_file = Path(f"{output_path}.pdf")
        pdfkit.from_string(styled_html, str(output_file))
        print(f"✅ PDF report saved: {output_file}")
        return output_file
        
    except ImportError as e:
        print(f"⚠️ PDF generation skipped: Missing dependency ({e})")
        print("   Install with: pip install markdown pdfkit")
        print("   Note: pdfkit also requires wkhtmltopdf (https://wkhtmltopdf.org/)")
        return None
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
        return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compare actual vs predicted estimation JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_estimates.py --actual actual.json --predicted predicted.json
  python compare_estimates.py --actual actual.json --predicted predicted.json --output my_report
  python compare_estimates.py --actual actual.json --predicted predicted.json --threshold 0.8
        """
    )
    
    parser.add_argument(
        '--actual',
        required=True,
        help='Path to actual estimation JSON file'
    )
    
    parser.add_argument(
        '--predicted',
        required=True,
        help='Path to predicted estimation JSON file'
    )
    
    parser.add_argument(
        '--output',
        default='comparison_report',
        help='Output file path (without extension, default: comparison_report)'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='Fuzzy matching threshold for epic names (0.0-1.0, default: 0.75)'
    )
    
    parser.add_argument(
        '--no-pdf',
        action='store_true',
        help='Skip PDF generation (only create Markdown)'
    )
    
    args = parser.parse_args()
    
    # Validate threshold
    if not 0.0 <= args.threshold <= 1.0:
        print("❌ Error: Threshold must be between 0.0 and 1.0")
        sys.exit(1)
    
    try:
        # Load JSON files
        print(f"📂 Loading actual estimation: {args.actual}")
        actual_data = load_json_file(args.actual)
        
        print(f"📂 Loading predicted estimation: {args.predicted}")
        predicted_data = load_json_file(args.predicted)
        
        print("🔍 Performing comparison analysis...")
        
        # Extract data
        actual_platforms = extract_platforms(actual_data)
        predicted_platforms = extract_platforms(predicted_data)
        
        actual_roles = extract_user_roles(actual_data)
        predicted_roles = extract_user_roles(predicted_data)
        
        actual_epics = extract_epics(actual_data)
        predicted_epics = extract_epics(predicted_data)
        
        actual_hours = calculate_total_hours(actual_data)
        predicted_hours = calculate_total_hours(predicted_data)
        
        # Perform comparisons
        print("  ⏱️  Comparing total hours...")
        hours_comparison = compare_total_hours(actual_hours, predicted_hours)
        
        print("  🖥️  Comparing platform coverage...")
        platform_comparison = compare_platforms(actual_platforms, predicted_platforms)
        
        print("  👥 Comparing user role coverage...")
        user_role_comparison = compare_user_roles(actual_roles, predicted_roles)
        
        print("  📋 Comparing epic coverage...")
        epic_comparison = compare_epics(actual_epics, predicted_epics, args.threshold)
        
        print("  ✅ Comparing task coverage...")
        task_comparison = compare_tasks(actual_epics, predicted_epics, epic_comparison['matched'])
        
        # Generate report
        print("📝 Generating report...")
        report_content = generate_markdown_report(
            actual_data,
            predicted_data,
            hours_comparison,
            platform_comparison,
            user_role_comparison,
            epic_comparison,
            task_comparison,
            args.threshold
        )
        
        # Save Markdown
        save_markdown_report(report_content, args.output)
        
        # Save PDF (unless --no-pdf)
        if not args.no_pdf:
            save_pdf_report(report_content, args.output)
        
        print("")
        print("✅ Comparison complete!")
        print(f"📊 Overall Coverage Score: {((platform_comparison['coverage_percentage'] + user_role_comparison['coverage_percentage'] + epic_comparison['coverage_percentage'] + task_comparison['overall_task_coverage']) / 4):.2f}%")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
