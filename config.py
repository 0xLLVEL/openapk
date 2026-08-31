import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
WORKSPACE_DIR = BASE_DIR / "workspace"
FRIDA_SCRIPTS_DIR = BASE_DIR / "frida_scripts"

APKS_DIR = WORKSPACE_DIR / "apks"
DECODED_DIR = WORKSPACE_DIR / "decoded"
JAVA_SRC_DIR = WORKSPACE_DIR / "java_src"
SMALI_DIR = WORKSPACE_DIR / "smali"
JARS_DIR = WORKSPACE_DIR / "jars"

ADB_PATH = os.environ.get("ADB_PATH", "adb")
JADX_PATH = os.environ.get("JADX_PATH", "jadx")
JADX_GUI_PATH = os.environ.get("JADX_GUI_PATH", "jadx-gui")
APKTOOL_PATH = os.environ.get("APKTOOL_PATH", "apktool")
DEX2JAR_PATH = os.environ.get("DEX2JAR_PATH", "d2j-dex2jar.sh")
APKSIGNER_PATH = os.environ.get("APKSIGNER_PATH", "apksigner")
KEYTOOL_PATH = os.environ.get("KEYTOOL_PATH", "keytool")
ZIPALIGN_PATH = os.environ.get("ZIPALIGN_PATH", "zipalign")
AAPT_PATH = os.environ.get("AAPT_PATH", "aapt")
AAPT2_PATH = os.environ.get("AAPT2_PATH", "aapt2")
FRIDA_GADGET_PATH = os.environ.get("FRIDA_GADGET_PATH", "frida-gadget")
JAVA_HOME = os.environ.get("JAVA_HOME", "")
ANDROID_HOME = os.environ.get("ANDROID_HOME", "")
FRIDA_SERVER_VERSION = os.environ.get("FRIDA_SERVER_VERSION", "")
FRIDA_SERVER_DIR = WORKSPACE_DIR / "frida_server"

NOX_ADB_PORT = int(os.environ.get("NOX_ADB_PORT", "62001"))
NOX_ADB_HOST = os.environ.get("NOX_ADB_HOST", "127.0.0.1")

EMULATOR_CONFIGS = {
    "nox": {
        "name": "Nox Player",
        "adb_paths": [
            r"C:\Program Files (x86)\nox\bin\nox_adb.exe",
            r"C:\Program Files\nox\bin\nox_adb.exe",
            os.path.expanduser(r"~\AppData\Local\Nox\bin\nox_adb.exe"),
            os.path.expanduser(r"~\nox\bin\nox_adb.exe"),
        ],
        "default_host": NOX_ADB_HOST,
        "default_port": NOX_ADB_PORT,
        "common_ports": [62001, 5555, 5556, 5557, 5558, 5559, 5560],
        "arch": "x86_64",
        "is_emulator": True,
    },
    "bluestacks": {
        "name": "BlueStacks",
        "adb_paths": [
            r"C:\Program Files\BlueStacks_nxt\hd-adb.exe",
            r"C:\Program Files (x86)\BlueStacks\HD-Adb.exe",
        ],
        "default_host": "127.0.0.1",
        "default_port": 5555,
        "common_ports": [5555, 5556],
        "arch": "x86_64",
        "is_emulator": True,
    },
    "memu": {
        "name": "MEmu Play",
        "adb_paths": [
            r"C:\Program Files\MEmu\adb.exe",
            r"C:\Program Files (x86)\MEmu\adb.exe",
        ],
        "default_host": "127.0.0.1",
        "default_port": 21503,
        "common_ports": [21503, 21504, 21505],
        "arch": "x86_64",
        "is_emulator": True,
    },
}

WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
APKS_DIR.mkdir(parents=True, exist_ok=True)
DECODED_DIR.mkdir(parents=True, exist_ok=True)
JAVA_SRC_DIR.mkdir(parents=True, exist_ok=True)
SMALI_DIR.mkdir(parents=True, exist_ok=True)
JARS_DIR.mkdir(parents=True, exist_ok=True)
FRIDA_SERVER_DIR.mkdir(parents=True, exist_ok=True)
