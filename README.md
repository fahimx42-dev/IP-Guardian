# IP Guardian

Free-first online IP intelligence dashboard with FastAPI backend and Android WebView wrapper.

## Deploy online
1. Push this repository to GitHub.
2. Open https://render.com and create a new Blueprint from this repository.
3. Render reads `render.yaml`. Deploy the `ip-guardian` web service.
4. Optional: add your own Shodan API key as `SHODAN_API_KEY` in the Render service environment.
5. Open the Render service URL. The dashboard and API are served from the same URL.

## Android
The Android app opens the hosted dashboard. Before building, replace `https://YOUR-RENDER-SERVICE.onrender.com`
in `android/app/src/main/java/com/ipguardian/app/MainActivity.java` with your actual Render URL.
Then run the GitHub Actions workflow and download the APK artifact.

## Notes
- Free hosting may sleep when idle and may have usage limits.
- Third-party IP/DNS/RDAP services have their own rate limits and privacy policies.
- Shodan requires a valid API key. Keep it in hosting environment secrets; never commit it to source.
- This app provides public IP intelligence. It does not perform stealth monitoring, unauthorized access, or port scanning.
