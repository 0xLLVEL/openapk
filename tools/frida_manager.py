import os
import sys
import platform
import urllib.request
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command, check_tool_exists


class FridaServerManager:
    def __init__(self, adb_path: Optional[str] = None):
        self.adb_path = adb_path or config.ADB_PATH
        self.server_dir = config.FRIDA_SERVER_DIR

    def _adb_cmd(self, device_id: Optional[str] = None) -> list[str]:
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        return cmd

    def _shell(self, command: str, device_id: Optional[str] = None) -> dict:
        cmd = self._adb_cmd(device_id)
        cmd.extend(["shell", command])
        return run_command(cmd)

    def _get_frida_version(self) -> str:
        result = run_command(["frida", "--version"])
        if result["success"]:
            return result["stdout"].strip()
        return ""

    def _get_device_arch(self, device_id: Optional[str] = None) -> Optional[str]:
        result = self._shell("getprop ro.product.cpu.abi", device_id)
        if result["success"]:
            return result["stdout"].strip()
        return None

    def _download_server(self, version: str, arch: str) -> Optional[Path]:
        arch_map = {
            "arm64-v8a": "arm64",
            "armeabi-v7a": "arm",
            "x86_64": "x86_64",
            "x86": "x86",
        }
        frida_arch = arch_map.get(arch, arch)
        filename = f"frida-server-{version}-android-{frida_arch}.xz"
        url = f"https://github.com/frida/frida/releases/download/{version}/{filename}"
        dest = self.server_dir / filename

        if dest.exists():
            return dest

        try:
            urllib.request.urlretrieve(url, dest)
            return dest
        except Exception:
            return None

    def _extract_server(self, xz_path: Path) -> Optional[Path]:
        result = run_command(["unxz", "-f", str(xz_path)])
        if result["success"]:
            extracted = xz_path.with_suffix("")
            if extracted.exists():
                return extracted
        return None

    def check_server(self, device_id: Optional[str] = None) -> dict:
        result = self._shell("ps | grep frida-server", device_id)
        running = "frida-server" in result.get("stdout", "")

        version = self._get_frida_version()
        device_version = ""
        if running:
            vresult = self._shell("/data/local/tmp/frida-server --version", device_id)
            if vresult["success"]:
                device_version = vresult["stdout"].strip()

        return {
            "success": True,
            "running": running,
            "host_version": version,
            "device_version": device_version,
            "version_match": version == device_version if device_version else False,
        }

    def start_server(self, device_id: Optional[str] = None, version: Optional[str] = None) -> dict:
        check = self.check_server(device_id)
        if check.get("running") and check.get("version_match"):
            return {"success": True, "message": "frida-server already running"}

        self.stop_server(device_id)

        frida_version = version or self._get_frida_version()
        if not frida_version:
            return {"success": False, "stderr": "Could not determine Frida version. Is Frida installed?"}

        arch = self._get_device_arch(device_id)
        if not arch:
            return {"success": False, "stderr": "Could not detect device architecture"}

        xz_path = self._download_server(frida_version, arch)
        if not xz_path:
            return {"success": False, "stderr": f"Failed to download frida-server {frida_version} for {arch}"}

        server_binary = self._extract_server(xz_path)
        if not server_binary:
            return {"success": False, "stderr": "Failed to extract frida-server"}

        remote_path = "/data/local/tmp/frida-server"
        cmd = self._adb_cmd(device_id)
        cmd.extend(["push", str(server_binary), remote_path])
        push_result = run_command(cmd, timeout=120)
        if not push_result["success"]:
            return push_result

        self._shell(f"chmod 755 {remote_path}", device_id)
        start_result = self._shell(f"nohup {remote_path} -l 0.0.0.0 > /dev/null 2>&1 &", device_id)

        import time
        time.sleep(2)

        check = self.check_server(device_id)
        if check.get("running"):
            return {
                "success": True,
                "message": f"frida-server {frida_version} started on {arch}",
                "version": frida_version,
                "arch": arch,
            }
        return {"success": False, "stderr": "Failed to start frida-server"}

    def stop_server(self, device_id: Optional[str] = None) -> dict:
        self._shell("pkill frida-server", device_id)
        self._shell("killall frida-server", device_id)
        self._shell("rm -f /data/local/tmp/frida-server", device_id)
        return {"success": True, "message": "frida-server stopped"}

    def restart_server(self, device_id: Optional[str] = None, version: Optional[str] = None) -> dict:
        self.stop_server(device_id)
        import time
        time.sleep(1)
        return self.start_server(device_id, version)

    def get_version(self, device_id: Optional[str] = None) -> dict:
        result = self._shell("/data/local/tmp/frida-server --version 2>/dev/null", device_id)
        if result["success"] and result["stdout"].strip():
            return {"success": True, "version": result["stdout"].strip()}
        return {"success": False, "stderr": "frida-server not found or not running on device"}

    def list_processes(self, device_id: Optional[str] = None) -> dict:
        cmd = ["frida-ps"]
        if device_id:
            cmd.extend(["-U", "-s", device_id])
        else:
            cmd.append("-U")
        result = run_command(cmd)
        if not result["success"]:
            return result

        processes = []
        for line in result["stdout"].strip().split("\n")[1:]:
            line = line.strip()
            if not line:
                continue
            pid_str = line[:7].strip()
            name = line[7:].strip()
            try:
                processes.append({"pid": int(pid_str), "name": name})
            except ValueError:
                continue
        return {"success": True, "processes": processes}

    def list_apps(self, device_id: Optional[str] = None) -> dict:
        result = self._shell("pm list packages -3", device_id)
        if not result["success"]:
            return result

        apps = []
        for line in result["stdout"].strip().split("\n"):
            line = line.strip()
            if line.startswith("package:"):
                apps.append(line[8:])
        return {"success": True, "apps": apps}
