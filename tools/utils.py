import subprocess
import shutil
from pathlib import Path
from typing import Optional


def run_command(
    cmd: list[str],
    timeout: int = 120,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
) -> dict:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command not found: {cmd[0]}",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def check_tool_exists(tool_path: str) -> bool:
    return shutil.which(tool_path) is not None


def get_file_extension(filepath: str) -> str:
    return Path(filepath).suffix.lower()


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in name)


def get_arch_from_device(adb_path: str, device_id: Optional[str] = None) -> Optional[str]:
    cmd = [adb_path]
    if device_id:
        cmd.extend(["-s", device_id])
    cmd.extend(["shell", "getprop", "ro.product.cpu.abi"])

    result = run_command(cmd)
    if result["success"]:
        return result["stdout"].strip()
    return None
