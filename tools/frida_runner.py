import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command


class FridaScriptRunner:
    def __init__(self):
        self.active_sessions = {}

    def _load_script(self, script_path: str) -> str:
        path = Path(script_path)
        if not path.exists():
            path = config.FRIDA_SCRIPTS_DIR / script_path
        if not path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        return path.read_text(encoding="utf-8")

    def run_script(
        self,
        package_name: str,
        script_source: str,
        device_id: Optional[str] = None,
        spawn: bool = True,
        runtime: str = "v8",
        timeout: int = 30,
    ) -> dict:
        temp_script = None
        try:
            temp_script = tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False, encoding="utf-8"
            )
            temp_script.write(script_source)
            temp_script.close()

            cmd = ["frida"]
            if device_id:
                cmd.extend(["-U", "-s", device_id])
            else:
                cmd.append("-U")

            if spawn:
                cmd.extend(["-f", package_name])
            else:
                cmd.append(package_name)

            cmd.extend(["-l", temp_script.name, "--runtime", runtime, "--no-pause"])

            result = run_command(cmd, timeout=timeout)
            return {
                "success": result["success"],
                "output": result["stdout"],
                "errors": result["stderr"] if not result["success"] else "",
            }
        except Exception as e:
            return {"success": False, "output": "", "errors": str(e)}
        finally:
            if temp_script and os.path.exists(temp_script.name):
                os.unlink(temp_script.name)

    def run_script_file(
        self,
        package_name: str,
        script_path: str,
        device_id: Optional[str] = None,
        spawn: bool = True,
        runtime: str = "v8",
        timeout: int = 30,
    ) -> dict:
        try:
            script_source = self._load_script(script_path)
        except FileNotFoundError as e:
            return {"success": False, "output": "", "errors": str(e)}

        return self.run_script(
            package_name, script_source, device_id, spawn, runtime, timeout
        )

    def run_script_inline(
        self,
        package_name: str,
        script: str,
        device_id: Optional[str] = None,
        spawn: bool = True,
        timeout: int = 30,
    ) -> dict:
        return self.run_script(package_name, script, device_id, spawn, timeout=timeout)

    def run_ssl_bypass(self, package_name: str, device_id: Optional[str] = None, spawn: bool = True) -> dict:
        return self.run_script_file(package_name, "ssl_pinning_bypass.js", device_id, spawn)

    def run_root_bypass(self, package_name: str, device_id: Optional[str] = None, spawn: bool = True) -> dict:
        return self.run_script_file(package_name, "root_detection_bypass.js", device_id, spawn)

    def run_emulator_bypass(self, package_name: str, device_id: Optional[str] = None, spawn: bool = True) -> dict:
        return self.run_script_file(package_name, "emulator_detection_bypass.js", device_id, spawn)

    def run_anti_debug_bypass(self, package_name: str, device_id: Optional[str] = None, spawn: bool = True) -> dict:
        return self.run_script_file(package_name, "anti_debug_bypass.js", device_id, spawn)

    def trace_function(
        self,
        package_name: str,
        class_method: str,
        device_id: Optional[str] = None,
        spawn: bool = True,
    ) -> dict:
        parts = class_method.rsplit(".", 1)
        if len(parts) != 2:
            return {"success": False, "output": "", "errors": "Format must be ClassName.methodName"}

        class_name, method_name = parts
        script = f"""
Java.perform(function() {{
    var className = Java.use("{class_name}");
    className.{method_name}.implementation = function() {{
        console.log("[TRACE] {class_method} called");
        console.log("  Arguments: " + JSON.stringify(arguments));
        var result = this.{method_name}.apply(this, arguments);
        console.log("  Return: " + JSON.stringify(result));
        return result;
    }};
}});
"""
        return self.run_script(package_name, script, device_id, spawn)

    def list_modules(self, package_name: str, device_id: Optional[str] = None) -> dict:
        script = """
rpc.exports = {
    listModules: function() {
        return Process.enumerateModules().map(function(m) {
            return { name: m.name, base: m.base.toString(), size: m.size, path: m.path };
        });
    }
};
"""
        try:
            result = self.run_script(package_name, script, device_id, False, timeout=10)
            return {"success": result["success"], "output": result["output"], "errors": result.get("errors", "")}
        except Exception as e:
            return {"success": False, "output": "", "errors": str(e)}

    def find_classes(self, package_name: str, pattern: str, device_id: Optional[str] = None) -> dict:
        script = f"""
Java.perform(function() {{
    Java.enumerateLoadedClasses({{
        onMatch: function(className) {{
            if (className.includes("{pattern}")) {{
                console.log("[CLASS] " + className);
            }}
        }},
        onComplete: function() {{
            console.log("[DONE] Enumeration complete");
        }}
    }});
}});
"""
        return self.run_script(package_name, script, device_id, False, timeout=15)

    def find_methods(self, package_name: str, class_name: str, device_id: Optional[str] = None) -> dict:
        script = f"""
Java.perform(function() {{
    var className = Java.use("{class_name}");
    var methods = className.class.getDeclaredMethods();
    console.log("[METHODS] Methods of {class_name}:");
    for (var i = 0; i < methods.length; i++) {{
        console.log("  " + methods[i].toString());
    }}
}});
"""
        return self.run_script(package_name, script, device_id, False, timeout=10)

    def memory_dump(self, package_name: str, address: str, size: int, device_id: Optional[str] = None) -> dict:
        script = f"""
var addr = ptr("{address}");
var buf = Memory.readByteArray(addr, {size});
console.log("[DUMP] " + hexdump(buf, {{ offset: 0, length: {size} }}));
"""
        return self.run_script(package_name, script, device_id, False, timeout=10)

    def memory_scan(self, package_name: str, pattern: str, device_id: Optional[str] = None) -> dict:
        script = f"""
var matches = Memory.scanSync(ptr("0"), Process.pointerSize * 1000000, "{pattern}");
matches.forEach(function(match) {{
    console.log("[SCAN] Found at: " + match.address);
}});
"""
        return self.run_script(package_name, script, device_id, False, timeout=15)
