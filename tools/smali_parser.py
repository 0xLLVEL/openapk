import os
import re
import sys
from pathlib import Path
from typing import Optional
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class SmaliParser:
    def __init__(self):
        self.decoded_dir = config.DECODED_DIR

    def parse_smali_file(self, smali_path: str) -> dict:
        if not os.path.exists(smali_path):
            return {"success": False, "error": f"File not found: {smali_path}"}

        try:
            with open(smali_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            result = {
                "success": True,
                "path": smali_path,
                "class_name": self._extract_class_name(content),
                "super_class": self._extract_super_class(content),
                "interfaces": self._extract_interfaces(content),
                "fields": self._extract_fields(content),
                "methods": self._extract_methods(content),
                "annotations": self._extract_annotations(content),
                "source_file": self._extract_source_file(content),
                "line_count": len(content.splitlines()),
            }
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_classes(self, apk_name: str, pattern: str = "") -> dict:
        smali_dir = self.decoded_dir / apk_name / "smali"
        if not smali_dir.exists():
            return {"success": False, "error": f"Smali directory not found: {apk_name}"}

        classes = []
        for smali_file in smali_dir.rglob("*.smali"):
            if pattern and pattern.lower() not in str(smali_file).lower():
                continue
            rel_path = smali_file.relative_to(smali_dir)
            class_name = str(rel_path).replace(os.sep, ".").replace("/", ".").replace(".smali", "")
            classes.append({
                "class": class_name,
                "path": str(smali_file),
                "size": smali_file.stat().st_size,
            })

        return {"success": True, "apk": apk_name, "count": len(classes), "classes": classes}

    def search_smali(self, apk_name: str, pattern: str, search_type: str = "all") -> dict:
        smali_dir = self.decoded_dir / apk_name / "smali"
        if not smali_dir.exists():
            return {"success": False, "error": f"Smali directory not found: {apk_name}"}

        results = []
        regex = re.compile(pattern, re.IGNORECASE)

        for smali_file in smali_dir.rglob("*.smali"):
            try:
                with open(smali_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                matches = []
                for i, line in enumerate(lines, 1):
                    if regex.search(line):
                        matches.append({"line": i, "content": line.strip()})

                if matches:
                    results.append({
                        "file": str(smali_file),
                        "matches": matches[:10],
                        "total_matches": len(matches),
                    })
            except Exception:
                continue

        return {"success": True, "pattern": pattern, "files_found": len(results), "results": results[:50]}

    def get_method_xref(self, apk_name: str, class_name: str, method_name: str) -> dict:
        smali_dir = self.decoded_dir / apk_name / "smali"
        if not smali_dir.exists():
            return {"success": False, "error": f"Smali directory not found: {apk_name}"}

        references = []
        pattern = re.compile(rf"invoke.*{class_name}.*{method_name}", re.IGNORECASE)

        for smali_file in smali_dir.rglob("*.smali"):
            try:
                with open(smali_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    if pattern.search(line):
                        rel_path = smali_file.relative_to(smali_dir)
                        caller_class = str(rel_path).replace(os.sep, ".").replace("/", ".").replace(".smali", "")
                        references.append({
                            "caller": caller_class,
                            "line": i,
                            "instruction": line.strip(),
                        })
            except Exception:
                continue

        return {
            "success": True,
            "target": f"{class_name}->{method_name}",
            "references": references[:100],
            "total": len(references),
        }

    def get_field_xref(self, apk_name: str, class_name: str, field_name: str) -> dict:
        smali_dir = self.decoded_dir / apk_name / "smali"
        if not smali_dir.exists():
            return {"success": False, "error": f"Smali directory not found: {apk_name}"}

        references = []
        pattern = re.compile(rf"(iget|iput|sget|sput|aget|aput).*{class_name}.*{field_name}", re.IGNORECASE)

        for smali_file in smali_dir.rglob("*.smali"):
            try:
                with open(smali_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    if pattern.search(line):
                        rel_path = smali_file.relative_to(smali_dir)
                        caller_class = str(rel_path).replace(os.sep, ".").replace("/", ".").replace(".smali", "")
                        references.append({
                            "caller": caller_class,
                            "line": i,
                            "instruction": line.strip(),
                        })
            except Exception:
                continue

        return {
            "success": True,
            "target": f"{class_name}->{field_name}",
            "references": references[:100],
            "total": len(references),
        }

    def get_smali_code(self, smali_path: str, start_line: int = 1, end_line: int = 0) -> dict:
        if not os.path.exists(smali_path):
            return {"success": False, "error": f"File not found: {smali_path}"}

        try:
            with open(smali_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            if end_line == 0:
                end_line = len(lines)

            code = []
            for i, line in enumerate(lines[start_line - 1:end_line], start_line):
                code.append({"line": i, "content": line.rstrip()})

            return {"success": True, "path": smali_path, "total_lines": len(lines), "code": code}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_method(self, smali_path: str, method_name: str) -> dict:
        if not os.path.exists(smali_path):
            return {"success": False, "error": f"File not found: {smali_path}"}

        try:
            with open(smali_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            in_method = False
            method_lines = []
            brace_depth = 0

            for i, line in enumerate(lines):
                stripped = line.strip()

                if stripped.startswith(".method") and method_name in stripped:
                    in_method = True
                    method_lines.append(stripped)
                    continue

                if in_method:
                    method_lines.append(stripped)
                    if stripped == ".end method":
                        break

            if not method_lines:
                return {"success": False, "error": f"Method not found: {method_name}"}

            method_text = "\n".join(method_lines)
            header_match = re.search(r"\.method\s+(.*?)\s+" + re.escape(method_name) + r"\((.*?)\)(.*?)$", method_text, re.MULTILINE)

            if not header_match:
                return {"success": False, "error": f"Could not parse method: {method_name}"}

            access_flags = header_match.group(1).strip()
            params = header_match.group(2).strip()
            return_type = header_match.group(3).strip()

            instructions = []
            for line in method_lines[1:-1]:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("."):
                    instructions.append(line)

            registers = set()
            for instr in instructions:
                regs = re.findall(r"[vp]\d+", instr)
                registers.update(regs)

            return {
                "success": True,
                "method": method_name,
                "access_flags": access_flags,
                "parameters": params,
                "return_type": return_type,
                "instruction_count": len(instructions),
                "registers": sorted(registers),
                "instructions": instructions,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_apk_stats(self, apk_name: str) -> dict:
        smali_dir = self.decoded_dir / apk_name / "smali"
        if not smali_dir.exists():
            return {"success": False, "error": f"Smali directory not found: {apk_name}"}

        total_files = 0
        total_lines = 0
        total_methods = 0
        total_fields = 0
        packages = defaultdict(int)

        for smali_file in smali_dir.rglob("*.smali"):
            total_files += 1
            try:
                with open(smali_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                total_lines += len(content.splitlines())
                total_methods += len(re.findall(r"^\.method ", content, re.MULTILINE))
                total_fields += len(re.findall(r"^\.field ", content, re.MULTILINE))

                rel_path = smali_file.relative_to(smali_dir)
                parts = list(rel_path.parts[:-1])
                if parts:
                    packages[".".join(parts)] += 1
            except Exception:
                continue

        return {
            "success": True,
            "apk": apk_name,
            "total_files": total_files,
            "total_lines": total_lines,
            "total_methods": total_methods,
            "total_fields": total_fields,
            "top_packages": dict(sorted(packages.items(), key=lambda x: x[1], reverse=True)[:20]),
        }

    def _extract_class_name(self, content: str) -> str:
        match = re.search(r"^\.class\s+(.*?)$", content, re.MULTILINE)
        if match:
            parts = match.group(1).strip().split()
            return parts[-1] if parts else ""
        return ""

    def _extract_super_class(self, content: str) -> str:
        match = re.search(r"^\.super\s+(.*?)$", content, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _extract_interfaces(self, content: str) -> list:
        return re.findall(r"^\.implements\s+(.*?)$", content, re.MULTILINE)

    def _extract_fields(self, content: str) -> list:
        fields = []
        for match in re.finditer(r"^\.field\s+(.*?)$", content, re.MULTILINE):
            parts = match.group(1).strip().split()
            if len(parts) >= 2:
                fields.append({
                    "access_flags": parts[0],
                    "name": parts[1].split(":")[0] if ":" in parts[1] else parts[1],
                    "type": parts[1].split(":")[1] if ":" in parts[1] else (parts[2] if len(parts) > 2 else ""),
                })
        return fields

    def _extract_methods(self, content: str) -> list:
        methods = []
        for match in re.finditer(r"^\.method\s+(.*?)$", content, re.MULTILINE):
            parts = match.group(1).strip().split("(")
            if len(parts) >= 1:
                method_parts = parts[0].strip().split()
                if len(method_parts) >= 2:
                    methods.append({
                        "access_flags": " ".join(method_parts[:-1]),
                        "name": method_parts[-1],
                        "signature": match.group(1).strip(),
                    })
        return methods

    def _extract_annotations(self, content: str) -> list:
        return re.findall(r"^\.annotation\s+(.*?)$", content, re.MULTILINE)

    def _extract_source_file(self, content: str) -> str:
        match = re.search(r"^\.source\s+(.*?)$", content, re.MULTILINE)
        return match.group(1).strip() if match else ""
