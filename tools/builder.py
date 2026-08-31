import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command


class APKBuilder:
    def __init__(self):
        self.apktool_path = config.APKTOOL_PATH

    def build(
        self,
        decoded_dir: str,
        output_apk: Optional[str] = None,
        force: bool = True,
        use_aapt2: bool = False,
        net_sec_conf: bool = False,
        debuggable: bool = False,
    ) -> dict:
        if not os.path.exists(decoded_dir):
            return {"success": False, "stderr": f"Decoded directory not found: {decoded_dir}"}

        if not output_apk:
            dir_name = Path(decoded_dir).name
            output_apk = str(config.WORKSPACE_DIR / "apks" / f"{dir_name}_rebuilt.apk")

        cmd = ["java", "-jar", self.apktool_path, "b"]
        if force:
            cmd.append("-f")
        if use_aapt2:
            cmd.append("--use-aapt2")
        if net_sec_conf:
            cmd.append("--net-sec-conf")
        if debuggable:
            cmd.append("--debuggable")
        cmd.extend(["-o", output_apk, decoded_dir])

        result = run_command(cmd, timeout=600)
        if result["success"]:
            result["output_apk"] = output_apk
        return result
