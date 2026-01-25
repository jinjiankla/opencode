#!/usr/bin/env python3
"""
Complexity Checker - Specialized tool for analyzing Java code complexity
Focuses on cyclomatic and cognitive complexity metrics
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import json

class ComplexityChecker:
    def __init__(self, threshold: int = 10):
        self.threshold = threshold
        self.issues = []
        
        # Complexity keywords and their weights
        self.complexity_operators = {
            'if': 1, 'else': 1, 'while': 1, 'for': 1, 'case': 1,
            'catch': 1, '&&': 1, '||': 1, '?:': 1
        }
        
        # Cognitive complexity patterns
        self.cognitive_patterns = [
            (r'\bif\b', 1),
            (r'\belse\b', 1),
            (r'\bwhile\b', 1),
            (r'\bfor\b', 1),
            (r'\bswitch\b', 1),
            (r'\bcase\b', 1),
            (r'\bcatch\b', 1),
            (r'\bbreak\b', 1),
            (r'\bcontinue\b', 1),
            (r'\bgoto\b', 1),
            (r'\?\s*[^:]+\s*:', 1),  # Ternary operator
            (r'\b&&\b', 1),
            (r'\|\|\b', 1)
        ]

    def calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calculate cyclomatic complexity using McCabe's method"""
        complexity = 1  # Base complexity
        
        for operator in self.complexity_operators:
            pattern = r'\b' + operator + r'\b'
            matches = re.findall(pattern, content)
            complexity += len(matches) * self.complexity_operators[operator]
        
        return complexity

    def calculate_cognitive_complexity(self, content: str) -> int:
        """Calculate cognitive complexity (SonarQube method)"""
        complexity = 0
        nesting_level = 0
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue
            
            # Check for nesting increases
            if any(keyword in line for keyword in ['if', 'while', 'for', 'catch', 'switch']):
                nesting_level += 1
                complexity += 1 + nesting_level
            elif 'else' in line and 'if' not in line:
                complexity += 1 + nesting_level
            elif line.startswith('case'):
                complexity += 1
            elif any(op in line for op in ['&&', '||', '?:']):
                complexity += 1
            
            # Check for nesting decreases
            if line == '}':
                nesting_level = max(0, nesting_level - 1)
        
        return complexity

    def find_methods(self, content: str) -> List[Tuple[str, int, int]]:
        """Find all methods with their start and end positions"""
        methods = []
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:abstract\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{'
        
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            method_start = match.start()
            
            # Find method end by matching braces
            brace_count = 0
            method_end = method_start
            for i, char in enumerate(content[method_start:], method_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        method_end = i + 1
                        break
            
            methods.append((method_name, method_start, method_end))
        
        return methods

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single Java file for complexity issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e)}
        
        file_issues = []
        methods = self.find_methods(content)
        
        # Analyze each method
        for method_name, start, end in methods:
            method_content = content[start:end]
            
            # Calculate complexities
            cyclomatic = self.calculate_cyclomatic_complexity(method_content)
            cognitive = self.calculate_cognitive_complexity(method_content)
            
            # Check against thresholds
            if cyclomatic > self.threshold:
                line_num = content[:start].count('\n') + 1
                severity = 'critical' if cyclomatic > 20 else 'high' if cyclomatic > 15 else 'medium'
                
                file_issues.append({
                    'type': 'cyclomatic_complexity',
                    'method': method_name,
                    'file': str(file_path),
                    'line': line_num,
                    'severity': severity,
                    'value': cyclomatic,
                    'message': f'Method {method_name} has cyclomatic complexity of {cyclomatic} (threshold: {self.threshold})'
                })
            
            if cognitive > self.threshold:
                line_num = content[:start].count('\n') + 1
                severity = 'critical' if cognitive > 20 else 'high' if cognitive > 15 else 'medium'
                
                file_issues.append({
                    'type': 'cognitive_complexity',
                    'method': method_name,
                    'file': str(file_path),
                    'line': line_num,
                    'severity': severity,
                    'value': cognitive,
                    'message': f'Method {method_name} has cognitive complexity of {cognitive} (threshold: {self.threshold})'
                })
        
        # Also check overall file complexity
        total_cyclomatic = self.calculate_cyclomatic_complexity(content)
        total_cognitive = self.calculate_cognitive_complexity(content)
        
        return {
            'file': str(file_path),
            'total_cyclomatic': total_cyclomatic,
            'total_cognitive': total_cognitive,
            'method_count': len(methods),
            'issues': file_issues
        }

    def analyze_project(self, project_path: Path) -> Dict:
        """Analyze entire Java project"""
        java_files = []
        for root in project_path.rglob('*.java'):
            if 'test' not in str(root).lower():
                java_files.append(root)
        
        results = {
            'project_path': str(project_path),
            'files_analyzed': len(java_files),
            'files': [],
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0
            }
        }
        
        for java_file in java_files:
            file_result = self.analyze_file(java_file)
            results['files'].append(file_result)
            
            if 'issues' in file_result:
                for issue in file_result['issues']:
                    results['summary']['total_issues'] += 1
                    results['summary'][f"{issue['severity']}_issues"] += 1
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Java Complexity Checker')
    parser.add_argument('--project', required=True, help='Path to Java project')
    parser.add_argument('--threshold', type=int, default=10, help='Complexity threshold (default: 10)')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--method', help='Analyze specific method name')
    parser.add_argument('--file', help='Analyze specific file')
    
    args = parser.parse_args()
    
    checker = ComplexityChecker(args.threshold)
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"File not found: {args.file}")
            return
        
        result = checker.analyze_file(file_path)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
    else:
        project_path = Path(args.project)
        if not project_path.exists():
            print(f"Project directory not found: {args.project}")
            return
        
        results = checker.analyze_project(project_path)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            print(json.dumps(results, indent=2))
            
            # Print summary
            summary = results['summary']
            print(f"\nComplexity Analysis Summary:")
            print(f"Files analyzed: {results['files_analyzed']}")
            print(f"Total issues: {summary['total_issues']}")
            print(f"Critical: {summary['critical_issues']}")
            print(f"High: {summary['high_issues']}")
            print(f"Medium: {summary['medium_issues']}")

if __name__ == '__main__':
    main()