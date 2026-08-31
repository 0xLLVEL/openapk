Java.perform(function () {
    console.log("[*] Emulator Detection Bypass loaded (Nox, BlueStacks, MEmu, AVD)");

    // Build.MODEL - fake as real device
    try {
        var Build = Java.use("android.os.Build");
        Build.MODEL.value = "Samsung Galaxy S21";
        Build.MANUFACTURER.value = "samsung";
        Build.BRAND.value = "samsung";
        Build.DEVICE.value = "o1s";
        Build.PRODUCT.value = "o1sxx";
        Build.HARDWARE.value = "exynos2100";
        Build.FINGERPRINT.value = "samsung/o1sxx/o1s:12/SP1A.210812.016/G991BXXSDBUIA5:user/release-keys";
        Build.BOARD.value = "exynos2100";
        Build.DISPLAY.value = "SP1A.210812.016";
        Build.HOST.value = "219K25820000588";
        Build.TAGS.value = "release-keys";
        Build.TYPE.value = "user";
        Build.USER.value = "ubuntu";
        console.log("[+] Build properties spoofed");
    } catch (e) {}

    // SystemProperties
    try {
        var SystemProperties = Java.use("android.os.SystemProperties");
        SystemProperties.get.overload("java.lang.String").implementation = function (key) {
            var spoofed = {
                "ro.product.model": "SM-G991B",
                "ro.product.brand": "samsung",
                "ro.product.device": "o1s",
                "ro.product.name": "o1sxx",
                "ro.build.display.id": "SP1A.210812.016.G991BXXSDBUIA5",
                "ro.build.version.release": "12",
                "ro.hardware": "exynos2100",
                "ro.product.board": "exynos2100",
                "ro.build.tags": "release-keys",
                "ro.build.type": "user",
                "ro.debuggable": "0",
                "ro.secure": "1",
                "init.svc.adbd": "stopped",
                // Nox-specific
                "ro.nox.ac_version": "",
                "nox.prop.version": "",
                "persist.nox.simulator_version": "",
                // BlueStacks-specific
                "ro.bluestacks.version": "",
                " ro.bluestacks.device": "",
                // MEmu-specific
                "ro.memu.device": "",
                "persist.memu.device": "",
            };
            if (key in spoofed) {
                console.log("[+] SystemProperties.get bypassed for: " + key);
                return spoofed[key];
            }
            return this.get(key);
        };
    } catch (e) {}

    // TelephonyManager - fake phone info
    try {
        var TelephonyManager = Java.use("android.telephony.TelephonyManager");
        TelephonyManager.getDeviceId.overload().implementation = function () {
            console.log("[+] TelephonyManager.getDeviceId bypassed");
            return "123456789012345";
        };
        TelephonyManager.getSubscriberId.overload().implementation = function () {
            console.log("[+] TelephonyManager.getSubscriberId bypassed");
            return "310260000000000";
        };
        TelephonyManager.getSimSerialNumber.overload().implementation = function () {
            console.log("[+] TelephonyManager.getSimSerialNumber bypassed");
            return "89012345678901234567";
        };
        TelephonyManager.getLine1Number.overload().implementation = function () {
            console.log("[+] TelephonyManager.getLine1Number bypassed");
            return "+15551234567";
        };
        TelephonyManager.getNetworkOperator.overload().implementation = function () {
            return "310260";
        };
        TelephonyManager.getNetworkOperatorName.overload().implementation = function () {
            return "T-Mobile";
        };
        TelephonyManager.getSimOperator.overload().implementation = function () {
            return "310260";
        };
        TelephonyManager.getSimOperatorName.overload().implementation = function () {
            return "T-Mobile";
        };
    } catch (e) {}

    // File checks - hide emulator files (Nox, BlueStacks, MEmu, AVD)
    try {
        var emulator_files = [
            // Generic emulator
            "/dev/socket/qemud",
            "/dev/qemu_pipe",
            "/system/lib/libc_malloc_debug_qemu.so",
            "/sys/qemu_trace",
            "/system/bin/qemu-props",
            "/dev/goldfish_pipe",
            // Nox Player
            "/system/bin/nox-prop",
            "/system/bin/nox-vbox-sf",
            "/system/lib/libnoxd.so",
            "/system/lib/libnoxspeedup.so",
            "/system/bin/nox-vbox-sf",
            "/system/lib/libmemuime.so",
            "/system/lib/libmemu_runtime.so",
            // BlueStacks
            "/system/bin/bstfolderd",
            "/system/lib/libbstfolder_jni.so",
            "/system/bin/bstfolderd",
            "/system/lib/libbstfolder_jni.so",
            // MEmu
            "/system/bin/memuime",
            "/system/lib/libmemuime_jni.so",
            "/system/bin/nemud",
            "/system/lib/libnemu_ime.so",
            // Generic
            "/system/bin/windroye",
            "/system/bin/genybaseband",
            "/system/bin/genybaseband-prop",
            "/system/lib/lib Juni.so",
            "/dev/socket/genyd",
        ];

        var File = Java.use("java.io.File");
        File.exists.implementation = function () {
            var path = this.getAbsolutePath();
            if (emulator_files.indexOf(path) !== -1) {
                console.log("[+] File.exists bypassed for emulator file: " + path);
                return false;
            }
            return this.exists();
        };
    } catch (e) {}

    // Settings.Secure - hide emulator indicators
    try {
        var Settings = Java.use("android.provider.Settings$Secure");
        Settings.getString.overload("android.content.ContentResolver", "java.lang.String").implementation = function (resolver, name) {
            if (name === "android_id") {
                console.log("[+] Settings.Secure.getString bypassed for android_id");
                return "abcdef1234567890";
            }
            return this.getString(resolver, name);
        };
    } catch (e) {}

    // PackageManager - hide emulator packages
    try {
        var PackageManager = Java.use("android.app.ApplicationPackageManager");
        var emulatorPackages = [
            "com.bstp.mapzone",
            "com.bluestacks.settings",
            "com.bluestacks.appmart",
            "com.bluestacks.searchapp",
            "com.bluestacks.ext.gp",
            "com.vphone.launcher",
            "com.vphone.helper",
            "com.memu.launcher",
            "com.memu.tools",
            "com.nox.app.manager",
            "com.nox.store",
            "com.bignox.app.storeHD",
            "com.bignox.app.secure",
            "me.weishu.exp",
            "com.bluestacks.s2p",
            "com.bluestacks.oem.x86sandbox.service",
        ];

        PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function (name, flags) {
            if (emulatorPackages.indexOf(name) !== -1) {
                console.log("[+] PackageManager.getPackageInfo bypassed for emulator package: " + name);
                throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new();
            }
            return this.getPackageInfo(name, flags);
        };
    } catch (e) {}

    // Check for /proc/cpuinfo (emulator indicators)
    try {
        var Runtime = Java.use("java.lang.Runtime");
        Runtime.exec.overload("[Ljava.lang.String;").implementation = function (cmds) {
            var cmd = cmds.join(" ");
            if (cmd.indexOf("cpuinfo") !== -1 || cmd.indexOf("qemu") !== -1 || cmd.indexOf("nox") !== -1) {
                console.log("[+] Runtime.exec blocked for emulator detection command: " + cmd);
                throw Java.use("java.io.IOException").$new("Cannot run program");
            }
            return this.exec(cmds);
        };
    } catch (e) {}

    // Network interfaces - hide emulator interfaces
    try {
        var NetworkInterface = Java.use("java.net.NetworkInterface");
        NetworkInterface.getByName.overload("java.lang.String").implementation = function (name) {
            var emulatorInterfaces = ["eth0", "wlan0", "noxy_router", "vboxnet0"];
            if (emulatorInterfaces.indexOf(name) !== -1) {
                console.log("[+] NetworkInterface.getByName bypassed for: " + name);
                return null;
            }
            return this.getByName(name);
        };
    } catch (e) {}

    console.log("[*] Emulator Detection Bypass completed (Nox, BlueStacks, MEmu, AVD)");
});
