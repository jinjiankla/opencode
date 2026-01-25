#!/usr/bin/env python3
"""
HTML Reporter - Generate comprehensive HTML reports for Java code analysis
Converts JSON analysis results into interactive HTML reports
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import html

class HTMLReporter:
    def generate_report(self, analysis_data: dict, output_path: str):
        """Generate complete HTML report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract summary information
        summary = analysis_data.get('summary', {})
        total_issues = summary.get('total_issues', 0)
        critical_issues = summary.get('critical_issues', 0)
        high_issues = summary.get('high_issues', 0)
        medium_issues = summary.get('medium_issues', 0)
        low_issues = summary.get('low_issues', 0)
        
        health_score = max(0, 100 - (critical_issues * 10 + high_issues * 5 + medium_issues * 2 + low_issues))
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Java Code Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .header .subtitle {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .summary-card.critical {{
            border-left-color: #e74c3c;
        }}
        .summary-card.high {{
            border-left-color: #f39c12;
        }}
        .summary-card.medium {{
            border-left-color: #f1c40f;
        }}
        .summary-card.low {{
            border-left-color: #27ae60;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 2em;
            color: #2c3e50;
        }}
        .summary-card p {{
            margin: 0;
            color: #7f8c8d;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .issue-list {{
            list-style: none;
            padding: 0;
        }}
        .issue-item {{
            background: #f8f9fa;
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .issue-item.critical {{
            border-left-color: #e74c3c;
        }}
        .issue-item.high {{
            border-left-color: #f39c12;
        }}
        .issue-item.medium {{
            border-left-color: #f1c40f;
        }}
        .issue-item.low {{
            border-left-color: #27ae60;
        }}
        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .issue-title {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .issue-severity {{
            padding: 3px 8px;
            border-radius: 3px;
            color: white;
            font-size: 0.8em;
        }}
        .severity-critical {{
            background: #e74c3c;
        }}
        .severity-high {{
            background: #f39c12;
        }}
        .severity-medium {{
            background: #f1c40f;
        }}
        .severity-low {{
            background: #27ae60;
        }}
        .issue-details {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        .file-path {{
            font-family: monospace;
            background: #ecf0f1;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        .toggle-button {{
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 10px;
        }}
        .toggle-button:hover {{
            background: #2980b9;
        }}
        .collapsible {{
            display: none;
        }}
        .show {{
            display: block;
        }}
        .progress-bar {{
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            height: 20px;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #f1c40f, #f39c12, #e74c3c);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Java Code Analysis Report</h1>
            <div class="subtitle">Generated on {timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{total_issues}</h3>
                <p>Total Issues</p>
            </div>
            <div class="summary-card critical">
                <h3>{critical_issues}</h3>
                <p>Critical</p>
            </div>
            <div class="summary-card high">
                <h3>{high_issues}</h3>
                <p>High Priority</p>
            </div>
            <div class="summary-card medium">
                <h3>{medium_issues}</h3>
                <p>Medium Priority</p>
            </div>
            <div class="summary-card low">
                <h3>{low_issues}</h3>
                <p>Low Priority</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Analysis Overview</h2>
            <p><strong>Project:</strong> {html.escape(str(analysis_data.get('project_path', 'Unknown')))}</p>
            <p><strong>Analysis Time:</strong> {html.escape(str(analysis_data.get('analysis_time', timestamp)))}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {health_score}%"></div>
            </div>
            <p>Code Health Score: {health_score}%</p>
        </div>
        
        {self.generate_issue_sections(analysis_data)}
    </div>
    
    <script>
        function toggleSection(sectionId) {{
            const section = document.getElementById(sectionId);
            const button = document.getElementById('toggle-' + sectionId);
            
            if (section.classList.contains('show')) {{
                section.classList.remove('show');
                button.textContent = 'Show Details';
            }} else {{
                section.classList.add('show');
                button.textContent = 'Hide Details';
            }}
        }}
    </script>
</body>
</html>"""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {output_path}")
        print(f"Code health score: {health_score}%")
        print(f"Total issues found: {total_issues}")
    
    def generate_issue_sections(self, analysis_data: dict) -> str:
        """Generate HTML sections for all issue types"""
        sections = ''
        
        # Quality Issues Section
        if 'quality_issues' in analysis_data:
            sections += self.generate_issue_section(
                analysis_data['quality_issues'], 
                'Code Quality Issues', 
                'quality'
            )
        
        # Complexity Issues Section
        if 'complexity_issues' in analysis_data:
            sections += self.generate_issue_section(
                analysis_data['complexity_issues'], 
                'Complexity Issues', 
                'complexity'
            )
        
        # Performance Issues Section
        if 'performance_issues' in analysis_data:
            sections += self.generate_issue_section(
                analysis_data['performance_issues'], 
                'Performance Issues', 
                'performance'
            )
        
        # Security Issues Section
        if 'security_issues' in analysis_data:
            sections += self.generate_issue_section(
                analysis_data['security_issues'], 
                'Security Issues', 
                'security'
            )
        
        return sections
    
    def generate_issue_section(self, issues: list, section_title: str, section_id: str) -> str:
        """Generate HTML for a section of issues"""
        if not issues:
            return f'''
            <div class="section">
                <h2>{section_title}</h2>
                <p>No {section_title.lower()} found.</p>
            </div>
            '''
        
        issue_html = ''
        for issue in issues:
            severity = issue.get('severity', 'medium')
            file_path = issue.get('file', 'Unknown file')
            line = issue.get('line', 'Unknown line')
            message = issue.get('message', 'No message')
            
            issue_html += f'''
                <li class="issue-item {severity}">
                    <div class="issue-header">
                        <div class="issue-title">{html.escape(message)}</div>
                        <div class="issue-severity severity-{severity}">{severity.upper()}</div>
                    </div>
                    <div class="issue-details">
                        File: <span class="file-path">{html.escape(file_path)}</span> 
                        Line: {html.escape(str(line))}
                    </div>
                </li>
            '''
        
        return f'''
        <div class="section">
            <h2>{section_title}</h2>
            <button class="toggle-button" onclick="toggleSection('{section_id}')">Show Details ({len(issues)} issues)</button>
            <div id="{section_id}" class="collapsible">
                <ul class="issue-list">
                    {issue_html}
                </ul>
            </div>
        </div>
        '''

def main():
    parser = argparse.ArgumentParser(description='Generate HTML reports from Java analysis results')
    parser.add_argument('--input', required=True, help='Input JSON analysis results')
    parser.add_argument('--output', required=True, help='Output HTML report file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {args.input}")
        return
    
    output_path = Path(args.output)
    
    # Load analysis data
    try:
        with open(input_path, 'r') as f:
            analysis_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return
    
    # Generate report
    reporter = HTMLReporter()
    reporter.generate_report(analysis_data, str(output_path))

if __name__ == '__main__':
    main()