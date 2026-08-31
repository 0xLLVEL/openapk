from mcp.server.mcpserver import MCPServer

from tools import (
    ADBManager,
    FridaServerManager,
    FridaScriptRunner,
    FridaGadgetInjector,
    APKAnalyzer,
    Decompiler,
    APKBuilder,
    APKSigner,
    SystemChecker,
    ToolInstaller,
)

mcp = MCPServer("openapk")

adb = ADBManager()
frida_server = FridaServerManager()
frida_runner = FridaScriptRunner()
frida_gadget = FridaGadgetInjector()
apk_analyzer = APKAnalyzer()
decompiler = Decompiler()
builder = APKBuilder()
signer = APKSigner()
checker = SystemChecker()
installer = ToolInstaller()


# ========== System Compatibility Check ==========


@mcp.tool()
def check_system() -> dict:
    """Full system compatibility check - all tools, emulators, scripts, workspace."""
    return checker.run_full_check()


@mcp.tool()
def check_core_tools() -> dict:
    """Check core tools: Python, ADB, Frida, Java, Frida Gadget."""
    return {
        "success": True,
        "python": checker.check_python(),
        "adb": checker.check_adb(),
        "frida": checker.check_frida(),
        "frida_gadget": checker.check_frida_gadget(),
        "java": checker.check_java(),
    }


@mcp.tool()
def check_decompile_tools() -> dict:
    """Check decompilation tools: jadx, apktool, dex2jar."""
    return {
        "success": True,
        "jadx": checker.check_jadx(),
        "apktool": checker.check_apktool(),
        "dex2jar": checker.check_dex2jar(),
    }


@mcp.tool()
def check_signing_tools() -> dict:
    """Check signing tools: apksigner, keytool, zipalign, aapt."""
    return {
        "success": True,
        "apksigner": checker.check_apksigner(),
        "keytool": checker.check_keytool(),
        "zipalign": checker.check_zipalign(),
        "aapt": checker.check_aapt(),
    }


@mcp.tool()
def check_emulators() -> dict:
    """Check installed emulators: Nox Player, BlueStacks, MEmu."""
    return {
        "success": True,
        "nox": checker.check_nox(),
        "bluestacks": checker.check_bluestacks(),
        "memu": checker.check_memu(),
    }


@mcp.tool()
def check_frida_scripts() -> dict:
    """Check if all pre-built Frida scripts are present."""
    return checker.check_frida_scripts()


# ========== Tool Installer ==========


@mcp.tool()
def install_tool(tool_name: str) -> dict:
    """Install a missing tool. Available: jadx, dex2jar, apktool, uber-apk-signer"""
    return installer.install(tool_name)


@mcp.tool()
def install_jadx() -> dict:
    """Download and install jadx (DEX to Java decompiler)."""
    return installer.install_jadx()


@mcp.tool()
def install_dex2jar() -> dict:
    """Download and install dex2jar (DEX to JAR converter)."""
    return installer.install_dex2jar()


@mcp.tool()
def install_apktool() -> dict:
    """Download and install apktool (APK decompiler/builder)."""
    return installer.install_apktool()


@mcp.tool()
def install_uber_apk_signer() -> dict:
    """Download and install uber-apk-signer (APK signing tool)."""
    return installer.install_uber_apk_signer()


@mcp.tool()
def install_build_tools() -> dict:
    """Download and install Android SDK Build Tools (apksigner, zipalign, aapt)."""
    return installer.install_build_tools()


@mcp.tool()
def install_all_missing() -> dict:
    """Auto-detect and install all missing tools."""
    return installer.install_all_missing()


@mcp.tool()
def list_installed_tools() -> dict:
    """List all tools installed by the MCP server."""
    return installer.list_installed()


# ========== ADB Device Management ==========


@mcp.tool()
def adb_list_devices() -> dict:
    """List all connected Android devices and emulators."""
    return adb.list_devices()


@mcp.tool()
def adb_connect(address: str) -> dict:
    """Connect to a device via TCP/IP. Example: 192.168.1.100:5555"""
    return adb.connect(address)


@mcp.tool()
def adb_disconnect(address: str = "") -> dict:
    """Disconnect from a TCP/IP device."""
    return adb.disconnect(address) if address else adb.disconnect()


@mcp.tool()
def adb_install_apk(apk_path: str, device_id: str = "") -> dict:
    """Install an APK to a connected device."""
    return adb.install_apk(apk_path, device_id or None)


@mcp.tool()
def adb_uninstall_app(package_name: str, device_id: str = "") -> dict:
    """Uninstall an app from the device."""
    return adb.uninstall_app(package_name, device_id or None)


@mcp.tool()
def adb_shell(command: str, device_id: str = "") -> dict:
    """Execute a shell command on the device."""
    return adb.shell(command, device_id or None)


@mcp.tool()
def adb_pull(remote_path: str, local_path: str, device_id: str = "") -> dict:
    """Pull a file from the device to local filesystem."""
    return adb.pull(remote_path, local_path, device_id or None)


@mcp.tool()
def adb_push(local_path: str, remote_path: str, device_id: str = "") -> dict:
    """Push a file from local filesystem to the device."""
    return adb.push(local_path, remote_path, device_id or None)


@mcp.tool()
def adb_screenshot(device_id: str = "") -> dict:
    """Capture a screenshot from the connected device."""
    return adb.screenshot(device_id or None)


@mcp.tool()
def adb_logcat(device_id: str = "", filter_expr: str = "", lines: int = 100) -> dict:
    """Get device logs with optional filter."""
    return adb.logcat(device_id or None, filter_expr or None, lines)


@mcp.tool()
def adb_start_app(package_name: str, activity: str = "", device_id: str = "") -> dict:
    """Start an application on the device."""
    return adb.start_app(package_name, activity or None, device_id or None)


@mcp.tool()
def adb_stop_app(package_name: str, device_id: str = "") -> dict:
    """Force stop an application on the device."""
    return adb.stop_app(package_name, device_id or None)


@mcp.tool()
def adb_get_props(device_id: str = "") -> dict:
    """Get device properties (model, brand, Android version, etc.)."""
    return adb.get_props(device_id or None)


# ========== Emulator Management (Nox, BlueStacks, MEmu) ==========


@mcp.tool()
def detect_emulators() -> dict:
    """Detect installed emulators (Nox Player, BlueStacks, MEmu)."""
    return adb.detect_emulators()


@mcp.tool()
def connect_nox(port: int = 62001, host: str = "") -> dict:
    """Connect to Nox Player via ADB. Default port: 62001"""
    return adb.connect_nox(port, host)


@mcp.tool()
def connect_emulator(emulator: str, port: int = 0, host: str = "") -> dict:
    """Connect to an emulator (nox, bluestacks, memu)."""
    return adb.connect_emulator(emulator, port or None, host)


@mcp.tool()
def start_emulator(emulator: str) -> dict:
    """Start an emulator (nox, bluestacks, memu)."""
    return adb.start_emulator(emulator)


@mcp.tool()
def start_nox() -> dict:
    """Start Nox Player."""
    return adb.start_nox()


# ========== Frida Server Management ==========


@mcp.tool()
def frida_check_server(device_id: str = "") -> dict:
    """Check if frida-server is running on the device."""
    return frida_server.check_server(device_id or None)


@mcp.tool()
def frida_start_server(device_id: str = "", version: str = "") -> dict:
    """Auto-download, push, and start frida-server on the device."""
    return frida_server.start_server(device_id or None, version or None)


@mcp.tool()
def frida_stop_server(device_id: str = "") -> dict:
    """Stop frida-server on the device."""
    return frida_server.stop_server(device_id or None)


@mcp.tool()
def frida_restart_server(device_id: str = "", version: str = "") -> dict:
    """Restart frida-server on the device."""
    return frida_server.restart_server(device_id or None, version or None)


@mcp.tool()
def frida_get_version(device_id: str = "") -> dict:
    """Get frida-server version running on the device."""
    return frida_server.get_version(device_id or None)


@mcp.tool()
def frida_list_processes(device_id: str = "") -> dict:
    """List running processes on the device via Frida."""
    return frida_server.list_processes(device_id or None)


@mcp.tool()
def frida_list_apps(device_id: str = "") -> dict:
    """List installed third-party apps on the device."""
    return frida_server.list_apps(device_id or None)


# ========== Frida Script Runner ==========


@mcp.tool()
def frida_run_script(
    package_name: str,
    script_source: str,
    device_id: str = "",
    spawn: bool = True,
    runtime: str = "v8",
    timeout: int = 30,
) -> dict:
    """Inject and run a custom Frida script against an app."""
    return frida_runner.run_script(
        package_name, script_source, device_id or None, spawn, runtime, timeout
    )


@mcp.tool()
def frida_run_script_file(
    package_name: str,
    script_path: str,
    device_id: str = "",
    spawn: bool = True,
    timeout: int = 30,
) -> dict:
    """Run a Frida script from a file."""
    return frida_runner.run_script_file(
        package_name, script_path, device_id or None, spawn, timeout=timeout
    )


@mcp.tool()
def frida_ssl_bypass(package_name: str, device_id: str = "", spawn: bool = True) -> dict:
    """Run SSL pinning bypass script on the target app."""
    return frida_runner.run_ssl_bypass(package_name, device_id or None, spawn)


@mcp.tool()
def frida_root_bypass(package_name: str, device_id: str = "", spawn: bool = True) -> dict:
    """Run root detection bypass script on the target app."""
    return frida_runner.run_root_bypass(package_name, device_id or None, spawn)


@mcp.tool()
def frida_emulator_bypass(package_name: str, device_id: str = "", spawn: bool = True) -> dict:
    """Run emulator detection bypass script on the target app."""
    return frida_runner.run_emulator_bypass(package_name, device_id or None, spawn)


@mcp.tool()
def frida_anti_debug_bypass(package_name: str, device_id: str = "", spawn: bool = True) -> dict:
    """Run anti-debug bypass script on the target app."""
    return frida_runner.run_anti_debug_bypass(package_name, device_id or None, spawn)


@mcp.tool()
def frida_trace_function(package_name: str, class_method: str, device_id: str = "", spawn: bool = True) -> dict:
    """Trace a Java method. Format: com.example.MyClass.methodName"""
    return frida_runner.trace_function(package_name, class_method, device_id or None, spawn)


@mcp.tool()
def frida_list_modules(package_name: str, device_id: str = "") -> dict:
    """List loaded native modules in the target process."""
    return frida_runner.list_modules(package_name, device_id or None)


@mcp.tool()
def frida_find_classes(package_name: str, pattern: str, device_id: str = "") -> dict:
    """Find loaded classes matching a pattern (partial match)."""
    return frida_runner.find_classes(package_name, pattern, device_id or None)


# ========== Frida Script Runner (FSR) ==========


@mcp.tool()
def fsr_list_scripts(category: str = "") -> dict:
    """List available FSR scripts. Categories: android, ios, ssl, root, all"""
    from pathlib import Path
    import config

    fsr_dir = config.FRIDA_SCRIPTS_DIR / "fsr"
    if not fsr_dir.exists():
        return {"success": False, "error": "FSR scripts not found. Run install_fsr_scripts first."}

    categories = {}
    for cat_dir in fsr_dir.iterdir():
        if cat_dir.is_dir():
            scripts = [f.name for f in cat_dir.glob("*.js")]
            categories[cat_dir.name] = scripts

    if category and category != "all":
        if category not in categories:
            return {"success": False, "error": f"Category '{category}' not found. Available: {list(categories.keys())}"}
        return {"success": True, "category": category, "scripts": categories[category]}

    return {"success": True, "categories": categories, "total": sum(len(s) for s in categories.values())}


@mcp.tool()
def fsr_run_script(
    package_name: str,
    category: str,
    script_name: str,
    device_id: str = "",
    spawn: bool = True,
    timeout: int = 30,
) -> dict:
    """Run a FSR script by category and name. Use fsr_list_scripts to see available scripts."""
    from pathlib import Path
    import config

    fsr_dir = config.FRIDA_SCRIPTS_DIR / "fsr" / category / script_name
    if not fsr_dir.exists():
        return {"success": False, "error": f"Script not found: {category}/{script_name}"}

    return frida_runner.run_script_file(
        package_name, str(fsr_dir), device_id or None, spawn, timeout=timeout
    )


@mcp.tool()
def fsr_run_category(
    package_name: str,
    category: str,
    device_id: str = "",
    spawn: bool = True,
    timeout: int = 30,
) -> dict:
    """Run all scripts in a FSR category sequentially."""
    from pathlib import Path
    import config

    fsr_dir = config.FRIDA_SCRIPTS_DIR / "fsr" / category
    if not fsr_dir.exists():
        return {"success": False, "error": f"Category '{category}' not found"}

    scripts = list(fsr_dir.glob("*.js"))
    if not scripts:
        return {"success": False, "error": f"No scripts found in category '{category}'"}

    results = []
    for script in scripts:
        result = frida_runner.run_script_file(
            package_name, str(script), device_id or None, spawn, timeout=timeout
        )
        results.append({"script": script.name, "result": result})

    return {"success": True, "category": category, "executed": len(results), "results": results}


@mcp.tool()
def fsr_run_ssl_bypass_all(
    package_name: str,
    device_id: str = "",
    spawn: bool = True,
) -> dict:
    """Run all SSL bypass scripts from FSR."""
    from pathlib import Path
    import config

    ssl_dir = config.FRIDA_SCRIPTS_DIR / "fsr" / "ssl"
    if not ssl_dir.exists():
        return {"success": False, "error": "SSL scripts not found"}

    scripts = list(ssl_dir.glob("*.js"))
    results = []
    for script in scripts:
        result = frida_runner.run_script_file(
            package_name, str(script), device_id or None, spawn, timeout=10
        )
        results.append({"script": script.name, "success": result.get("success", False)})

    return {
        "success": True,
        "executed": len(results),
        "bypassed": sum(1 for r in results if r["success"]),
        "results": results,
    }


@mcp.tool()
def fsr_update_scripts() -> dict:
    """Download or update FSR scripts from GitHub."""
    import subprocess
    import shutil
    from pathlib import Path
    import config

    fsr_dir = config.WORKSPACE_DIR / "Frida-Script-Runner"
    fsr_scripts = config.FRIDA_SCRIPTS_DIR / "fsr"
    repo_url = "https://github.com/z3n70/Frida-Script-Runner.git"

    try:
        if fsr_dir.exists():
            result = subprocess.run(
                ["git", "-C", str(fsr_dir), "pull"],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                return {"success": False, "error": f"Git pull failed: {result.stderr}"}
            action = "updated"
        else:
            result = subprocess.run(
                ["git", "clone", repo_url, str(fsr_dir), "--depth", "1"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                return {"success": False, "error": f"Git clone failed: {result.stderr}"}
            action = "downloaded"

        scripts_src = fsr_dir / "scripts"
        if not scripts_src.exists():
            return {"success": False, "error": "Scripts directory not found in repo"}

        if fsr_scripts.exists():
            shutil.rmtree(fsr_scripts)

        for category in scripts_src.iterdir():
            if category.is_dir() and category.name.startswith("Script Directory"):
                continue
            if category.is_dir():
                cat_dst = fsr_scripts / category.name.lower().replace(" ", "-")
                cat_dst.mkdir(parents=True, exist_ok=True)
                for js_file in category.glob("*.js"):
                    shutil.copy2(js_file, cat_dst / js_file.name)

        for js_file in scripts_src.glob("*.js"):
            cat_name = "misc"
            for cat in ["android", "ios", "ssl", "root"]:
                if cat in js_file.name.lower():
                    cat_name = cat
                    break
            cat_dst = fsr_scripts / cat_name
            cat_dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(js_file, cat_dst / js_file.name)

        total = sum(1 for _ in fsr_scripts.rglob("*.js"))

        return {
            "success": True,
            "action": action,
            "total_scripts": total,
            "path": str(fsr_scripts),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Download timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def frida_find_methods(package_name: str, class_name: str, device_id: str = "") -> dict:
    """List all methods of a Java class."""
    return frida_runner.find_methods(package_name, class_name, device_id or None)


@mcp.tool()
def frida_memory_dump(package_name: str, address: str, size: int, device_id: str = "") -> dict:
    """Dump memory at a specific address. Address in hex: 0x7fff00000000"""
    return frida_runner.memory_dump(package_name, address, size, device_id or None)


@mcp.tool()
def frida_memory_scan(package_name: str, pattern: str, device_id: str = "") -> dict:
    """Scan memory for a byte pattern. Pattern: '48 89 E5 48 83'"""
    return frida_runner.memory_scan(package_name, pattern, device_id or None)


# ========== Frida Gadget Injection ==========


@mcp.tool()
def gadget_inject(
    apk_path: str,
    arch: str = "",
    sign: bool = True,
    js_script: str = "",
    js_delay: int = 2,
    frida_version: str = "",
) -> dict:
    """Inject Frida Gadget into an APK. Auto-detects arch if not specified."""
    return frida_gadget.inject(
        apk_path,
        arch=arch or None,
        sign=sign,
        js_script=js_script or None,
        js_delay=js_delay,
        frida_version=frida_version or None,
    )


@mcp.tool()
def gadget_inject_with_script(
    apk_path: str,
    js_script_path: str,
    arch: str = "",
    sign: bool = True,
    js_delay: int = 2,
) -> dict:
    """Inject Frida Gadget + custom JavaScript into an APK."""
    return frida_gadget.inject_with_script(
        apk_path, js_script_path, arch=arch or None, sign=sign, js_delay=js_delay
    )


@mcp.tool()
def gadget_inject_custom(apk_path: str, gadget_so_path: str, sign: bool = True) -> dict:
    """Inject a custom Frida Gadget .so file into an APK."""
    return frida_gadget.inject_custom_gadget(apk_path, gadget_so_path, sign=sign)


@mcp.tool()
def gadget_verify(apk_path: str) -> dict:
    """Check if Frida Gadget is present in an APK."""
    return frida_gadget.verify_injection(apk_path)


# ========== APK Analysis ==========


@mcp.tool()
def apk_analyze(apk_path: str) -> dict:
    """Full APK analysis: package info, permissions, activities, services."""
    return apk_analyzer.analyze(apk_path)


@mcp.tool()
def apk_manifest(apk_path: str) -> dict:
    """Dump AndroidManifest.xml from an APK."""
    return apk_analyzer.manifest(apk_path)


@mcp.tool()
def apk_permissions(apk_path: str) -> dict:
    """List all permissions requested by the APK."""
    return apk_analyzer.get_permissions(apk_path)


@mcp.tool()
def apk_activities(apk_path: str) -> dict:
    """List all activities in the APK."""
    return apk_analyzer.get_activities(apk_path)


@mcp.tool()
def apk_services(apk_path: str) -> dict:
    """List all services in the APK."""
    return apk_analyzer.get_services(apk_path)


@mcp.tool()
def apk_receivers(apk_path: str) -> dict:
    """List all broadcast receivers in the APK."""
    return apk_analyzer.get_receivers(apk_path)


@mcp.tool()
def apk_providers(apk_path: str) -> dict:
    """List all content providers in the APK."""
    return apk_analyzer.get_providers(apk_path)


@mcp.tool()
def apk_deep_links(apk_path: str) -> dict:
    """Extract deep links and intent filters from the APK."""
    return apk_analyzer.get_deep_links(apk_path)


@mcp.tool()
def apk_certificates(apk_path: str) -> dict:
    """Show signing certificate information for the APK."""
    return apk_analyzer.get_certificates(apk_path)


@mcp.tool()
def apk_native_libs(apk_path: str) -> dict:
    """List native libraries (.so files) in the APK."""
    return apk_analyzer.get_native_libs(apk_path)


@mcp.tool()
def apk_secrets_scan(apk_path: str) -> dict:
    """Scan APK for hardcoded secrets, API keys, and credentials."""
    return apk_analyzer.scan_secrets(apk_path)


# ========== Decompilation ==========


@mcp.tool()
def decompile_jadx(apk_path: str, output_dir: str = "", no_res: bool = False, threads: int = 4) -> dict:
    """Decompile APK to Java source using jadx."""
    return decompiler.decompile_jadx(apk_path, output_dir or None, no_res, threads)


@mcp.tool()
def decompile_apktool(
    apk_path: str, output_dir: str = "", no_src: bool = False, no_res: bool = False
) -> dict:
    """Decompile APK to Smali + resources using apktool."""
    return decompiler.decompile_apktool(apk_path, output_dir or None, no_src=no_src, no_res=no_res)


@mcp.tool()
def decompile_dex2jar(apk_path: str, output_jar: str = "") -> dict:
    """Convert APK DEX files to JAR using dex2jar."""
    return decompiler.decompile_dex2jar(apk_path, output_jar or None)


@mcp.tool()
def smali_disassemble(dex_path: str, output_dir: str = "") -> dict:
    """Disassemble a DEX file to Smali."""
    return decompiler.disassemble_smali(dex_path, output_dir or None)


@mcp.tool()
def smali_assemble(smali_dir: str, output_dex: str = "") -> dict:
    """Assemble Smali files to a DEX."""
    return decompiler.assemble_smali(smali_dir, output_dex or None)


@mcp.tool()
def apk_extract_dex(apk_path: str) -> dict:
    """Extract DEX files from an APK."""
    return decompiler.extract_dex(apk_path)


# ========== Build & Sign ==========


@mcp.tool()
def apk_build(
    decoded_dir: str,
    output_apk: str = "",
    use_aapt2: bool = False,
    net_sec_conf: bool = False,
    debuggable: bool = False,
) -> dict:
    """Build an APK from a decoded apktool directory."""
    return builder.build(decoded_dir, output_apk or None, use_aapt2=use_aapt2, net_sec_conf=net_sec_conf, debuggable=debuggable)


@mcp.tool()
def apk_sign(
    apk_path: str,
    keystore_path: str = "",
    keystore_pass: str = "",
    key_alias: str = "",
    key_pass: str = "",
    output_apk: str = "",
) -> dict:
    """Sign an APK with a keystore. Uses debug keystore if none provided."""
    return signer.sign(
        apk_path,
        keystore_path or None,
        keystore_pass or None,
        key_alias or None,
        key_pass or None,
        output_apk or None,
    )


@mcp.tool()
def apk_verify_signature(apk_path: str) -> dict:
    """Verify the signature of an APK."""
    return signer.verify(apk_path)


@mcp.tool()
def apk_zipalign(apk_path: str, output_apk: str = "") -> dict:
    """Zipalign an APK for optimization. Run before signing."""
    return signer.zipalign(apk_path, output_apk or None)


@mcp.tool()
def apk_generate_keystore(
    output_path: str,
    alias: str = "pentest-key",
    password: str = "password123",
    validity: int = 10000,
) -> dict:
    """Generate a new signing keystore for APK signing."""
    return signer.generate_keystore(output_path, alias, password, validity)


@mcp.tool()
def apk_list_keystores() -> dict:
    """List available keystores (debug + custom)."""
    return signer.list_keystores()


if __name__ == "__main__":
    mcp.run()
