import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/cards.dart';

class RadarScreen extends StatelessWidget {
  const RadarScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    return BundleView(
      builder: (context, b) => ListView(padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.l, Gap.xl, Gap.xxl), children: [
        Text(s.radarTitle, style: IdeaType.headline(c.text, size: 38)),
        const SizedBox(height: Gap.s),
        Text(s.radarIntro, style: IdeaType.body(c.textMuted, size: 15)),
        const SizedBox(height: Gap.xl),
        RadarFeed(signals: b.radar, onOpen: (id) => context.push('/opportunity/$id')),
        for (final i in b.insufficient) InsufficientSignalCard(scope: i),
      ]),
    );
  }
}
