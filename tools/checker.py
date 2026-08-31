import os
import sys
import platform
import shutil
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command


class SystemChecker:
    def __init__(self):
        self.results = {}
        self.warnings = []
        self.errors = []

    def _check_tool(self, name: str, cmd: list[str], hint: str = "") -> dict:
        path = shutil.which(cmd[0])
        if not path:
            result = {"status": "missing", "path": None, "version": None, "hint": hint}
            self.errors.append(f"{name}: not found in PATH")
            return result

        version_result = run_command(cmd + ["--version"], timeout=10)
        if not version_result["success"]:
            version_result = run_command(cmd, timeout=10)

        version = ""
        if version_result["success"]:
            for line in (version_result["stdout"] + version_result["stderr"]).split("\n"):
                line = line.strip()
                if line and any(c.isdigit() for c in line):
                    version = line[:80]
                    break

        result = {"status": "ok", "path": path, "version": version, "hint": hint}
        return result

    def check_python(self) -> dict:
        result = {
            "status": "ok",
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "path": sys.executable,
            "min_version": "3.10",
        }
        if sys.version_info < (3, 10):
            result["status"] = "warning"
            self.warnings.append(f"Python {result['version']} < 3.10 recommended")
        return result

    def check_adb(self) -> dict:
        return self._check_tool(
            "ADB",
            [config.ADB_PATH],
            "Install Android SDK Platform Tools: https://developer.android.com/tools/releases/platform-tools"
        )

    def check_frida(self) -> dict:
        result = self._check_tool(
            "Frida",
            ["frida"],
            "pip install frida-tools frida"
        )
        if result["status"] == "ok":
            pip_result = run_command([sys.executable, "-m", "pip", "show", "frida-tools"], timeout=10)
            if pip_result["success"]:
                for line in pip_result["stdout"].split("\n"):
                    if line.startswith("Version:"):
                        result["version"] = line.split(":", 1)[1].strip()
                        break
        return result

    def check_frida_gadget(self) -> dict:
        result = self._check_tool(
            "Frida Gadget",
            [config.FRIDA_GADGET_PATH],
            "pip install frida-gadget"
        )
        if result["status"] == "missing":
            pip_result = run_command([sys.executable, "-m", "pip", "show", "frida-gadget"], timeout=10)
            if pip_result["success"]:
                result["status"] = "ok"
                result["path"] = "pip package installed"
        return result

    def check_jadx(self) -> dict:
        return self._check_tool(
            "JADX",
            [config.JADX_PATH],
            "brew install jadx / scoop install jadx / https://github.com/skylot/jadx/releases"
        )

    def check_apktool(self) -> dict:
        return self._check_tool(
            "Apktool",
            [config.APKTOOL_PATH],
            "brew install apktool / scoop install apktool / https://apktool.org/docs/install"
        )

    def check_dex2jar(self) -> dict:
        return self._check_tool(
            "dex2jar",
            [config.DEX2JAR_PATH],
            "brew install dex2jar / https://github.com/pxb1988/dex2jar/releases"
        )

    def check_apksigner(self) -> dict:
        return self._check_tool(
            "apksigner",
            [config.APKSIGNER_PATH],
            "Install Android SDK Build Tools: https://developer.android.com/studio/releases/build-tools"
        )

    def check_keytool(self) -> dict:
        return self._check_tool(
            "keytool",
            [config.KEYTOOL_PATH],
            "Install JDK: https://adoptium.net/"
        )

    def check_zipalign(self) -> dict:
        return self._check_tool(
            "zipalign",
            [config.ZIPALIGN_PATH],
            "Install Android SDK Build Tools"
        )

    def check_aapt(self) -> dict:
        return self._check_tool(
            "aapt",
            [config.AAPT_PATH],
            "Install Android SDK Build Tools"
        )

    def check_java(self) -> dict:
        result = self._check_tool(
            "Java",
            ["java"],
            "Install JDK 11+: https://adoptium.net/"
        )
        if result["status"] == "ok" and config.JAVA_HOME:
            result["java_home"] = config.JAVA_HOME
        return result

    def check_nox(self) -> dict:
        nox_cfg = config.EMULATOR_CONFIGS.get("nox", {})
        for path in nox_cfg.get("adb_paths", []):
            if os.path.exists(path):
                return {"status": "ok", "path": path, "name": "Nox Player"}

        nox_adb = shutil.which("nox_adb")
        if nox_adb:
            return {"status": "ok", "path": nox_adb, "name": "Nox Player"}

        return {"status": "not_installed", "path": None, "name": "Nox Player", "hint": "https://www.bignox.com/"}

    def check_bluestacks(self) -> dict:
        bs_cfg = config.EMULATOR_CONFIGS.get("bluestacks", {})
        for path in bs_cfg.get("adb_paths", []):
            if os.path.exists(path):
                return {"status": "ok", "path": path, "name": "BlueStacks"}

        return {"status": "not_installed", "path": None, "name": "BlueStacks", "hint": "https://www.bluestacks.com/"}

    def check_memu(self) -> dict:
        memu_cfg = config.EMULATOR_CONFIGS.get("memu", {})
        for path in memu_cfg.get("adb_paths", []):
            if os.path.exists(path):
                return {"status": "ok", "path": path, "name": "MEmu Play"}

        return {"status": "not_installed", "path": None, "name": "MEmu Play", "hint": "https://www.memuplay.com/"}

    def check_workspace(self) -> dict:
        dirs = {
            "workspace": config.WORKSPACE_DIR,
            "apks": config.APKS_DIR,
            "decoded": config.DECODED_DIR,
            "java_src": config.JAVA_SRC_DIR,
            "smali": config.SMALI_DIR,
            "jars": config.JARS_DIR,
            "frida_scripts": config.FRIDA_SCRIPTS_DIR,
        }
        status = "ok"
        details = {}
        for name, path in dirs.items():
            exists = path.exists()
            details[name] = {"path": str(path), "exists": exists}
            if not exists:
                status = "warning"

        return {"status": status, "directories": details}

    def check_frida_scripts(self) -> dict:
        scripts = [
            "ssl_pinning_bypass.js",
            "root_detection_bypass.js",
            "emulator_detection_bypass.js",
            "anti_debug_bypass.js",
            "common_bypasses.js",
            "method_tracer.js",
        ]
        found = []
        missing = []
        for script in scripts:
            path = config.FRIDA_SCRIPTS_DIR / script
            if path.exists():
                found.append(script)
            else:
                missing.append(script)

        return {
            "status": "ok" if not missing else "warning",
            "found": found,
            "missing": missing,
        }

    def run_full_check(self) -> dict:
        checks = {
            "system": {
                "platform": platform.system(),
                "release": platform.release(),
                "architecture": platform.machine(),
                "python": self.check_python(),
            },
            "core_tools": {
                "adb": self.check_adb(),
                "frida": self.check_frida(),
                "frida_gadget": self.check_frida_gadget(),
                "java": self.check_java(),
            },
            "decompilation": {
                "jadx": self.check_jadx(),
                "apktool": self.check_apktool(),
                "dex2jar": self.check_dex2jar(),
            },
            "signing": {
                "apksigner": self.check_apksigner(),
                "keytool": self.check_keytool(),
                "zipalign": self.check_zipalign(),
                "aapt": self.check_aapt(),
            },
            "emulators": {
                "nox": self.check_nox(),
                "bluestacks": self.check_bluestacks(),
                "memu": self.check_memu(),
            },
            "workspace": self.check_workspace(),
            "frida_scripts": self.check_frida_scripts(),
        }

        total = 0
        ok = 0
        warnings = 0
        errors = 0

        def count_status(obj):
            nonlocal total, ok, warnings, errors
            if isinstance(obj, dict):
                if "status" in obj:
                    total += 1
                    if obj["status"] == "ok":
                        ok += 1
                    elif obj["status"] == "warning":
                        warnings += 1
                        self.warnings.append(str(obj))
                    elif obj["status"] in ("missing", "error"):
                        errors += 1
                        self.errors.append(str(obj))
                for v in obj.values():
                    count_status(v)
            elif isinstance(obj, list):
                for item in obj:
                    count_status(item)

        count_status(checks)

        return {
            "success": True,
            "checks": checks,
            "summary": {
                "total": total,
                "ok": ok,
                "warnings": warnings,
                "errors": errors,
                "health": f"{ok}/{total} checks passed",
            },
            "warnings": self.warnings,
            "errors": self.errors,
        }
