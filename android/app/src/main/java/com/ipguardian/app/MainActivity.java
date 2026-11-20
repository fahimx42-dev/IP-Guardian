package com.ipguardian.app;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.widget.Toast;
import android.webkit.WebResourceRequest;

public class MainActivity extends Activity {
    private static final String DASHBOARD_URL = "https://YOUR-RENDER-SERVICE.onrender.com";
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        WebView web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient());
        web.setWebChromeClient(new WebChromeClient());
        setContentView(web);
        if (DASHBOARD_URL.contains("YOUR-RENDER-SERVICE")) {
            Toast.makeText(this, "Set your Render URL in MainActivity.java before building.", Toast.LENGTH_LONG).show();
        }
        web.loadUrl(DASHBOARD_URL);
    }
}
