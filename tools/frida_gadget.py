import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command, check_tool_exists


class FridaGadgetInjector:
    def __init__(self):
        self.gadget_cmd = config.FRIDA_GADGET_PATH

    def inject(
        self,
        apk_path: str,
        arch: Optional[str] = None,
        sign: bool = True,
        js_script: Optional[str] = None,
        js_delay: Optional[int] = None,
        no_res: bool = True,
        main_activity: Optional[str] = None,
        frida_version: Optional[str] = None,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        cmd = [self.gadget_cmd, apk_path]

        if arch:
            cmd.extend(["--arch", arch])
        if sign:
            cmd.append("--sign")
        if js_script:
            script_path = self._resolve_script(js_script)
            if not script_path:
                return {"success": False, "stderr": f"Script not found: {js_script}"}
            cmd.extend(["--js", script_path])
        if js_delay is not None:
            cmd.extend(["--js-delay", str(js_delay)])
        if no_res:
            cmd.append("--no-res")
        if main_activity:
            cmd.extend(["--main-activity", main_activity])
        if frida_version:
            cmd.extend(["--frida-version", frida_version])

        result = run_command(cmd, timeout=600)

        if result["success"]:
            apk_dir = Path(apk_path).parent
            dist_dir = apk_dir / "dist"
            patched_apks = list(dist_dir.glob("*.apk")) if dist_dir.exists() else []
            if patched_apks:
                result["patched_apk"] = str(patched_apks[0])
                result["message"] = f"Successfully patched APK with Frida Gadget"

        return result

    def inject_custom_gadget(
        self,
        apk_path: str,
        gadget_so_path: str,
        sign: bool = True,
        no_res: bool = True,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}
        if not os.path.exists(gadget_so_path):
            return {"success": False, "stderr": f"Gadget .so not found: {gadget_so_path}"}

        cmd = [self.gadget_cmd, apk_path]
        cmd.extend(["--custom-gadget-path", gadget_so_path])
        if sign:
            cmd.append("--sign")
        if no_res:
            cmd.append("--no-res")

        result = run_command(cmd, timeout=600)

        if result["success"]:
            apk_dir = Path(apk_path).parent
            dist_dir = apk_dir / "dist"
            patched_apks = list(dist_dir.glob("*.apk")) if dist_dir.exists() else []
            if patched_apks:
                result["patched_apk"] = str(patched_apks[0])

        return result

    def inject_with_script(
        self,
        apk_path: str,
        js_script_path: str,
        arch: Optional[str] = None,
        sign: bool = True,
        js_delay: int = 2,
        frida_version: Optional[str] = None,
    ) -> dict:
        return self.inject(
            apk_path,
            arch=arch,
            sign=sign,
            js_script=js_script_path,
            js_delay=js_delay,
            frida_version=frida_version,
        )

    def verify_injection(self, apk_path: str) -> dict:
        result = run_command(["unzip", "-l", apk_path])
        if not result["success"]:
            return result

        has_gadget = "libfrida-gadget" in result["stdout"]
        gadget_libs = [
            line.strip().split()[-1]
            for line in result["stdout"].split("\n")
            if "libfrida-gadget" in line
        ]

        return {
            "success": True,
            "has_gadget": has_gadget,
            "gadget_libraries": gadget_libs,
            "message": "Frida Gadget found in APK" if has_gadget else "No Frida Gadget found",
        }

    def _resolve_script(self, script: str) -> Optional[str]:
        path = Path(script)
        if path.exists():
            return str(path)

        path = config.FRIDA_SCRIPTS_DIR / script
        if path.exists():
            return str(path)

        return None
