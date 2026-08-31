import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command, get_arch_from_device


class ADBManager:
    def __init__(self, adb_path: Optional[str] = None):
        self.adb_path = adb_path or config.ADB_PATH
        self._nox_adb_path = self._find_nox_adb()

    def _cmd(self, device_id: Optional[str] = None) -> list[str]:
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        return cmd

    def _find_nox_adb(self) -> Optional[str]:
        for path in config.EMULATOR_CONFIGS["nox"]["adb_paths"]:
            if os.path.exists(path):
                return path
        nox_adb = shutil.which("nox_adb")
        if nox_adb:
            return nox_adb
        return None

    def _find_emulator_adb(self, emulator: str) -> Optional[str]:
        if emulator not in config.EMULATOR_CONFIGS:
            return None
        for path in config.EMULATOR_CONFIGS[emulator]["adb_paths"]:
            if os.path.exists(path):
                return path
        return None

    def detect_emulators(self) -> dict:
        detected = {}
        for name, cfg in config.EMULATOR_CONFIGS.items():
            adb_path = self._find_emulator_adb(name)
            if adb_path:
                detected[name] = {
                    "name": cfg["name"],
                    "adb_path": adb_path,
                    "default_host": cfg["default_host"],
                    "default_port": cfg["default_port"],
                    "common_ports": cfg["common_ports"],
                }
        return {"success": True, "emulators": detected}

    def connect_nox(self, port: Optional[int] = None, host: str = "") -> dict:
        nox_cfg = config.EMULATOR_CONFIGS["nox"]
        target_host = host or nox_cfg["default_host"]
        target_port = port or nox_cfg["default_port"]
        address = f"{target_host}:{target_port}"

        if self._nox_adb_path:
            result = run_command([self._nox_adb_path, "connect", address])
        else:
            result = run_command([self.adb_path, "connect", address])

        if not result["success"]:
            for p in nox_cfg["common_ports"]:
                addr = f"{target_host}:{p}"
                result = run_command([self.adb_path, "connect", addr])
                if result["success"] and "connected" in result["stdout"].lower():
                    result["connected_address"] = addr
                    return result

        return result

    def connect_emulator(self, emulator: str, port: Optional[int] = None, host: str = "") -> dict:
        if emulator not in config.EMULATOR_CONFIGS:
            return {"success": False, "stderr": f"Unknown emulator: {emulator}. Supported: {list(config.EMULATOR_CONFIGS.keys())}"}

        cfg = config.EMULATOR_CONFIGS[emulator]
        target_host = host or cfg["default_host"]
        target_port = port or cfg["default_port"]
        address = f"{target_host}:{target_port}"

        adb_path = self._find_emulator_adb(emulator) or self.adb_path
        result = run_command([adb_path, "connect", address])

        if not result["success"]:
            for p in cfg["common_ports"]:
                addr = f"{target_host}:{p}"
                result = run_command([adb_path, "connect", addr])
                if result["success"] and "connected" in result["stdout"].lower():
                    result["connected_address"] = addr
                    return result

        return result

    def start_nox(self) -> dict:
        nox_cfg = config.EMULATOR_CONFIGS["nox"]
        nox_paths = [
            r"C:\Program Files (x86)\nox\bin\Nox.exe",
            r"C:\Program Files\nox\bin\Nox.exe",
            os.path.expanduser(r"~\AppData\Local\Nox\bin\Nox.exe"),
        ]

        for path in nox_paths:
            if os.path.exists(path):
                result = run_command([path], timeout=10)
                return {"success": True, "message": "Nox Player starting...", "path": path}

        nox_console = shutil.which("nox")
        if nox_console:
            return run_command([nox_console], timeout=10)

        return {"success": False, "stderr": "Nox Player not found. Please install Nox Player or set NOX_ADB_PATH."}

    def start_emulator(self, emulator: str) -> dict:
        if emulator not in config.EMULATOR_CONFIGS:
            return {"success": False, "stderr": f"Unknown emulator: {emulator}"}

        if emulator == "nox":
            return self.start_nox()

        cfg = config.EMULATOR_CONFIGS[emulator]
        adb_path = self._find_emulator_adb(emulator)
        if adb_path:
            emulator_dir = Path(adb_path).parent
            emulator_exe = emulator_dir / f"{emulator}.exe"
            if emulator_exe.exists():
                return run_command([str(emulator_exe)], timeout=10)

        return {"success": False, "stderr": f"{cfg['name']} executable not found"}

    def list_devices(self) -> dict:
        result = run_command([self.adb_path, "devices", "-l"])
        if not result["success"]:
            return result

        devices = []
        for line in result["stdout"].strip().split("\n")[1:]:
            line = line.strip()
            if not line or "offline" in line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                device_id = parts[0]
                device_type = "unknown"
                if "nox" in line.lower():
                    device_type = "nox"
                elif "bluestacks" in line.lower():
                    device_type = "bluestacks"
                elif "memu" in line.lower():
                    device_type = "memu"
                elif ":" in device_id:
                    device_type = "network"
                else:
                    device_type = "usb"

                devices.append({
                    "id": device_id,
                    "state": parts[1],
                    "type": device_type,
                    "info": " ".join(parts[2:]) if len(parts) > 2 else "",
                })
        return {"success": True, "devices": devices}

    def connect(self, address: str) -> dict:
        return run_command([self.adb_path, "connect", address])

    def disconnect(self, address: Optional[str] = None) -> dict:
        cmd = [self.adb_path, "disconnect"]
        if address:
            cmd.append(address)
        return run_command(cmd)

    def install_apk(self, apk_path: str, device_id: Optional[str] = None) -> dict:
        cmd = self._cmd(device_id)
        cmd.extend(["install", "-r", apk_path])
        return run_command(cmd, timeout=300)

    def uninstall_app(self, package_name: str, device_id: Optional[str] = None) -> dict:
        cmd = self._cmd(device_id)
        cmd.extend(["uninstall", package_name])
        return run_command(cmd)

    def shell(self, command: str, device_id: Optional[str] = None) -> dict:
        cmd = self._cmd(device_id)
        cmd.extend(["shell", command])
        return run_command(cmd)

    def pull(self, remote_path: str, local_path: str, device_id: Optional[str] = None) -> dict:
        cmd = self._cmd(device_id)
        cmd.extend(["pull", remote_path, local_path])
        return run_command(cmd, timeout=300)

    def push(self, local_path: str, remote_path: str, device_id: Optional[str] = None) -> dict:
        cmd = self._cmd(device_id)
        cmd.extend(["push", local_path, remote_path])
        return run_command(cmd, timeout=300)

    def screenshot(self, device_id: Optional[str] = None) -> dict:
        remote_path = "/sdcard/screenshot.png"
        local_path = str(config.WORKSPACE_DIR / "screenshot.png")

        result = self.shell(f"screencap -p {remote_path}", device_id)
        if not result["success"]:
            return result

        result = self.pull(remote_path, local_path, device_id)
        if result["success"]:
            result["local_path"] = local_path
        self.shell(f"rm {remote_path}", device_id)
        return result

    def logcat(
        self,
        device_id: Optional[str] = None,
        filter_expr: Optional[str] = None,
        lines: int = 100,
    ) -> dict:
        cmd = self._cmd(device_id)
        cmd.extend(["logcat", "-d", "-t", str(lines)])
        if filter_expr:
            cmd.extend(["-s", filter_expr])
        return run_command(cmd, timeout=30)

    def start_app(self, package_name: str, activity: Optional[str] = None, device_id: Optional[str] = None) -> dict:
        if activity:
            component = f"{package_name}/{activity}"
        else:
            component = package_name
        return self.shell(f"am start -n {component}", device_id)

    def stop_app(self, package_name: str, device_id: Optional[str] = None) -> dict:
        return self.shell(f"am force-stop {package_name}", device_id)

    def get_props(self, device_id: Optional[str] = None) -> dict:
        props = {}
        prop_keys = [
            "ro.product.model",
            "ro.product.brand",
            "ro.product.device",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.product.cpu.abi",
            "ro.build.display.id",
            "ro.product.manufacturer",
        ]
        for key in prop_keys:
            result = self.shell(f"getprop {key}", device_id)
            if result["success"]:
                props[key] = result["stdout"].strip()
        return {"success": True, "properties": props}

    def get_device_arch(self, device_id: Optional[str] = None) -> Optional[str]:
        return get_arch_from_device(self.adb_path, device_id)
