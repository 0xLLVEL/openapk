# OpenAPK

A Python MCP (Model Context Protocol) server for mobile application penetration testing with 83+ tools covering Frida, Frida-server, Frida-gadget, apktool, jadx, dex2jar, smali, APK analysis, APK decompile/build, APK signing, emulator support, and system compatibility checking.

## Features

- **83 MCP Tools** for mobile pentesting
- **Auto-download** missing tools (jadx, dex2jar, apktool, build-tools)
- **Frida Integration** - Server management, script execution, gadget injection
- **55+ FSR Scripts** - SSL bypass, root bypass, emulator bypass, and more
- **APK Analysis** - Manifest, permissions, activities, services, secrets scan
- **Decompilation** - Java source (jadx), Smali (apktool), DEX to JAR (dex2jar)
- **APK Signing** - Sign, verify, zipalign, keystore generation
- **Emulator Support** - Nox Player, BlueStacks, MEmu
- **System Check** - Verify all tools are installed and working

## Requirements

- Python 3.10+
- ADB (Android Debug Bridge)
- Frida tools
- Java JDK 11+

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/openapk.git
cd openapk
```

### 2. Run setup (creates venv + installs requirements)

```bash
setup.bat
```

### 3. Configure opencode

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "openapk": {
      "type": "local",
      "command": ["C:\\path\\to\\openapk\\.venv\\Scripts\\python.exe", "C:\\path\\to\\openapk\\server.py"],
      "enabled": true,
      "timeout": 30000
    }
  }
}
```

### 4. Restart opencode

The MCP server will load automatically.

## Quick Start

```
# Check system status
check_system

# Install all missing tools
install_all_missing

# Update FSR scripts
fsr_update_scripts

# Connect to Nox Player
connect_nox

# Analyze an APK
apk_analyze("path/to/app.apk")
```

## Available Tools (83)

### System Check (6)

| Tool | Description |
|------|-------------|
| `check_system` | Full system compatibility check |
| `check_core_tools` | Python, ADB, Frida, Java, Frida Gadget |
| `check_decompile_tools` | jadx, apktool, dex2jar |
| `check_signing_tools` | apksigner, keytool, zipalign, aapt |
| `check_emulators` | Nox, BlueStacks, MEmu |
| `check_frida_scripts` | Verify pre-built scripts |

### Tool Installer (7)

| Tool | Description |
|------|-------------|
| `install_tool` | Install any tool by name |
| `install_jadx` | Download & install jadx |
| `install_dex2jar` | Download & install dex2jar |
| `install_apktool` | Download & install apktool |
| `install_uber_apk_signer` | Download & install uber-apk-signer |
| `install_build_tools` | Download & install Android SDK Build Tools |
| `install_all_missing` | Auto-detect & install all missing tools |
| `list_installed_tools` | Show tools installed by MCP |

### ADB Device Management (13)

| Tool | Description |
|------|-------------|
| `adb_list_devices` | List all connected devices |
| `adb_connect` | Connect via TCP/IP |
| `adb_disconnect` | Disconnect from device |
| `adb_shell` | Execute shell command |
| `adb_install_apk` | Install APK to device |
| `adb_uninstall_app` | Uninstall app |
| `adb_push` | Push file to device |
| `adb_pull` | Pull file from device |
| `adb_screenshot` | Capture screenshot |
| `adb_logcat` | Get device logs |
| `adb_get_props` | Get device properties |
| `adb_start_app` | Start application |
| `adb_stop_app` | Force stop application |

### Emulator Management (5)

| Tool | Description |
|------|-------------|
| `detect_emulators` | Detect installed emulators |
| `connect_nox` | Connect to Nox Player |
| `connect_emulator` | Connect to any emulator |
| `start_nox` | Start Nox Player |
| `start_emulator` | Start any emulator |

### Frida Server (7)

| Tool | Description |
|------|-------------|
| `frida_start_server` | Auto-download & start frida-server |
| `frida_stop_server` | Stop frida-server |
| `frida_restart_server` | Restart frida-server |
| `frida_check_server` | Check if frida-server running |
| `frida_get_version` | Get frida-server version |
| `frida_list_processes` | List running processes |
| `frida_list_apps` | List installed apps |

### Frida Script Runner (13)

| Tool | Description |
|------|-------------|
| `frida_run_script` | Run custom Frida script |
| `frida_run_script_file` | Run script from file |
| `frida_ssl_bypass` | Bypass SSL pinning |
| `frida_root_bypass` | Bypass root detection |
| `frida_emulator_bypass` | Bypass emulator detection |
| `frida_anti_debug_bypass` | Bypass anti-debug |
| `frida_trace_function` | Trace Java method |
| `frida_find_classes` | Find loaded classes |
| `frida_find_methods` | List class methods |
| `frida_list_modules` | List native modules |
| `frida_memory_dump` | Dump memory at address |
| `frida_memory_scan` | Scan memory for pattern |

### Frida Gadget (4)

| Tool | Description |
|------|-------------|
| `gadget_inject` | Inject Frida Gadget into APK |
| `gadget_inject_with_script` | Inject Gadget + custom JS |
| `gadget_inject_custom` | Inject custom Gadget .so |
| `gadget_verify` | Check if Gadget present |

### FSR Scripts (6)

| Tool | Description |
|------|-------------|
| `fsr_list_scripts` | List available FSR scripts |
| `fsr_run_script` | Run a specific FSR script |
| `fsr_run_category` | Run all scripts in a category |
| `fsr_run_ssl_bypass_all` | Run all SSL bypass scripts |
| `fsr_update_scripts` | Download/update FSR scripts from GitHub |

### APK Analysis (11)

| Tool | Description |
|------|-------------|
| `apk_analyze` | Full APK analysis |
| `apk_manifest` | Dump AndroidManifest.xml |
| `apk_permissions` | List permissions |
| `apk_activities` | List activities |
| `apk_services` | List services |
| `apk_providers` | List content providers |
| `apk_receivers` | List broadcast receivers |
| `apk_certificates` | Show signing certificates |
| `apk_deep_links` | Extract deep links |
| `apk_native_libs` | List native libraries |
| `apk_secrets_scan` | Scan for secrets/API keys |

### Decompile (6)

| Tool | Description |
|------|-------------|
| `decompile_jadx` | Decompile to Java source |
| `decompile_apktool` | Decompile to Smali + resources |
| `decompile_dex2jar` | Convert DEX to JAR |
| `smali_disassemble` | DEX → Smali |
| `smali_assemble` | Smali → DEX |
| `apk_extract_dex` | Extract DEX from APK |

### Build & Sign (6)

| Tool | Description |
|------|-------------|
| `apk_build` | Build APK from decoded dir |
| `apk_sign` | Sign APK with keystore |
| `apk_verify_signature` | Verify APK signature |
| `apk_zipalign` | Zipalign APK |
| `apk_generate_keystore` | Generate signing keystore |
| `apk_list_keystores` | List available keystores |

## FSR Script Categories

| Category | Scripts | Description |
|----------|---------|-------------|
| `android` | 9 | Biometric bypass, emulator bypass, pin bypass |
| `ios` | 15 | Jailbreak bypass, SSL, biometric |
| `ssl` | 21 | Universal SSL bypass, OkHttp, Flutter, TikTok |
| `root` | 10 | Root detection bypass variants |

## Project Structure

```
openapk/
├── server.py                  # MCP server entry point (83 tools)
├── config.py                  # Paths and emulator configs
├── requirements.txt           # Python dependencies
├── setup.bat                  # Windows setup script
├── start.bat                  # Windows start script
├── tools/
│   ├── adb.py                 # ADB + emulator management
│   ├── frida_manager.py       # Frida server lifecycle
│   ├── frida_runner.py        # Frida script execution
│   ├── frida_gadget.py        # Gadget injection
│   ├── apk_analyzer.py        # APK analysis
│   ├── decompiler.py          # jadx/apktool/dex2jar/smali
│   ├── builder.py             # APK build
│   ├── signer.py              # APK signing
│   ├── checker.py             # System compatibility check
│   ├── installer.py           # Tool downloader/installer
│   └── utils.py               # Shared utilities
├── frida_scripts/
│   ├── *.js                   # Pre-built bypass scripts
│   └── fsr/                   # FSR scripts (55+)
│       ├── android/
│       ├── ios/
│       ├── ssl/
│       └── root/
└── workspace/
    ├── apks/                  # User APK files
    ├── decoded/               # Decompiled output
    ├── java_src/              # Java source output
    ├── smali/                 # Smali output
    ├── jars/                  # JAR output
    └── tools_bin/             # Auto-downloaded tools
        ├── jadx/
        ├── dex-tools-v2.4/
        ├── apktool/
        ├── uber-apk-signer/
        └── build-tools/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ADB_PATH` | `adb` | Path to ADB executable |
| `JADX_PATH` | `jadx` | Path to jadx |
| `APKTOOL_PATH` | `apktool` | Path to apktool |
| `DEX2JAR_PATH` | `d2j-dex2jar` | Path to dex2jar |
| `JAVA_HOME` | - | Java installation path |
| `NOX_ADB_HOST` | `127.0.0.1` | Nox ADB host |
| `NOX_ADB_PORT` | `62001` | Nox ADB port |

## License

MIT
