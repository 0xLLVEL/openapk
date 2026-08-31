Java.perform(function () {
    console.log("[*] SSL Pinning Bypass loaded");

    // TrustManagerImpl
    try {
        var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
        TrustManagerImpl.verifyChain.implementation = function () {
            console.log("[+] TrustManagerImpl.verifyChain bypassed");
            return arguments[0];
        };
    } catch (e) {}

    // TrustManagerImpl checkTrustedRecursive
    try {
        var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
        TrustManagerImpl.checkTrustedRecursive.implementation = function () {
            console.log("[+] TrustManagerImpl.checkTrustedRecursive bypassed");
            return arguments[0];
        };
    } catch (e) {}

    // OkHttp CertificatePinner
    try {
        var CertificatePinner = Java.use("okhttp3.CertificatePinner");
        CertificatePinner.check.overload("java.lang.String", "java.util.List").implementation = function () {
            console.log("[+] OkHttp3 CertificatePinner.check bypassed");
        };
    } catch (e) {}

    // OkHttp CertificatePinner (older versions)
    try {
        var CertificatePinner = Java.use("okhttp3.CertificatePinner");
        CertificatePinner.check.overload("java.lang.String", "java.util.List").implementation = function () {
            console.log("[+] OkHttp3 CertificatePinner.check (old) bypassed");
        };
    } catch (e) {}

    // HttpsURLConnection
    try {
        var HttpsURLConnection = Java.use("javax.net.ssl.HttpsURLConnection");
        HttpsURLConnection.setSSLSocketFactory.implementation = function () {
            console.log("[+] HttpsURLConnection.setSSLSocketFactory bypassed");
        };
    } catch (e) {}

    // SSLContext
    try {
        var SSLContext = Java.use("javax.net.ssl.SSLContext");
        SSLContext.init.overload("[Ljavax.net.ssl.KeyManager;", "[Ljavax.net.ssl.TrustManager;", "java.security.SecureRandom").implementation = function () {
            console.log("[+] SSLContext.init bypassed");
            this.init(arguments[0], [Java.use("javax.net.ssl.X509TrustManager").$new()], arguments[2]);
        };
    } catch (e) {}

    // Conscrypt SSLParametersImpl
    try {
        var SSLParametersImpl = Java.use("com.android.org.conscrypt.SSLParametersImpl");
        SSLParametersImpl.setEndpointIdentificationAlgorithm.implementation = function () {
            console.log("[+] Conscrypt SSLParametersImpl bypassed");
        };
    } catch (e) {}

    // WebViewClient onReceivedSslError
    try {
        var WebViewClient = Java.use("android.webkit.WebViewClient");
        WebViewClient.onReceivedSslError.implementation = function (view, handler, error) {
            console.log("[+] WebViewClient.onReceivedSslError bypassed");
            handler.proceed();
        };
    } catch (e) {}

    // Apache HTTP Client
    try {
        var AbstractVerifier = Java.use("org.apache.http.conn.ssl.AbstractVerifier");
        AbstractVerifier.verify.overload("java.lang.String", "[Ljava.lang.String;").implementation = function () {
            console.log("[+] Apache HTTP AbstractVerifier bypassed");
        };
    } catch (e) {}

    console.log("[*] SSL Pinning Bypass completed");
});
