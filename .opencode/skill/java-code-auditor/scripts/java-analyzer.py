#!/usr/bin/env python3
"""
Java Code Analyzer - Main orchestrator for Java code quality analysis
Focuses on code quality, performance, security, and complexity analysis
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

class JavaAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results = {
            'project_path': str(project_path),
            'analysis_time': '',
            'quality_issues': [],
            'complexity_issues': [],
            'performance_issues': [],
            'security_issues': [],
            'summary': {}
        }

    def find_java_files(self) -> List[Path]:
        """Find all Java source files in the project"""
        java_files = []
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix == '.java':
                # Skip test files and generated sources
                if 'test' not in str(file_path).lower() and 'generated' not in str(file_path).lower():
                    java_files.append(file_path)
        print(f"Found Java files: {java_files}")
        return java_files

    def analyze_quality(self, java_files: List[Path]):
        """Analyze code quality issues"""
        print("Analyzing code quality...")
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                # Check method length
                method_matches = re.finditer(r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{', content)
                for match in method_matches:
                    method_start = match.start()
                    brace_count = 0
                    method_length = 0
                    in_method = False
                    
                    for i, char in enumerate(content[method_start:], method_start):
                        if char == '{':
                            brace_count += 1
                            in_method = True
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0 and in_method:
                                method_length = i - method_start
                                break
                    
                    if method_length > 500:  # 50 lines (assuming 10 chars per line average)
                        self.results['quality_issues'].append({
                            'type': 'method_length',
                            'file': str(java_file),
                            'line': content[:method_start].count('\n') + 1,
                            'severity': 'medium',
                            'message': f'Method is too long ({method_length//10} lines)',
                            'method': match.group(1)
                        })

                # Check class size
                class_matches = re.finditer(r'(?:public\s+)?class\s+(\w+)', content)
                for match in class_matches:
                    class_start = match.start()
                    class_content = content[class_start:]
                    
                    # Find class end
                    brace_count = 0
                    class_length = 0
                    for char in class_content:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                break
                        class_length += 1
                    
                    if class_length > 3000:  # Large class
                        self.results['quality_issues'].append({
                            'type': 'class_size',
                            'file': str(java_file),
                            'line': content[:match.start()].count('\n') + 1,
                            'severity': 'medium',
                            'message': f'Class is too large ({class_length//10} lines)',
                            'class': match.group(1)
                        })

            except Exception as e:
                print(f"Error analyzing {java_file}: {e}")

    def analyze_complexity(self, java_files: List[Path]):
        """Analyze cyclomatic and cognitive complexity"""
        print("Analyzing complexity...")
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Calculate cyclomatic complexity
                complexity_keywords = ['if', 'else', 'while', 'for', 'case', 'catch', '&&', '||']
                complexity = 0
                
                for keyword in complexity_keywords:
                    complexity += len(re.findall(r'\b' + keyword + r'\b', content))
                
                # Base complexity is 1
                complexity += 1
                
                if complexity > 10:  # Threshold
                    self.results['complexity_issues'].append({
                        'type': 'cyclomatic_complexity',
                        'file': str(java_file),
                        'severity': 'high' if complexity > 20 else 'medium',
                        'message': f'Cyclomatic complexity is {complexity}',
                        'value': complexity
                    })

            except Exception as e:
                print(f"Error analyzing complexity for {java_file}: {e}")

    def analyze_performance(self, java_files: List[Path]):
        """Analyze performance issues"""
        print("Analyzing performance issues...")
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check for inefficient collection usage
                inefficient_patterns = [
                    (r'new\s+ArrayList\s*\(\)\s*\.add', 'Using ArrayList.add() without initial capacity'),
                    (r'new\s+HashMap\s*\(\)\s*\.put', 'Using HashMap without initial capacity'),
                    (r'String\s*\+\s*String', 'String concatenation in loop'),
                    (r'new\s+String\s*\(', 'Unnecessary String constructor')
                ]
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, message in inefficient_patterns:
                        if re.search(pattern, line):
                            self.results['performance_issues'].append({
                                'type': 'inefficient_pattern',
                                'file': str(java_file),
                                'line': line_num,
                                'severity': 'low',
                                'message': message,
                                'code': line.strip()
                            })

            except Exception as e:
                print(f"Error analyzing performance for {java_file}: {e}")

    def analyze_security(self, java_files: List[Path]):
        """Analyze security vulnerabilities"""
        print("Analyzing security issues...")
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check for hardcoded passwords/keys
                sensitive_patterns = [
                    (r'password\s*=\s*"[^"]*"', 'Hardcoded password'),
                    (r'secret\s*=\s*"[^"]*"', 'Hardcoded secret'),
                    (r'api[_-]?key\s*=\s*"[^"]*"', 'Hardcoded API key'),
                    (r'executeQuery\s*\([^)]*\+', 'Potential SQL injection'),
                    (r'Runtime\.getRuntime\(\)\.exec', 'Command injection risk')
                ]
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, message in sensitive_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.results['security_issues'].append({
                                'type': 'security_vulnerability',
                                'file': str(java_file),
                                'line': line_num,
                                'severity': 'critical',
                                'message': message,
                                'code': line.strip()
                            })

            except Exception as e:
                print(f"Error analyzing security for {java_file}: {e}")

    def generate_summary(self):
        """Generate analysis summary"""
        self.results['summary'] = {
            'total_quality_issues': len(self.results['quality_issues']),
            'total_complexity_issues': len(self.results['complexity_issues']),
            'total_performance_issues': len(self.results['performance_issues']),
            'total_security_issues': len(self.results['security_issues']),
            'total_issues': (
                len(self.results['quality_issues']) +
                len(self.results['complexity_issues']) +
                len(self.results['performance_issues']) +
                len(self.results['security_issues'])
            )
        }

    def run_full_analysis(self):
        """Run complete analysis"""
        from datetime import datetime
        self.results['analysis_time'] = datetime.now().isoformat()
        
        java_files = self.find_java_files()
        print(f"Found {len(java_files)} Java files")
        
        if not java_files:
            print("No Java files found in the specified directory")
            return
        
        self.analyze_quality(java_files)
        self.analyze_complexity(java_files)
        self.analyze_performance(java_files)
        self.analyze_security(java_files)
        self.generate_summary()

def main():
    parser = argparse.ArgumentParser(description='Java Code Quality Analyzer')
    parser.add_argument('--project', required=True, help='Path to Java project')
    parser.add_argument('--output', help='Output file for analysis results (JSON)')
    parser.add_argument('--quality', action='store_true', help='Run quality analysis only')
    parser.add_argument('--complexity', action='store_true', help='Run complexity analysis only')
    parser.add_argument('--performance', action='store_true', help='Run performance analysis only')
    parser.add_argument('--security', action='store_true', help='Run security analysis only')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project):
        print(f"Error: Project directory '{args.project}' does not exist")
        sys.exit(1)
    
    analyzer = JavaAnalyzer(args.project)
    
    if args.quality:
        java_files = analyzer.find_java_files()
        analyzer.analyze_quality(java_files)
        analyzer.generate_summary()
    elif args.complexity:
        java_files = analyzer.find_java_files()
        analyzer.analyze_complexity(java_files)
        analyzer.generate_summary()
    elif args.performance:
        java_files = analyzer.find_java_files()
        analyzer.analyze_performance(java_files)
        analyzer.generate_summary()
    elif args.security:
        java_files = analyzer.find_java_files()
        analyzer.analyze_security(java_files)
        analyzer.generate_summary()
    else:
        analyzer.run_full_analysis()
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(analyzer.results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(analyzer.results, indent=2))

if __name__ == '__main__':
    main()