import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';
import '../../core/widgets/inputs.dart';
import '../../domain/models.dart';

class DiscoverScreen extends StatefulWidget {
  const DiscoverScreen({super.key});
  @override
  State<DiscoverScreen> createState() => _DiscoverScreenState();
}

class _DiscoverScreenState extends State<DiscoverScreen> {
  final _query = TextEditingController();
  DiscoverFilter _filter = const DiscoverFilter();

  @override
  void dispose() {
    _query.dispose();
    super.dispose();
  }

  /// Client-side text match for the skeleton. Real semantic search is GET /v1/search backed by pgvector.
  List<Opportunity> _results(Bundle b) {
    final q = _query.text.trim().toLowerCase();
    return b.opportunities.where((o) {
      if (o.score < _filter.minScore) return false;
      if (_filter.source != null && !o.stats.sources.containsKey(_filter.source)) return false;
      return q.isEmpty || '${o.title} ${o.coreQuestion} ${o.audience}'.toLowerCase().contains(q);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    return BundleView(
      builder: (context, b) {
        final results = _results(b);
        final q = _query.text.trim().toLowerCase();
        final insufficient = q.isEmpty ? <InsufficientScope>[] : b.insufficient.where((i) => i.scope.toLowerCase().contains(q)).toList();
        return ListView(padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.l, Gap.xl, Gap.xxl), children: [
          Text(s.navDiscover, style: IdeaType.headline(c.text, size: 38)),
          const SizedBox(height: Gap.l),
          IdeaSearchField(
            controller: _query,
            onChanged: (_) => setState(() {}),
            filtersActive: _filter.active,
            onFilter: () async {
              final next = await showFilterSheet(context, _filter);
              if (next != null) setState(() => _filter = next);
            },
          ),
          if (_query.text.isEmpty) ...[
            SectionTitle(s.categories),
            Wrap(spacing: Gap.s, runSpacing: Gap.s, children: [
              for (final cat in b.categories)
                InkWell(
                  onTap: () => setState(() => _query.text = cat),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: Gap.m, vertical: Gap.s),
                    decoration: BoxDecoration(border: Border.all(color: c.line), borderRadius: kBorder),
                    child: Text(cat, style: IdeaType.body(c.text, size: 14)),
                  ),
                ),
            ]),
          ],
          const SizedBox(height: Gap.l),
          for (final i in insufficient) Padding(padding: const EdgeInsets.only(bottom: Gap.l), child: InsufficientSignalCard(scope: i)),
          if (results.isEmpty && insufficient.isEmpty) Padding(padding: const EdgeInsets.only(top: Gap.xl), child: Text(s.noResults, style: IdeaType.body(c.textMuted, size: 15))),
          for (final o in results) OpportunityCard(opportunity: o, onTap: () => context.push('/opportunity/${o.id}')),
        ]);
      },
    );
  }
}
