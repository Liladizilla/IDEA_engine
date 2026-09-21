import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';
import '../../data/providers.dart';

class SavedScreen extends ConsumerWidget {
  const SavedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final c = context.c;
    final s = context.s;
    final saved = ref.watch(savedProvider);
    return BundleView(
      builder: (context, b) {
        final items = b.opportunities.where((o) => saved.contains(o.id)).toList();
        return ListView(padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.l, Gap.xl, Gap.xxl), children: [
          Text(s.navSaved, style: IdeaType.headline(c.text, size: 38)),
          const SizedBox(height: Gap.l),
          if (items.isEmpty) ...[
            const SizedBox(height: Gap.xl),
            Text(s.savedEmptyTitle, style: IdeaType.headline(c.text, size: 24)),
            const SizedBox(height: Gap.s),
            Text(s.savedEmptyBody, style: IdeaType.body(c.textMuted, size: 15)),
            const SizedBox(height: Gap.xl),
            IdeaButton(label: s.findAnIdea, expand: false, onPressed: () => context.push('/scan')),
          ],
          for (final o in items) OpportunityCard(opportunity: o, onTap: () => context.push('/opportunity/${o.id}')),
        ]);
      },
    );
  }
}
