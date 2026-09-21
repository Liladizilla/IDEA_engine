import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/idea_logo.dart';
import '../../data/providers.dart';

/// The one orchestrated motion in the app: the filament lights.
class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});
  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _lit = AnimationController(vsync: this, duration: const Duration(milliseconds: 900));

  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(milliseconds: 350), () {
      if (mounted) _lit.forward();
    });
    _leave();
  }

  Future<void> _leave() async {
    await Future.delayed(const Duration(milliseconds: 1900));
    while (mounted && !ref.read(profileLoadedProvider)) {
      await Future.delayed(const Duration(milliseconds: 50));
    }
    if (!mounted) return;
    context.go(ref.read(profileProvider).done ? '/home' : '/onboarding');
  }

  @override
  void dispose() {
    _lit.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Scaffold(
      body: Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          AnimatedBuilder(animation: _lit, builder: (_, __) => BulbMark(size: 112, lit: Curves.easeOut.transform(_lit.value))),
          const SizedBox(height: Gap.l),
          Text('IDEA', style: IdeaType.headline(c.text, size: 44).copyWith(letterSpacing: 6)),
          const SizedBox(height: Gap.s),
          Text(context.s.tagline, style: IdeaType.body(c.textMuted, size: 16)),
        ]),
      ),
    );
  }
}
