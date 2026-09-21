import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config.dart';
import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';
import '../../core/widgets/score.dart';
import '../../data/providers.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final c = context.c;
    final s = context.s;
    final profile = ref.watch(profileProvider);
    return ListView(padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.l, Gap.xl, Gap.xxl), children: [
      Text(s.navProfile, style: IdeaType.headline(c.text, size: 38)),
      SectionTitle(s.creatorProfile),
      CreatorProfileCard(profile: profile),
      SectionTitle(s.usage),
      // Wire to GET /v1/me/usage once auth exists. The numbers here are placeholders in mock mode.
      const UsageMeter(used: 6, limit: 20),
      const SizedBox(height: Gap.l),
      const AIStatusIndicator(provider: 'Hugging Face', connected: !AppConfig.useMock),
      const SizedBox(height: Gap.m),
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Text(s.dataMode, style: IdeaType.body(c.text, size: 14, weight: FontWeight.w500)),
        Text(AppConfig.useMock ? s.sampleData : 'Live', style: IdeaType.body(c.textMuted, size: 14)),
      ]),
    ]);
  }
}
