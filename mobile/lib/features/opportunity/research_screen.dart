import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/format.dart';
import '../../core/icons/idea_icons.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';

/// Research brief (spec section 30). Sections fill from evidence already collected; the rest say plainly
/// that they need a research run instead of pretending. Every externally derived claim keeps its source.
class ResearchScreen extends StatelessWidget {
  const ResearchScreen({super.key, required this.id});
  final String id;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Scaffold(
      body: SafeArea(
        child: BundleView(
          builder: (context, b) {
            final o = b.opportunity(id);
            if (o == null) return const SizedBox.shrink();
            Widget note(String t) => Text(t, style: IdeaType.body(c.textMuted, size: 15));
            Widget text(String t) => Text(t, style: IdeaType.body(c.text, size: 16));
            const pending = 'Needs a research run.';
            return ListView(padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.s, Gap.xl, Gap.xxl), children: [
              Align(alignment: Alignment.centerLeft, child: InkWell(onTap: () => context.pop(), child: Padding(padding: const EdgeInsets.symmetric(vertical: Gap.s), child: const IdeaIcon(IdeaIcons.back)))),
              Text('Research brief', style: IdeaType.headline(c.text, size: 34)),
              const SizedBox(height: Gap.xs),
              Text(o.title, style: IdeaType.body(c.textMuted, size: 15)),
              ResearchSection(title: 'Problem', child: text(o.coreQuestion)),
              ResearchSection(title: 'Audience', child: text(o.audience)),
              ResearchSection(title: 'Existing solutions', child: text(o.competitionNote)),
              ResearchSection(title: 'Missing information', child: text(o.answerGapNote)),
              ResearchSection(title: 'Common misconceptions', child: note(pending)),
              ResearchSection(title: 'Conflicting opinions', child: note(pending)),
              ResearchSection(title: 'Potential angles', child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [for (final i in o.ideas) Padding(padding: const EdgeInsets.only(bottom: Gap.s), child: text(i.title))])),
              ResearchSection(title: 'Sources', child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [for (final e in o.evidence) Padding(padding: const EdgeInsets.only(bottom: Gap.s), child: note('${sourceLabel(e.source)}, ${e.where}'))])),
              const SizedBox(height: Gap.xl),
              const IdeaButton(label: 'Run deep research', onPressed: null), // TODO: POST /v1/research/{id}
            ]);
          },
        ),
      ),
    );
  }
}
