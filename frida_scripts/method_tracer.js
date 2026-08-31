Java.perform(function () {
    console.log("[*] Method Tracer loaded");

    // Trace a specific class method
    window.traceMethod = function (className, methodName) {
        var clazz = Java.use(className);
        var overloads = clazz[methodName].overloads;

        overloads.forEach(function (overload) {
            overload.implementation = function () {
                var args = [];
                for (var i = 0; i < arguments.length; i++) {
                    args.push(JSON.stringify(arguments[i]));
                }
                console.log("[TRACE] " + className + "." + methodName + "(" + args.join(", ") + ")");
                var result = this[methodName].apply(this, arguments);
                console.log("[TRACE] " + className + "." + methodName + " -> " + JSON.stringify(result));
                return result;
            };
        });
        console.log("[+] Tracing " + className + "." + methodName);
    };

    // Trace all methods of a class
    window.traceClass = function (className) {
        var clazz = Java.use(className);
        var methods = clazz.class.getDeclaredMethods();

        methods.forEach(function (method) {
            var methodName = method.getName();
            try {
                window.traceMethod(className, methodName);
            } catch (e) {}
        });
        console.log("[+] Tracing all methods of " + className);
    };

    // Log all loaded classes
    window.logClasses = function (filter) {
        Java.enumerateLoadedClasses({
            onMatch: function (className) {
                if (!filter || className.includes(filter)) {
                    console.log("[CLASS] " + className);
                }
            },
            onComplete: function () {
                console.log("[DONE] Class enumeration complete");
            },
        });
    };

    console.log("[*] Tracer functions available:");
    console.log("    traceMethod('com.example.MyClass', 'myMethod')");
    console.log("    traceClass('com.example.MyClass')");
    console.log("    logClasses('com.example')");
});
