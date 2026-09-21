import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';
import '../../core/widgets/idea_logo.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final c = context.c;
    final s = context.s;

    return BundleView(
      builder: (context, bundle) {
        final opportunities = bundle.opportunities.take(2).toList();

        return ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.l, Gap.xl, Gap.xxl),
          children: [
            const IdeaLogo(size: 22),
            const SizedBox(height: Gap.xxl),
            Text(s.greeting(DateTime.now().hour), style: IdeaType.headline(c.text, size: 42)),
            const SizedBox(height: Gap.xs),
            Text(s.homePrompt, style: IdeaType.body(c.textMuted, size: 18)),
            const SizedBox(height: Gap.xl),
            IdeaButton(label: s.findAnIdea, onPressed: () => context.push('/scan')),
            const SizedBox(height: Gap.m),
            IdeaButton(label: s.exploreRadar, primary: false, onPressed: () => context.go('/radar')),
            const SizedBox(height: Gap.xxl),
            Row(
              children: [
                Expanded(child: Text(s.todaysOpportunities, style: IdeaType.headline(c.text, size: 24))),
                InkWell(
                  onTap: () => context.go('/discover'),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: Gap.xs),
                    child: Text(s.seeAll, style: IdeaType.body(c.accentText, size: 14, weight: FontWeight.w600)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: Gap.m),
            for (final opportunity in opportunities) ...[
              OpportunityCard(
                opportunity: opportunity,
                onTap: () => context.push('/opportunity/${opportunity.id}'),
              ),
            ],
          ],
        );
      },
    );
  }
}
