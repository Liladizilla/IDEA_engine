import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router.dart';
import 'core/theme/theme.dart';
import 'core/theme/tokens.dart';

class IdeaApp extends ConsumerWidget {
  const IdeaApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'IDEA',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(IdeaColors.dark, Brightness.dark),
      darkTheme: buildTheme(IdeaColors.dark, Brightness.dark),
      themeMode: ThemeMode.dark,
      routerConfig: ref.watch(routerProvider),
    );
  }
}
