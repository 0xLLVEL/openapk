import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command


class APKAnalyzer:
    def __init__(self, aapt_path: Optional[str] = None):
        self.aapt_path = aapt_path or config.AAPT_PATH

    def analyze(self, apk_path: str) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        info = {}

        badging = self._dump_badging(apk_path)
        if badging["success"]:
            info["package"] = self._extract_value(badging["stdout"], "package: name")
            info["version_code"] = self._extract_value(badging["stdout"], "versionCode")
            info["version_name"] = self._extract_value(badging["stdout"], "versionName")
            info["sdk_version"] = self._extract_value(badging["stdout"], "sdkVersion")
            info["target_sdk"] = self._extract_value(badging["stdout"], "targetSdkVersion")
            info["application_label"] = self._extract_value(badging["stdout"], "application-label")
            info["launchable_activity"] = self._extract_value(badging["stdout"], "launchable-activity")

        permissions = self.get_permissions(apk_path)
        if permissions["success"]:
            info["permissions"] = permissions["permissions"]

        activities = self.get_activities(apk_path)
        if activities["success"]:
            info["activities"] = activities["activities"]

        services = self.get_services(apk_path)
        if services["success"]:
            info["services"] = services["services"]

        receivers = self.get_receivers(apk_path)
        if receivers["success"]:
            info["receivers"] = receivers["receivers"]

        providers = self.get_providers(apk_path)
        if providers["success"]:
            info["providers"] = providers["providers"]

        info["size"] = os.path.getsize(apk_path)
        info["path"] = apk_path

        return {"success": True, "info": info}

    def manifest(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "xmltree", apk_path, "AndroidManifest.xml"])
        return result

    def get_permissions(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "badging", apk_path])
        if not result["success"]:
            return result

        permissions = re.findall(r"uses-permission: name='([^']+)'", result["stdout"])
        return {"success": True, "permissions": permissions}

    def get_activities(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "badging", apk_path])
        if not result["success"]:
            return result

        activities = re.findall(r"launchable-activity: name='([^']+)'", result["stdout"])
        all_activities = re.findall(r"activity: name='([^']+)'", result["stdout"])
        return {"success": True, "activities": all_activities or activities}

    def get_services(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "badging", apk_path])
        if not result["success"]:
            return result

        services = re.findall(r"service: name='([^']+)'", result["stdout"])
        return {"success": True, "services": services}

    def get_receivers(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "badging", apk_path])
        if not result["success"]:
            return result

        receivers = re.findall(r"receiver: name='([^']+)'", result["stdout"])
        return {"success": True, "receivers": receivers}

    def get_providers(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "badging", apk_path])
        if not result["success"]:
            return result

        providers = re.findall(r"provider: name='([^']+)'", result["stdout"])
        return {"success": True, "providers": providers}

    def get_deep_links(self, apk_path: str) -> dict:
        result = run_command([self.aapt_path, "dump", "badging", apk_path])
        if not result["success"]:
            return result

        deep_links = re.findall(r"intent-filter:.*?scheme=(\w+)", result["stdout"], re.DOTALL)
        return {"success": True, "deep_links": deep_links}

    def get_certificates(self, apk_path: str) -> dict:
        result = run_command(["keytool", "-printcert", "-jarfile", apk_path])
        return result

    def get_native_libs(self, apk_path: str) -> dict:
        result = run_command(["unzip", "-l", apk_path])
        if not result["success"]:
            return result

        libs = [
            line.strip().split()[-1]
            for line in result["stdout"].split("\n")
            if "lib/" in line and line.strip().endswith(".so")
        ]
        return {"success": True, "native_libs": libs}

    def scan_secrets(self, apk_path: str) -> dict:
        patterns = [
            (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([^'\"]+)['\"]", "API Key"),
            (r"(?i)(secret|password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Secret/Password"),
            (r"(?i)(token|auth[_-]?token|access[_-]?token)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Token"),
            (r"(?i)(client[_-]?secret|client[_-]?id)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Client Credentials"),
            (r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "Private Key"),
            (r"(?i)(aws[_-]?(?:access|secret)[-_]?(?:key|id))\s*[:=]\s*['\"]([^'\"]+)['\"]", "AWS Key"),
            (r"(?i)(firebase|google)[-_]?(?:api|app)[-_]?key\s*[:=]\s*['\"]([^'\"]+)['\"]", "Firebase/Google Key"),
        ]

        secrets = []
        temp_dir = config.WORKSPACE_DIR / "apk_extract"

        import zipfile
        try:
            with zipfile.ZipFile(apk_path, "r") as z:
                z.extractall(temp_dir)

            for root, dirs, files in os.walk(temp_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", errors="ignore") as f:
                            content = f.read()
                        for pattern, label in patterns:
                            for match in re.finditer(pattern, content):
                                secrets.append({
                                    "type": label,
                                    "match": match.group(0)[:100],
                                    "file": os.path.relpath(fpath, temp_dir),
                                })
                    except Exception:
                        continue
        except Exception as e:
            return {"success": False, "stderr": str(e)}
        finally:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        return {"success": True, "secrets": secrets}

    def _dump_badging(self, apk_path: str) -> dict:
        return run_command([self.aapt_path, "dump", "badging", apk_path])

    def _extract_value(self, output: str, key: str) -> str:
        match = re.search(rf"{key}='([^']*)'", output)
        if match:
            return match.group(1)
        match = re.search(rf"{key}:\s*(\S+)", output)
        if match:
            return match.group(1)
        return ""
