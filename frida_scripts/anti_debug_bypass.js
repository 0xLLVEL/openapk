Java.perform(function () {
    console.log("[*] Anti-Debug Bypass loaded");

    // Debug.isDebuggerConnected
    try {
        var Debug = Java.use("android.os.Debug");
        Debug.isDebuggerConnected.implementation = function () {
            console.log("[+] Debug.isDebuggerConnected bypassed");
            return false;
        };
    } catch (e) {}

    // Debug.waitingForDebugger
    try {
        var Debug = Java.use("android.os.Debug");
        Debug.waitingForDebugger.implementation = function () {
            console.log("[+] Debug.waitingForDebugger bypassed");
            return false;
        };
    } catch (e) {}

    // Thread.isDebugging
    try {
        var Thread = Java.use("java.lang.Thread");
        Thread.isInterrupted.implementation = function () {
            return false;
        };
    } catch (e) {}

    // ptrace - prevent debugger attachment
    try {
        var ptrace = Module.findExportByName(null, "ptrace");
        if (ptrace) {
            Interceptor.attach(ptrace, {
                onEnter: function (args) {
                    var request = args[0].toInt32();
                    if (request === 0) { // PTRACE_TRACEME
                        console.log("[+] ptrace(PTRACE_TRACEME) intercepted");
                        args[0] = ptr(0);
                    }
                },
                onLeave: function (retval) {},
            });
        }
    } catch (e) {}

    // TracerPid check
    try {
        var File = Java.use("java.io.File");
        File.exists.implementation = function () {
            var path = this.getAbsolutePath();
            if (path === "/proc/self/status") {
                console.log("[+] /proc/status check intercepted");
                return false;
            }
            return this.exists();
        };
    } catch (e) {}

    // android.os.Debug(Java level)
    try {
        var Debug = Java.use("android.os.Debug");
        Debug.isDebuggerConnected.implementation = function () {
            console.log("[+] Debug.isDebuggerConnected (Java) bypassed");
            return false;
        };
    } catch (e) {}

    // Frida detection - hide frida agent
    try {
        var Runtime = Java.use("java.lang.Runtime");
        Runtime.exec.overload("java.lang.String").implementation = function (cmd) {
            if (cmd.indexOf("frida") !== -1 || cmd.indexOf("xposed") !== -1) {
                console.log("[+] Frida/Xposed detection blocked: " + cmd);
                throw Java.use("java.io.IOException").$new("Command not found");
            }
            return this.exec(cmd);
        };
    } catch (e) {}

    // Process class checks
    try {
        var Process = Java.use("android.os.Process");
        Process.killProcess.implementation = function (pid) {
            if (pid === Process.myPid()) {
                console.log("[+] Process.killProcess(self) blocked");
                return;
            }
            this.killProcess(pid);
        };
    } catch (e) {}

    console.log("[*] Anti-Debug Bypass completed");
});
