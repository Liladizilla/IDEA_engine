# Deployment

Backend: any container host with Postgres+pgvector and Redis (Render, Fly.io, a VPS). Run the API and the worker as two processes from the same image.
`uvicorn app.main:app --host 0.0.0.0 --port 8000` and `python -m app.workers.scheduler`.
Set `APP_ENV=production` and every variable in ENVIRONMENT.md. Put HTTPS in front.

Android
- Emulator to local backend: `http://10.0.2.2:8000`. Plain http needs `android:usesCleartextTraffic="true"` in `android/app/src/debug/AndroidManifest.xml` only. Release builds must use https.
- `tool/bootstrap.sh` adds the INTERNET permission for release builds.
- Build: `flutter build appbundle --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=https://api.yourdomain`
- Change the application id (`com.cyberzilla.idea_app` by default) in `android/app/build.gradle` before publishing.

Observability: add Sentry via `SENTRY_DSN`, and log collector errors, queue depth, provider usage and opportunity generation rate as structured logs.
