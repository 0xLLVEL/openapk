Java.perform(function () {
    console.log("[*] Common Bypasses loaded - SSL + Root + Emulator + Anti-Debug");

    // ========== SSL PINNING ==========
    try {
        var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
        TrustManagerImpl.verifyChain.implementation = function () {
            return arguments[0];
        };
    } catch (e) {}

    try {
        var CertificatePinner = Java.use("okhttp3.CertificatePinner");
        CertificatePinner.check.implementation = function () {};
    } catch (e) {}

    // ========== ROOT DETECTION ==========
    try {
        var File = Java.use("java.io.File");
        var root_paths = [
            "/system/app/Superuser.apk", "/system/xbin/su", "/system/bin/su",
            "/sbin/su", "/system/app/SuperSU.apk", "/su/bin/su",
        ];
        File.exists.implementation = function () {
            if (root_paths.indexOf(this.getAbsolutePath()) !== -1) return false;
            return this.exists();
        };
    } catch (e) {}

    try {
        var Build = Java.use("android.os.Build");
        Build.TAGS.value = "release-keys";
    } catch (e) {}

    // ========== EMULATOR DETECTION ==========
    try {
        var Build = Java.use("android.os.Build");
        Build.MODEL.value = "Samsung Galaxy S21";
        Build.MANUFACTURER.value = "samsung";
        Build.FINGERPRINT.value = "samsung/o1sxx/o1s:12/SP1A.210812.016:user/release-keys";
    } catch (e) {}

    try {
        var emulator_files = [
            "/dev/socket/qemud", "/dev/qemu_pipe",
            "/system/lib/libc_malloc_debug_qemu.so", "/dev/goldfish_pipe",
        ];
        var File = Java.use("java.io.File");
        File.exists.implementation = function () {
            if (emulator_files.indexOf(this.getAbsolutePath()) !== -1) return false;
            return this.exists();
        };
    } catch (e) {}

    // ========== ANTI-DEBUG ==========
    try {
        var Debug = Java.use("android.os.Debug");
        Debug.isDebuggerConnected.implementation = function () {
            return false;
        };
    } catch (e) {}

    console.log("[*] All common bypasses applied");
});
