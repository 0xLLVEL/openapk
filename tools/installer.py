import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class ToolInstaller:
    TOOLS_DIR = config.WORKSPACE_DIR / "tools_bin"

    DOWNLOAD_URLS = {
        "jadx": {
            "url": "https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip",
            "archive": "zip",
            "extract_to": "jadx",
            "binaries": {
                "windows": "jadx/bin/jadx.bat",
                "linux": "jadx/bin/jadx",
                "darwin": "jadx/bin/jadx",
            },
        },
        "dex2jar": {
            "url": "https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex-tools-v2.4.zip",
            "archive": "zip",
            "extract_to": "dex-tools-v2.4",
            "binaries": {
                "windows": "dex-tools-v2.4/d2j-dex2jar.bat",
                "linux": "dex-tools-v2.4/d2j-dex2jar.sh",
                "darwin": "dex-tools-v2.4/d2j-dex2jar.sh",
            },
        },
        "apktool": {
            "url": "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.10.0.jar",
            "archive": "jar",
            "extract_to": "apktool",
            "binaries": {
                "windows": "apktool.jar",
                "linux": "apktool.jar",
                "darwin": "apktool.jar",
            },
        },
        "uber-apk-signer": {
            "url": "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar",
            "archive": "jar",
            "extract_to": "uber-apk-signer",
            "binaries": {
                "windows": "uber-apk-signer.jar",
                "linux": "uber-apk-signer.jar",
                "darwin": "uber-apk-signer.jar",
            },
        },
    }

    def __init__(self):
        self.TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    def _get_platform(self) -> str:
        if sys.platform == "win32":
            return "windows"
        elif sys.platform == "darwin":
            return "darwin"
        return "linux"

    def _download_file(self, url: str, dest: Path) -> bool:
        try:
            print(f"Downloading {url}...")
            urllib.request.urlretrieve(url, dest)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    def _extract_zip(self, archive_path: Path, dest_dir: Path) -> bool:
        try:
            with zipfile.ZipFile(archive_path, "r") as z:
                z.extractall(dest_dir)
            return True
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False

    def _make_executable(self, path: Path) -> None:
        if sys.platform != "win32":
            try:
                os.chmod(path, 0o755)
            except Exception:
                pass

    def _create_wrapper(self, name: str, jar_path: Path) -> Path:
        wrapper_dir = self.TOOLS_DIR / "bin"
        wrapper_dir.mkdir(parents=True, exist_ok=True)

        if sys.platform == "win32":
            wrapper = wrapper_dir / f"{name}.bat"
            content = f'@echo off\njava -jar "{jar_path}" %*\n'
        else:
            wrapper = wrapper_dir / name
            content = f'#!/bin/bash\njava -jar "{jar_path}" "$@"\n'

        wrapper.write_text(content, encoding="utf-8")
        self._make_executable(wrapper)
        return wrapper

    def install_jadx(self) -> dict:
        tool_dir = self.TOOLS_DIR / "jadx"
        platform = self._get_platform()

        if tool_dir.exists():
            info = self.DOWNLOAD_URLS["jadx"]
            binary = info["binaries"][platform]
            binary_path = self.TOOLS_DIR / binary
            if binary_path.exists():
                return {"success": True, "message": "jadx already installed", "path": str(binary_path)}

        info = self.DOWNLOAD_URLS["jadx"]
        archive_path = self.TOOLS_DIR / "jadx.zip"

        if not self._download_file(info["url"], archive_path):
            return {"success": False, "stderr": "Failed to download jadx"}

        if not self._extract_zip(archive_path, self.TOOLS_DIR):
            return {"success": False, "stderr": "Failed to extract jadx"}

        bin_dir = self.TOOLS_DIR / "bin"
        lib_dir = self.TOOLS_DIR / "lib"
        if bin_dir.exists() and not tool_dir.exists():
            shutil.move(str(bin_dir), str(tool_dir / "bin"))
        if lib_dir.exists():
            shutil.move(str(lib_dir), str(tool_dir / "lib"))
        for f in ["LICENSE", "README.md"]:
            src = self.TOOLS_DIR / f
            if src.exists():
                shutil.move(str(src), str(tool_dir / f))

        binary = info["binaries"][platform]
        binary_path = self.TOOLS_DIR / binary
        self._make_executable(binary_path)

        wrapper = self._create_wrapper("jadx", binary_path)

        archive_path.unlink(missing_ok=True)

        return {
            "success": True,
            "message": "jadx installed successfully",
            "path": str(wrapper),
            "binary": str(binary_path),
        }

    def install_dex2jar(self) -> dict:
        tool_dir = self.TOOLS_DIR / "dex2jar"
        platform = self._get_platform()

        if tool_dir.exists():
            info = self.DOWNLOAD_URLS["dex2jar"]
            binary = info["binaries"][platform]
            binary_path = self.TOOLS_DIR / binary
            if binary_path.exists():
                return {"success": True, "message": "dex2jar already installed", "path": str(binary_path)}

        info = self.DOWNLOAD_URLS["dex2jar"]
        archive_path = self.TOOLS_DIR / "dex2jar.zip"

        if not self._download_file(info["url"], archive_path):
            return {"success": False, "stderr": "Failed to download dex2jar"}

        if not self._extract_zip(archive_path, self.TOOLS_DIR):
            return {"success": False, "stderr": "Failed to extract dex2jar"}

        binary = info["binaries"][platform]
        binary_path = self.TOOLS_DIR / binary
        self._make_executable(binary_path)

        archive_path.unlink(missing_ok=True)

        return {
            "success": True,
            "message": "dex2jar installed successfully",
            "path": str(binary_path),
        }

    def install_apktool(self) -> dict:
        jar_dir = self.TOOLS_DIR / "apktool"
        jar_dir.mkdir(parents=True, exist_ok=True)
        jar_path = jar_dir / "apktool.jar"

        if jar_path.exists():
            return {"success": True, "message": "apktool already installed", "path": str(jar_path)}

        info = self.DOWNLOAD_URLS["apktool"]

        if not self._download_file(info["url"], jar_path):
            return {"success": False, "stderr": "Failed to download apktool"}

        wrapper = self._create_wrapper("apktool", jar_path)

        return {
            "success": True,
            "message": "apktool installed successfully",
            "path": str(wrapper),
            "jar": str(jar_path),
        }

    def install_uber_apk_signer(self) -> dict:
        jar_dir = self.TOOLS_DIR / "uber-apk-signer"
        jar_dir.mkdir(parents=True, exist_ok=True)
        jar_path = jar_dir / "uber-apk-signer.jar"

        if jar_path.exists():
            return {"success": True, "message": "uber-apk-signer already installed", "path": str(jar_path)}

        info = self.DOWNLOAD_URLS["uber-apk-signer"]

        if not self._download_file(info["url"], jar_path):
            return {"success": False, "stderr": "Failed to download uber-apk-signer"}

        wrapper = self._create_wrapper("uber-apk-signer", jar_path)

        return {
            "success": True,
            "message": "uber-apk-signer installed successfully",
            "path": str(wrapper),
            "jar": str(jar_path),
        }

    def install_all_missing(self) -> dict:
        from tools.checker import SystemChecker

        checker = SystemChecker()
        results = {}

        jadx_status = checker.check_jadx()
        if jadx_status["status"] != "ok":
            results["jadx"] = self.install_jadx()

        dex2jar_status = checker.check_dex2jar()
        if dex2jar_status["status"] != "ok":
            results["dex2jar"] = self.install_dex2jar()

        apktool_status = checker.check_apktool()
        if apktool_status["status"] != "ok":
            results["apktool"] = self.install_apktool()

        return {
            "success": True,
            "installed": results,
            "message": f"Installed {len(results)} tools",
        }

    def install(self, tool_name: str) -> dict:
        installers = {
            "jadx": self.install_jadx,
            "dex2jar": self.install_dex2jar,
            "apktool": self.install_apktool,
            "uber-apk-signer": self.install_uber_apk_signer,
        }

        if tool_name not in installers:
            return {
                "success": False,
                "stderr": f"Unknown tool: {tool_name}. Available: {list(installers.keys())}",
            }

        return installers[tool_name]()

    def list_installed(self) -> dict:
        installed = {}
        for name, info in self.DOWNLOAD_URLS.items():
            tool_dir = self.TOOLS_DIR / info["extract_to"]
            installed[name] = {
                "installed": tool_dir.exists(),
                "path": str(tool_dir) if tool_dir.exists() else None,
            }
        return {"success": True, "tools": installed, "tools_dir": str(self.TOOLS_DIR)}
