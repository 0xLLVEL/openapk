Java.perform(function () {
    console.log("[*] Root Detection Bypass loaded");

    // File.exists - hide su binary
    var file_paths = [
        "/system/app/Superuser.apk",
        "/system/xbin/su",
        "/system/bin/su",
        "/sbin/su",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/system/sd/xbin/su",
        "/system/bin/failsafe/su",
        "/data/local/su",
        "/su/bin/su",
        "/system/app/SuperSU.apk",
        "/system/app/SuperSU",
        "/system/xbin/daemonsu",
        "/system/etc/init.d/99sudemo",
        "/cache/su",
        "/data/su",
        "/dev/su",
    ];

    try {
        var File = Java.use("java.io.File");
        File.exists.implementation = function () {
            var path = this.getAbsolutePath();
            if (file_paths.indexOf(path) !== -1) {
                console.log("[+] File.exists() bypassed for: " + path);
                return false;
            }
            return this.exists();
        };
    } catch (e) {}

    // Runtime.exec - block root commands
    try {
        var Runtime = Java.use("java.lang.Runtime");
        Runtime.exec.overload("java.lang.String").implementation = function (cmd) {
            if (cmd.indexOf("su") !== -1 || cmd.indexOf("which") !== -1) {
                console.log("[+] Runtime.exec bypassed for: " + cmd);
                throw Java.use("java.io.IOException").$new("Cannot run program");
            }
            return this.exec(cmd);
        };
    } catch (e) {}

    // Runtime.exec with array
    try {
        var Runtime = Java.use("java.lang.Runtime");
        Runtime.exec.overload("[Ljava.lang.String;").implementation = function (cmds) {
            var cmd = cmds.join(" ");
            if (cmd.indexOf("su") !== -1) {
                console.log("[+] Runtime.exec(array) bypassed for: " + cmd);
                throw Java.use("java.io.IOException").$new("Cannot run program");
            }
            return this.exec(cmds);
        };
    } catch (e) {}

    // Build.TAGS - hide test-keys
    try {
        var Build = Java.use("android.os.Build");
        Build.TAGS.value = "release-keys";
        console.log("[+] Build.TAGS set to release-keys");
    } catch (e) {}

    // PackageManager - hide root apps
    try {
        var PackageManager = Java.use("android.app.ApplicationPackageManager");
        PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function (name, flags) {
            var rootPackages = [
                "com.topjohnwu.magisk",
                "eu.chainfire.supersu",
                "com.koushikdutta.superuser",
                "com.thirdparty.superuser",
                "com.noshufou.android.su",
                "com.devadvance.rootcloak",
                "com.devadvance.rootcloakplus",
                "com.saurik.substrate",
            ];
            if (rootPackages.indexOf(name) !== -1) {
                console.log("[+] PackageManager.getPackageInfo bypassed for: " + name);
                throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new();
            }
            return this.getPackageInfo(name, flags);
        };
    } catch (e) {}

    // File.canRead - hide root dirs
    try {
        var File = Java.use("java.io.File");
        File.canRead.implementation = function () {
            var path = this.getAbsolutePath();
            if (path === "/su" || path === "/system/xbin/su" || path === "/system/bin/su") {
                console.log("[+] File.canRead bypassed for: " + path);
                return false;
            }
            return this.canRead();
        };
    } catch (e) {}

    // SystemProperties.get
    try {
        var SystemProperties = Java.use("android.os.SystemProperties");
        SystemProperties.get.overload("java.lang.String").implementation = function (key) {
            if (key === "ro.build.selinux" || key === "ro.debuggable") {
                console.log("[+] SystemProperties.get bypassed for: " + key);
                return "0";
            }
            return this.get(key);
        };
    } catch (e) {}

    console.log("[*] Root Detection Bypass completed");
});
