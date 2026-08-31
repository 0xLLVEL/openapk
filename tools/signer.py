import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from tools.utils import run_command


class APKSigner:
    def __init__(self):
        self.apksigner_path = config.APKSIGNER_PATH
        self.keytool_path = config.KEYTOOL_PATH
        self.zipalign_path = config.ZIPALIGN_PATH

    def sign(
        self,
        apk_path: str,
        keystore_path: Optional[str] = None,
        keystore_pass: Optional[str] = None,
        key_alias: Optional[str] = None,
        key_pass: Optional[str] = None,
        output_apk: Optional[str] = None,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        cmd = [self.apksigner_path, "sign"]

        if keystore_path:
            cmd.extend(["--ks", keystore_path])
        else:
            debug_keystore = self._find_debug_keystore()
            if debug_keystore:
                cmd.extend(["--ks", debug_keystore])
                keystore_pass = keystore_pass or "android"
                key_alias = key_alias or "androiddebugkey"
            else:
                return {"success": False, "stderr": "No keystore provided and debug keystore not found"}

        if keystore_pass:
            cmd.extend(["--ks-pass", f"pass:{keystore_pass}"])
        if key_alias:
            cmd.extend(["--ks-key-alias", key_alias])
        if key_pass:
            cmd.extend(["--key-pass", f"pass:{key_pass}"])
        if output_apk:
            cmd.extend(["--out", output_apk])

        cmd.append(apk_path)
        result = run_command(cmd, timeout=120)

        if result["success"]:
            result["signed_apk"] = output_apk or apk_path
        return result

    def verify(self, apk_path: str) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        cmd = [self.apksigner_path, "verify", "--verbose", apk_path]
        result = run_command(cmd)
        result["verified"] = result["success"]
        return result

    def print_certs(self, apk_path: str) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        cmd = [self.apksigner_path, "verify", "--print-certs", apk_path]
        return run_command(cmd)

    def zipalign(
        self,
        apk_path: str,
        output_apk: Optional[str] = None,
        verify: bool = False,
    ) -> dict:
        if not os.path.exists(apk_path):
            return {"success": False, "stderr": f"APK not found: {apk_path}"}

        if verify:
            cmd = [self.zipalign_path, "-c", "-v", "4", apk_path]
        else:
            if not output_apk:
                apk_name = Path(apk_path).stem
                output_apk = str(Path(apk_path).parent / f"{apk_name}_aligned.apk")
            cmd = [self.zipalign_path, "-v", "4", apk_path, output_apk]

        result = run_command(cmd, timeout=120)
        if not verify and result["success"]:
            result["aligned_apk"] = output_apk
        return result

    def generate_keystore(
        self,
        output_path: str,
        alias: str = "pentest-key",
        password: str = "password123",
        validity: int = 10000,
        cn: str = "Mobile Pentest",
    ) -> dict:
        cmd = [
            self.keytool_path,
            "-genkey",
            "-v",
            "-keystore", output_path,
            "-alias", alias,
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", str(validity),
            "-storepass", password,
            "-keypass", password,
            "-dname", f"CN={cn}, OU=Security, O=Pentest, L=Unknown, ST=Unknown, C=US",
        ]

        result = run_command(cmd)
        if result["success"]:
            result["keystore_path"] = output_path
            result["alias"] = alias
            result["password"] = password
        return result

    def list_keystores(self) -> dict:
        keystores = []
        common_paths = [
            os.path.expanduser("~/.android/debug.keystore"),
            os.path.expanduser("~/debug.keystore"),
            str(config.WORKSPACE_DIR / "keystores"),
        ]

        for path in common_paths:
            if os.path.isfile(path):
                keystores.append(path)
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    if f.endswith((".keystore", ".jks", ".p12")):
                        keystores.append(os.path.join(path, f))

        return {"success": True, "keystores": keystores}

    def _find_debug_keystore(self) -> Optional[str]:
        debug_path = os.path.expanduser("~/.android/debug.keystore")
        if os.path.exists(debug_path):
            return debug_path
        return None
