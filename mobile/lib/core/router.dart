import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/discover/discover_screen.dart';
import '../features/home/home_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/opportunity/opportunity_screen.dart';
import '../features/opportunity/research_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/radar/radar_screen.dart';
import '../features/saved/saved_screen.dart';
import '../features/scan/scan_screen.dart';
import '../features/splash/splash_screen.dart';
import 'shell.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(path: '/splash', builder: (_, __) => const SplashScreen()),
      GoRoute(path: '/onboarding', builder: (_, __) => const OnboardingScreen()),
      GoRoute(path: '/scan', builder: (_, __) => const ScanScreen()),
      GoRoute(path: '/opportunity/:id', builder: (_, s) => OpportunityScreen(id: s.pathParameters['id']!)),
      GoRoute(path: '/research/:id', builder: (_, s) => ResearchScreen(id: s.pathParameters['id']!)),
      StatefulShellRoute.indexedStack(
        builder: (_, __, shell) => Shell(shell: shell),
        branches: [
          StatefulShellBranch(routes: [GoRoute(path: '/home', builder: (_, __) => const HomeScreen())]),
          StatefulShellBranch(routes: [GoRoute(path: '/discover', builder: (_, __) => const DiscoverScreen())]),
          StatefulShellBranch(routes: [GoRoute(path: '/radar', builder: (_, __) => const RadarScreen())]),
          StatefulShellBranch(routes: [GoRoute(path: '/saved', builder: (_, __) => const SavedScreen())]),
          StatefulShellBranch(routes: [GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen())]),
        ],
      ),
    ],
  );
});
