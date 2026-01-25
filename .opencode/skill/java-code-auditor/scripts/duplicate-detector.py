#!/usr/bin/env python3
"""
Duplicate Code Detector - Find duplicate code blocks in Java projects
Uses similarity detection to identify potentially duplicated code
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse
import json
from difflib import SequenceMatcher

class DuplicateDetector:
    def __init__(self, min_lines: int = 5, similarity_threshold: float = 0.8):
        self.min_lines = min_lines
        self.similarity_threshold = similarity_threshold
        self.duplicates = []
        
    def normalize_code(self, code: str) -> str:
        """Normalize code by removing comments, extra whitespace, and formatting"""
        # Remove single-line comments
        code = re.sub(r'//.*', '', code)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        # Remove leading/trailing whitespace
        code = code.strip()
        return code
    
    def extract_code_blocks(self, content: str) -> List[Tuple[str, int, int]]:
        """Extract code blocks from a file"""
        lines = content.split('\n')
        blocks = []
        
        # Simple approach: extract blocks of consecutive non-empty lines
        start_line = 0
        block_lines = []
        
        for i, line in enumerate(lines):
            if line.strip():  # Non-empty line
                if not block_lines:
                    start_line = i
                block_lines.append(line)
            else:
                if len(block_lines) >= self.min_lines:
                    block_content = '\n'.join(block_lines)
                    normalized = self.normalize_code(block_content)
                    if normalized:  # Only add if not empty after normalization
                        blocks.append((normalized, start_line, i - 1))
                block_lines = []
        
        # Handle the last block
        if len(block_lines) >= self.min_lines:
            block_content = '\n'.join(block_lines)
            normalized = self.normalize_code(block_content)
            if normalized:
                blocks.append((normalized, start_line, len(lines) - 1))
        
        return blocks
    
    def calculate_similarity(self, block1: str, block2: str) -> float:
        """Calculate similarity between two code blocks"""
        return SequenceMatcher(None, block1, block2).ratio()
    
    def find_hash_duplicates(self, all_blocks: List[Tuple[str, int, int, str]]) -> List[Dict]:
        """Find exact duplicates using hash comparison"""
        hash_map = {}
        duplicates = []
        
        for block_hash, start_line, end_line, file_path in all_blocks:
            if block_hash in hash_map:
                # Found a duplicate
                original = hash_map[block_hash]
                duplicates.append({
                    'type': 'exact_duplicate',
                    'similarity': 1.0,
                    'block1': {
                        'file': original[2],
                        'start_line': original[0],
                        'end_line': original[1]
                    },
                    'block2': {
                        'file': file_path,
                        'start_line': start_line,
                        'end_line': end_line
                    }
                })
            else:
                hash_map[block_hash] = (start_line, end_line, file_path)
        
        return duplicates
    
    def find_similar_duplicates(self, all_blocks: List[Tuple[str, int, int, str]]) -> List[Dict]:
        """Find similar (not exact) duplicates"""
        duplicates = []
        processed = set()
        
        for i, (block1, start1, end1, file1) in enumerate(all_blocks):
            if i in processed:
                continue
                
            for j, (block2, start2, end2, file2) in enumerate(all_blocks[i+1:], i+1):
                if j in processed:
                    continue
                
                # Skip if same file and overlapping
                if file1 == file2 and not (end1 < start2 or end2 < start1):
                    continue
                
                similarity = self.calculate_similarity(block1, block2)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append({
                        'type': 'similar_duplicate',
                        'similarity': similarity,
                        'block1': {
                            'file': file1,
                            'start_line': start1,
                            'end_line': end1
                        },
                        'block2': {
                            'file': file2,
                            'start_line': start2,
                            'end_line': end2
                        }
                    })
                    processed.add(j)
            
            processed.add(i)
        
        return duplicates
    
    def analyze_file(self, file_path: Path) -> List[Tuple[str, int, int, str]]:
        """Analyze a single file and return its code blocks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        blocks = self.extract_code_blocks(content)
        file_blocks = []
        
        for normalized_block, start_line, end_line in blocks:
            # Create hash for exact duplicate detection
            block_hash = hashlib.md5(normalized_block.encode()).hexdigest()
            file_blocks.append((normalized_block, start_line, end_line, str(file_path)))
        
        return file_blocks
    
    def analyze_project(self, project_path: Path) -> Dict:
        """Analyze entire project for duplicate code"""
        java_files = []
        for root in project_path.rglob('*.java'):
            if 'test' not in str(root).lower():
                java_files.append(root)
        
        print(f"Analyzing {len(java_files)} Java files for duplicates...")
        
        all_blocks = []
        file_results = {}
        
        for java_file in java_files:
            blocks = self.analyze_file(java_file)
            all_blocks.extend(blocks)
            file_results[str(java_file)] = len(blocks)
        
        print(f"Found {len(all_blocks)} code blocks")
        
        # Find exact duplicates
        exact_duplicates = self.find_hash_duplicates(all_blocks)
        print(f"Found {len(exact_duplicates)} exact duplicates")
        
        # Find similar duplicates
        similar_duplicates = self.find_similar_duplicates(all_blocks)
        print(f"Found {len(similar_duplicates)} similar duplicates")
        
        all_duplicates = exact_duplicates + similar_duplicates
        
        # Sort by similarity (highest first)
        all_duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'project_path': str(project_path),
            'files_analyzed': len(java_files),
            'total_blocks': len(all_blocks),
            'exact_duplicates': len(exact_duplicates),
            'similar_duplicates': len(similar_duplicates),
            'total_duplicates': len(all_duplicates),
            'duplicates': all_duplicates,
            'file_block_counts': file_results
        }

def main():
    parser = argparse.ArgumentParser(description='Java Duplicate Code Detector')
    parser.add_argument('--project', required=True, help='Path to Java project')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--min-lines', type=int, default=5, help='Minimum lines for a code block')
    parser.add_argument('--threshold', type=float, default=0.8, help='Similarity threshold (0.0-1.0)')
    
    args = parser.parse_args()
    
    detector = DuplicateDetector(args.min_lines, args.threshold)
    
    project_path = Path(args.project)
    if not project_path.exists():
        print(f"Project directory not found: {args.project}")
        return
    
    results = detector.analyze_project(project_path)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))
        
        # Print summary
        print(f"\nDuplicate Code Analysis Summary:")
        print(f"Files analyzed: {results['files_analyzed']}")
        print(f"Total code blocks: {results['total_blocks']}")
        print(f"Exact duplicates: {results['exact_duplicates']}")
        print(f"Similar duplicates: {results['similar_duplicates']}")
        print(f"Total duplicates: {results['total_duplicates']}")
        
        # Show top duplicates
        if results['duplicates']:
            print(f"\nTop 10 duplicates:")
            for i, dup in enumerate(results['duplicates'][:10]):
                print(f"{i+1}. Similarity: {dup['similarity']:.2f}")
                print(f"   File 1: {dup['block1']['file']} (lines {dup['block1']['start_line']}-{dup['block1']['end_line']})")
                print(f"   File 2: {dup['block2']['file']} (lines {dup['block2']['start_line']}-{dup['block2']['end_line']})")
                print()

if __name__ == '__main__':
    main()