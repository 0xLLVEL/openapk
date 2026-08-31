import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command


class Decompiler:
    def __init__(self):
        self.jadx_path = config.JADX_PATH
        self.apktool_path = config.APKTOOL_PATH
        self.dex2jar_path = config.DEX2JAR_PATH

    def decompile_jadx(
        self,
        apk_path: str,
        output_dir: Optional[str] = None,
        no_res: bool = False,
        threads: int = 4,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        if not output_dir:
            apk_name = Path(apk_path).stem
            output_dir = str(config.JAVA_SRC_DIR / apk_name)

        cmd = [self.jadx_path, "-d", output_dir, "--threads-count", str(threads)]
        if no_res:
            cmd.append("--no-res")
        cmd.append(apk_path)

        result = run_command(cmd, timeout=600)
        if result["success"]:
            result["output_dir"] = output_dir
        return result

    def decompile_apktool(
        self,
        apk_path: str,
        output_dir: Optional[str] = None,
        force: bool = True,
        no_src: bool = False,
        no_res: bool = False,
        keep_broken_res: bool = False,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        if not output_dir:
            apk_name = Path(apk_path).stem
            output_dir = str(config.DECODED_DIR / apk_name)

        cmd = ["java", "-jar", self.apktool_path, "d"]
        if force:
            cmd.append("-f")
        if no_src:
            cmd.append("-s")
        if no_res:
            cmd.append("-r")
        if keep_broken_res:
            cmd.append("--keep-broken-res")
        cmd.extend(["-o", output_dir, apk_path])

        result = run_command(cmd, timeout=600)
        if result["success"]:
            result["output_dir"] = output_dir
        return result

    def decompile_dex2jar(
        self,
        apk_path: str,
        output_jar: Optional[str] = None,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        if not output_jar:
            apk_name = Path(apk_path).stem
            output_jar = str(config.JARS_DIR / f"{apk_name}.jar")

        cmd = [self.dex2jar_path, apk_path, "-o", output_jar, "-f"]
        result = run_command(cmd, timeout=300)

        if result["success"]:
            result["output_jar"] = output_jar
        return result

    def disassemble_smali(
        self,
        dex_path: str,
        output_dir: Optional[str] = None,
    ) -> dict:
        if not os.path.exists(dex_path):
            return {"success": False, "stderr": f"DEX not found: {dex_path}"}

        if not output_dir:
            dex_name = Path(dex_path).stem
            output_dir = str(config.SMALI_DIR / dex_name)

        cmd = ["java", "-jar", self.apktool_path, "d", dex_path, "-o", output_dir, "-s"]
        result = run_command(cmd, timeout=300)

        if result["success"]:
            result["output_dir"] = output_dir
        return result

    def assemble_smali(
        self,
        smali_dir: str,
        output_dex: Optional[str] = None,
    ) -> dict:
        if not os.path.exists(smali_dir):
            return {"success": False, "stderr": f"Smali dir not found: {smali_dir}"}

        if not output_dex:
            dir_name = Path(smali_dir).name
            output_dex = str(config.WORKSPACE_DIR / f"{dir_name}.dex")

        cmd = ["java", "-jar", self.apktool_path, "b", smali_dir, "-o", output_dex]
        result = run_command(cmd, timeout=300)

        if result["success"]:
            result["output_dex"] = output_dex
        return result

    def extract_dex(self, apk_path: str, output_dir: Optional[str] = None) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        if not output_dir:
            apk_name = Path(apk_path).stem
            output_dir = str(config.WORKSPACE_DIR / f"{apk_name}_dex")

        os.makedirs(output_dir, exist_ok=True)

        result = run_command(["unzip", "-o", apk_path, "*.dex", "-d", output_dir])
        if result["success"]:
            dex_files = [f for f in os.listdir(output_dir) if f.endswith(".dex")]
            result["dex_files"] = [os.path.join(output_dir, f) for f in dex_files]
            result["output_dir"] = output_dir
        return result
