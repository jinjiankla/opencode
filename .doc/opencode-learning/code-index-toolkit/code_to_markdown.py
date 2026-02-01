#!/usr/bin/env python3
"""
代码转 Markdown 工具
支持 Python, JavaScript, TypeScript, Java 等
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class CodeParser:
    """代码解析器基类"""
    
    def parse(self, code: str, filename: str) -> Dict:
        """解析代码，返回树结构"""
        raise NotImplementedError


class PythonParser(CodeParser):
    """Python 代码解析器"""
    
    def parse(self, code: str, filename: str) -> Dict:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "title": filename,
                "error": f"语法错误: {str(e)}",
                "nodes": []
            }
        
        result = {
            "title": filename,
            "type": "python",
            "nodes": []
        }
        
        # 提取模块级别的 docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            result["description"] = module_doc
        
        # 遍历顶层节点
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                result["nodes"].append(self._parse_class(node))
            elif isinstance(node, ast.FunctionDef):
                result["nodes"].append(self._parse_function(node))
            elif isinstance(node, ast.AsyncFunctionDef):
                result["nodes"].append(self._parse_function(node, is_async=True))
        
        return result
    
    def _parse_class(self, node: ast.ClassDef) -> Dict:
        """解析类"""
        class_info = {
            "title": f"Class: {node.name}",
            "type": "class",
            "line": node.lineno,
            "nodes": []
        }
        
        # 类的 docstring
        docstring = ast.get_docstring(node)
        if docstring:
            class_info["description"] = docstring
        
        # 基类
        if node.bases:
            bases = [self._get_name(base) for base in node.bases]
            class_info["bases"] = bases
        
        # 类的方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info["nodes"].append(self._parse_function(item, is_method=True))
            elif isinstance(item, ast.AsyncFunctionDef):
                class_info["nodes"].append(self._parse_function(item, is_method=True, is_async=True))
        
        return class_info
    
    def _parse_function(self, node, is_method=False, is_async=False) -> Dict:
        """解析函数或方法"""
        prefix = "Method" if is_method else "Function"
        if is_async:
            prefix = f"Async {prefix}"
        
        func_info = {
            "title": f"{prefix}: {node.name}",
            "type": "method" if is_method else "function",
            "line": node.lineno
        }
        
        # 函数的 docstring
        docstring = ast.get_docstring(node)
        if docstring:
            func_info["description"] = docstring
        
        # 参数
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        if args:
            func_info["args"] = args
        
        # 返回类型注解
        if node.returns:
            func_info["returns"] = self._get_name(node.returns)
        
        return func_info
    
    def _get_name(self, node) -> str:
        """获取节点的名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        else:
            return str(node)


class JavaScriptParser(CodeParser):
    """JavaScript/TypeScript 代码解析器（简化版）"""
    
    def parse(self, code: str, filename: str) -> Dict:
        result = {
            "title": filename,
            "type": "javascript",
            "nodes": []
        }
        
        lines = code.split('\n')
        
        # 简单的正则匹配
        class_pattern = re.compile(r'^\s*class\s+(\w+)')
        function_pattern = re.compile(r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)')
        method_pattern = re.compile(r'^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*{')
        
        current_class = None
        
        for i, line in enumerate(lines, 1):
            # 类
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                current_class = {
                    "title": f"Class: {class_name}",
                    "type": "class",
                    "line": i,
                    "nodes": []
                }
                result["nodes"].append(current_class)
                continue
            
            # 函数
            func_match = function_pattern.match(line)
            if func_match:
                func_name = func_match.group(1)
                result["nodes"].append({
                    "title": f"Function: {func_name}",
                    "type": "function",
                    "line": i
                })
                continue
            
            # 方法（在类内部）
            if current_class and method_pattern.match(line):
                method_match = method_pattern.match(line)
                method_name = method_match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch']:
                    current_class["nodes"].append({
                        "title": f"Method: {method_name}",
                        "type": "method",
                        "line": i
                    })
        
        return result


class JavaParser(CodeParser):
    """Java 代码解析器"""
    
    def parse(self, code: str, filename: str) -> Dict:
        result = {
            "title": filename,
            "type": "java",
            "nodes": []
        }
        
        lines = code.split('\n')
        
        # 正则模式
        package_pattern = re.compile(r'^\s*package\s+([\w.]+);')
        import_pattern = re.compile(r'^\s*import\s+([\w.]+);')
        class_pattern = re.compile(r'^\s*(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(?:class|interface|enum)\s+(\w+)')
        method_pattern = re.compile(r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\(')
        field_pattern = re.compile(r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*[;=]')
        
        current_package = None
        current_class = None
        imports = []
        
        for i, line in enumerate(lines, 1):
            # Package
            package_match = package_pattern.match(line)
            if package_match:
                current_package = package_match.group(1)
                result["package"] = current_package
                continue
            
            # Import
            import_match = import_pattern.match(line)
            if import_match:
                imports.append(import_match.group(1))
                continue
            
            # Class/Interface/Enum
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                class_type = "interface" if "interface" in line else "enum" if "enum" in line else "class"
                current_class = {
                    "title": f"{class_type.capitalize()}: {class_name}",
                    "type": class_type,
                    "line": i,
                    "nodes": []
                }
                
                # 提取继承和实现
                if "extends" in line:
                    extends_match = re.search(r'extends\s+([\w<>,.]+)', line)
                    if extends_match:
                        current_class["extends"] = extends_match.group(1).strip()
                
                if "implements" in line:
                    implements_match = re.search(r'implements\s+([\w<>,.]+)', line)
                    if implements_match:
                        current_class["implements"] = implements_match.group(1).strip()
                
                result["nodes"].append(current_class)
                continue
            
            # Method
            if current_class:
                method_match = method_pattern.match(line)
                if method_match:
                    method_name = method_match.group(1)
                    # 跳过构造函数（与类名相同）
                    if method_name == current_class["title"].split(": ")[1]:
                        method_type = "Constructor"
                    else:
                        method_type = "Method"
                    
                    # 提取修饰符
                    modifiers = []
                    if "public" in line:
                        modifiers.append("public")
                    elif "private" in line:
                        modifiers.append("private")
                    elif "protected" in line:
                        modifiers.append("protected")
                    if "static" in line:
                        modifiers.append("static")
                    if "final" in line:
                        modifiers.append("final")
                    
                    method_info = {
                        "title": f"{method_type}: {method_name}",
                        "type": "method",
                        "line": i
                    }
                    
                    if modifiers:
                        method_info["modifiers"] = " ".join(modifiers)
                    
                    current_class["nodes"].append(method_info)
                    continue
                
                # Field
                field_match = field_pattern.match(line)
                if field_match and not method_pattern.match(line):
                    field_name = field_match.group(1)
                    current_class["nodes"].append({
                        "title": f"Field: {field_name}",
                        "type": "field",
                        "line": i
                    })
        
        if imports:
            result["imports"] = imports[:10]  # 只保留前 10 个
        
        return result


class KotlinParser(CodeParser):
    """Kotlin 代码解析器"""
    
    def parse(self, code: str, filename: str) -> Dict:
        result = {
            "title": filename,
            "type": "kotlin",
            "nodes": []
        }
        
        lines = code.split('\n')
        
        # 正则模式
        package_pattern = re.compile(r'^\s*package\s+([\w.]+)')
        import_pattern = re.compile(r'^\s*import\s+([\w.]+)')
        class_pattern = re.compile(r'^\s*(?:open\s+)?(?:abstract\s+)?(?:data\s+)?(?:sealed\s+)?(?:class|interface|object|enum class)\s+(\w+)')
        function_pattern = re.compile(r'^\s*(?:private\s+)?(?:public\s+)?(?:protected\s+)?(?:internal\s+)?(?:suspend\s+)?(?:inline\s+)?fun\s+(\w+)\s*\(')
        property_pattern = re.compile(r'^\s*(?:private\s+)?(?:public\s+)?(?:protected\s+)?(?:val|var)\s+(\w+)\s*[:=]')
        
        current_package = None
        current_class = None
        imports = []
        
        for i, line in enumerate(lines, 1):
            # Package
            package_match = package_pattern.match(line)
            if package_match:
                current_package = package_match.group(1)
                result["package"] = current_package
                continue
            
            # Import
            import_match = import_pattern.match(line)
            if import_match:
                imports.append(import_match.group(1))
                continue
            
            # Class/Interface/Object
            class_match = class_pattern.match(line)
            if class_match:
                class_name = class_match.group(1)
                
                # 确定类型
                if "data class" in line:
                    class_type = "data class"
                elif "sealed class" in line:
                    class_type = "sealed class"
                elif "object" in line:
                    class_type = "object"
                elif "interface" in line:
                    class_type = "interface"
                elif "enum class" in line:
                    class_type = "enum class"
                else:
                    class_type = "class"
                
                current_class = {
                    "title": f"{class_type.capitalize()}: {class_name}",
                    "type": class_type.replace(" ", "_"),
                    "line": i,
                    "nodes": []
                }
                
                # 提取继承
                if ":" in line and "{" in line:
                    inheritance = line.split(":")[1].split("{")[0].strip()
                    if inheritance:
                        current_class["inherits"] = inheritance
                
                result["nodes"].append(current_class)
                continue
            
            # Function
            function_match = function_pattern.match(line)
            if function_match:
                func_name = function_match.group(1)
                
                # 提取修饰符
                modifiers = []
                if "private" in line:
                    modifiers.append("private")
                elif "protected" in line:
                    modifiers.append("protected")
                elif "internal" in line:
                    modifiers.append("internal")
                if "suspend" in line:
                    modifiers.append("suspend")
                if "inline" in line:
                    modifiers.append("inline")
                
                func_info = {
                    "title": f"Function: {func_name}",
                    "type": "function",
                    "line": i
                }
                
                if modifiers:
                    func_info["modifiers"] = " ".join(modifiers)
                
                if current_class:
                    current_class["nodes"].append(func_info)
                else:
                    result["nodes"].append(func_info)
                continue
            
            # Property
            if current_class:
                property_match = property_pattern.match(line)
                if property_match:
                    prop_name = property_match.group(1)
                    prop_type = "val" if "val" in line else "var"
                    current_class["nodes"].append({
                        "title": f"Property: {prop_name} ({prop_type})",
                        "type": "property",
                        "line": i
                    })
        
        if imports:
            result["imports"] = imports[:10]
        
        return result


class MarkdownGenerator:
    """Markdown 生成器"""
    
    def generate(self, tree: Dict) -> str:
        """从树结构生成 Markdown"""
        lines = []
        
        # 标题
        lines.append(f"# {tree['title']}\n")
        
        # 描述
        if "description" in tree:
            lines.append(f"\n{tree['description']}\n")
        
        # 错误信息
        if "error" in tree:
            lines.append(f"\n**错误**: {tree['error']}\n")
            return "\n".join(lines)
        
        # 节点
        for node in tree.get("nodes", []):
            self._generate_node(node, lines, level=2)
        
        return "\n".join(lines)
    
    def _generate_node(self, node: Dict, lines: List[str], level: int):
        """生成节点的 Markdown"""
        # 标题
        prefix = "#" * level
        title = node["title"]
        line_info = f" (Line {node['line']})" if "line" in node else ""
        lines.append(f"\n{prefix} {title}{line_info}\n")
        
        # 描述
        if "description" in node:
            lines.append(f"\n{node['description']}\n")
        
        # 基类
        if "bases" in node:
            bases = ", ".join(node["bases"])
            lines.append(f"\n**继承自**: {bases}\n")
        
        # 参数
        if "args" in node:
            args = ", ".join(node["args"])
            lines.append(f"\n**参数**: `{args}`\n")
        
        # 返回类型
        if "returns" in node:
            lines.append(f"\n**返回**: `{node['returns']}`\n")
        
        # 子节点
        for child in node.get("nodes", []):
            self._generate_node(child, lines, level + 1)


def get_parser(filename: str) -> Optional[CodeParser]:
    """根据文件扩展名获取解析器"""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.py':
        return PythonParser()
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return JavaScriptParser()
    elif ext == '.java':
        return JavaParser()
    elif ext in ['.kt', '.kts']:
        return KotlinParser()
    else:
        return None


def convert_file(input_path: str, output_path: str) -> bool:
    """转换单个文件"""
    try:
        # 读取代码
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 获取解析器
        parser = get_parser(input_path)
        if not parser:
            print(f"⚠️  不支持的文件类型: {input_path}")
            return False
        
        # 解析代码
        filename = os.path.basename(input_path)
        tree = parser.parse(code, filename)
        
        # 生成 Markdown
        generator = MarkdownGenerator()
        markdown = generator.generate(tree)
        
        # 写入文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✅ {input_path} → {output_path}")
        return True
    
    except Exception as e:
        print(f"❌ 转换失败 {input_path}: {str(e)}")
        return False


def convert_directory(input_dir: str, output_dir: str, extensions: List[str] = None):
    """转换整个目录"""
    if extensions is None:
        extensions = ['.py', '.js', '.jsx', '.ts', '.tsx']
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    success_count = 0
    fail_count = 0
    
    # 遍历所有文件
    for ext in extensions:
        for file_path in input_path.rglob(f"*{ext}"):
            # 跳过隐藏文件和特殊目录
            if any(part.startswith('.') for part in file_path.parts):
                continue
            if any(part in ['node_modules', '__pycache__', 'venv', 'dist', 'build'] for part in file_path.parts):
                continue
            
            # 计算相对路径
            rel_path = file_path.relative_to(input_path)
            out_file = output_path / rel_path.with_suffix('.md')
            
            # 转换
            if convert_file(str(file_path), str(out_file)):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n📊 转换完成: {success_count} 成功, {fail_count} 失败")


def main():
    parser = argparse.ArgumentParser(
        description='将代码文件转换为 Markdown 格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个文件
  python3 code_to_markdown.py -i mycode.py -o mycode.md
  
  # 转换整个目录
  python3 code_to_markdown.py -i src/ -o docs/code/
  
  # 只转换 Python 文件
  python3 code_to_markdown.py -i src/ -o docs/code/ -e .py
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                        help='输入文件或目录')
    parser.add_argument('-o', '--output', required=True,
                        help='输出文件或目录')
    parser.add_argument('-e', '--extensions', nargs='+',
                        default=['.java', '.kt', '.py', '.js', '.ts'],
                        help='要处理的文件扩展名 (默认: .java .kt .py .js .ts)')
    
    args = parser.parse_args()
    
    input_path = args.input
    output_path = args.output
    
    if os.path.isfile(input_path):
        # 转换单个文件
        convert_file(input_path, output_path)
    elif os.path.isdir(input_path):
        # 转换目录
        convert_directory(input_path, output_path, args.extensions)
    else:
        print(f"❌ 输入路径不存在: {input_path}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
