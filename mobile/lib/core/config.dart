/// Build-time configuration. Nothing secret belongs here: the app only knows where the API lives.
///
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000 --dart-define=USE_MOCK=false
///
/// 10.0.2.2 is the host machine as seen from the Android emulator.
class AppConfig {
  static const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');
  static const useMock = bool.fromEnvironment('USE_MOCK', defaultValue: true);
}
