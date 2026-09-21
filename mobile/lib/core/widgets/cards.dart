import 'package:flutter/material.dart';

import '../../domain/models.dart';
import '../format.dart';
import '../icons/idea_icons.dart';
import '../l10n/strings.dart';
import '../theme/theme.dart';
import '../theme/tokens.dart';
import 'basics.dart';
import 'score.dart';
import 'trend_graph.dart';

/// A ruled list entry, not a card: the score leads because it is what the row is ranked by.
class OpportunityCard extends StatelessWidget {
  const OpportunityCard({super.key, required this.opportunity, required this.onTap});
  final Opportunity opportunity;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final o = opportunity;
    final growth = o.stats.growth7d;
    final growthPositive = growth > 0.05;

    return InkWell(
      onTap: onTap,
      borderRadius: kBorder,
      child: Container(
        width: double.infinity,
        margin: const EdgeInsets.only(bottom: Gap.l),
        padding: const EdgeInsets.all(Gap.l),
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: kBorder,
          border: Border.all(color: c.line),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 64,
              child: Text(
                '${o.score}',
                style: IdeaType.numeral(growthPositive ? c.accentText : c.text, 48),
              ),
            ),
            const SizedBox(width: Gap.l),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    o.title,
                    style: IdeaType.body(c.text, size: 17, weight: FontWeight.w600, height: 1.25),
                  ),
                  const SizedBox(height: Gap.s),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          '${o.stats.relatedQuestions} questions in ${o.stats.communities} communities',
                          style: IdeaType.body(c.textMuted, size: 13),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: Gap.xs),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      IdeaIcon(
                        growthPositive ? IdeaIcons.up : growth < -0.05 ? IdeaIcons.down : IdeaIcons.flat,
                        size: 12,
                        color: growthPositive ? c.accentText : c.textMuted,
                      ),
                      const SizedBox(width: Gap.xs),
                      Text(
                        '${formatPercent(growth)} in 7 days',
                        style: IdeaType.body(growthPositive ? c.accentText : c.textMuted, size: 13, weight: FontWeight.w600),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// A row on the radar's time rail. Filled marker: linked to a scored opportunity. Hollow: still gathering evidence.
class SignalCard extends StatelessWidget {
  const SignalCard({super.key, required this.signal, required this.onTap});
  final RadarSignal signal;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = signal;
    final linked = s.opportunityId != null;
    return InkWell(
      onTap: onTap,
      child: IntrinsicHeight(
        child: Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          SizedBox(
            width: 28,
            child: Column(children: [
              const SizedBox(height: 22),
              Container(width: 9, height: 9, decoration: BoxDecoration(color: linked ? c.filament : Colors.transparent, border: Border.all(color: linked ? c.filament : c.textMuted, width: 1.5))),
              Expanded(child: Container(width: 1, color: c.line)),
            ]),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: Gap.xl, top: Gap.m),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(formatAgo(s.minutesAgo), style: IdeaType.body(c.textMuted, size: 12)),
                const SizedBox(height: 2),
                Text(s.question, style: IdeaType.body(c.text, size: 16, weight: FontWeight.w500, height: 1.35)),
                const SizedBox(height: Gap.s),
                Wrap(spacing: Gap.s, runSpacing: Gap.xs, crossAxisAlignment: WrapCrossAlignment.center, children: [
                  for (final src in s.sources) SourceChip(sourceLabel(src)),
                  Text('${formatPercent(s.momentum)} momentum', style: IdeaType.body(c.textMuted, size: 13)),
                ]),
                const SizedBox(height: Gap.xs),
                Text(linked ? 'Answer gap: ${levelLabel(s.answerGap)}' : context.s.gatheringEvidence, style: IdeaType.body(linked ? c.accentText : c.textMuted, size: 13, weight: FontWeight.w500)),
              ]),
            ),
          ),
        ]),
      ),
    );
  }
}

class RadarFeed extends StatelessWidget {
  const RadarFeed({super.key, required this.signals, required this.onOpen});
  final List<RadarSignal> signals;
  final void Function(String opportunityId) onOpen;

  @override
  Widget build(BuildContext context) => Column(children: [
        for (final s in signals) SignalCard(signal: s, onTap: s.opportunityId == null ? null : () => onOpen(s.opportunityId!)),
      ]);
}

class QuestionClusterCard extends StatelessWidget {
  const QuestionClusterCard({super.key, required this.question, required this.count, this.examples = const []});
  final String question;
  final int count;
  final List<String> examples;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(question, style: IdeaType.headline(c.text, size: 26)),
      const SizedBox(height: Gap.s),
      Text('Representative of $count related questions', style: IdeaType.body(c.textMuted, size: 13)),
      for (final e in examples) ...[
        const SizedBox(height: Gap.m),
        Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Padding(padding: const EdgeInsets.only(top: 8, right: Gap.m), child: Container(width: 4, height: 4, color: c.textMuted)),
          Expanded(child: Text(e, style: IdeaType.body(c.text, size: 15))),
        ]),
      ],
    ]);
  }
}

class IdeaCard extends StatelessWidget {
  const IdeaCard({super.key, required this.idea});
  final IdeaConcept idea;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: Gap.m),
      padding: const EdgeInsets.all(Gap.l),
      decoration: BoxDecoration(border: Border.all(color: c.line), borderRadius: kBorder),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(idea.title, style: IdeaType.body(c.text, size: 17, weight: FontWeight.w600, height: 1.3)),
        const SizedBox(height: Gap.s),
        Text(idea.hook, style: IdeaType.body(c.textMuted, size: 15)),
        const SizedBox(height: Gap.m),
        Wrap(spacing: Gap.s, runSpacing: Gap.s, children: [SourceChip(formatLabel(idea.format)), SourceChip('Difficulty: ${idea.difficulty}')]),
        const SizedBox(height: Gap.m),
        Text.rich(TextSpan(children: [
          TextSpan(text: '${context.s.whyNow}  ', style: IdeaType.body(c.text, size: 13, weight: FontWeight.w600)),
          TextSpan(text: idea.whyNow, style: IdeaType.body(c.textMuted, size: 13)),
        ])),
      ]),
    );
  }
}

class NicheCard extends StatelessWidget {
  const NicheCard({super.key, required this.niche, this.onTap});
  final Niche niche;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return InkWell(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(Gap.l),
        decoration: BoxDecoration(border: Border.all(color: c.line), borderRadius: kBorder),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(niche.title, style: IdeaType.headline(c.text, size: 24)),
          const SizedBox(height: Gap.xs),
          Text('For ${niche.audience.toLowerCase()}', style: IdeaType.body(c.textMuted, size: 14)),
          const SizedBox(height: Gap.m),
          for (final w in niche.why)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Padding(padding: const EdgeInsets.only(top: 8, right: Gap.m), child: Container(width: 4, height: 4, color: c.filament)),
                Expanded(child: Text(w, style: IdeaType.body(c.text, size: 14))),
              ]),
            ),
        ]),
      ),
    );
  }
}

class CreatorProfileCard extends StatelessWidget {
  const CreatorProfileCard({super.key, required this.profile});
  final CreatorProfile profile;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    Widget row(String k, String v) => Padding(
          padding: const EdgeInsets.symmetric(vertical: Gap.s),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            SizedBox(width: 110, child: Text(k, style: IdeaType.body(c.textMuted, size: 14))),
            Expanded(child: Text(v.isEmpty ? 'Not set' : v, style: IdeaType.body(v.isEmpty ? c.textMuted : c.text, size: 15, weight: FontWeight.w500))),
          ]),
        );
    return Column(children: [
      row('Creates', profile.platforms.join(', ')),
      const Hairline(),
      row('Niche', profile.hasNiche == false ? 'Still looking' : profile.niche),
      const Hairline(),
      row('Audience', profile.audience),
      const Hairline(),
      row('Notify', profile.notify),
    ]);
  }
}

class ResearchSection extends StatelessWidget {
  const ResearchSection({super.key, required this.title, required this.child, this.topGap = Gap.xxl});
  final String title;
  final Widget child;
  final double topGap;

  @override
  Widget build(BuildContext context) => Padding(
        padding: EdgeInsets.only(top: topGap),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: IdeaType.headline(context.c.text, size: 22)),
          const SizedBox(height: Gap.m),
          child,
        ]),
      );
}

class InsufficientSignalCard extends StatelessWidget {
  const InsufficientSignalCard({super.key, required this.scope});
  final InsufficientScope scope;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Gap.l),
      decoration: BoxDecoration(border: Border.all(color: c.line), borderRadius: kBorder),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('${s.insufficientTitle}: ${scope.scope}', style: IdeaType.body(c.text, size: 16, weight: FontWeight.w600)),
        const SizedBox(height: Gap.s),
        Text(s.insufficientBody(scope.scope, scope.questionsFound, scope.questionsNeeded, scope.sourcesFound, scope.sourcesNeeded), style: IdeaType.body(c.textMuted, size: 14)),
        const SizedBox(height: Gap.m),
        SegmentBar(value: scope.questionsFound / scope.questionsNeeded * 100, muted: true, height: 6),
      ]),
    );
  }
}

class AIStatusIndicator extends StatelessWidget {
  const AIStatusIndicator({super.key, required this.provider, required this.connected});
  final String provider;
  final bool connected;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
      Text(context.s.aiProvider, style: IdeaType.body(c.text, size: 14, weight: FontWeight.w500)),
      Text(connected ? provider : 'Not connected', style: IdeaType.body(connected ? c.text : c.textMuted, size: 14)),
    ]);
  }
}

class TrendRow extends StatelessWidget {
  const TrendRow({super.key, required this.opportunity, required this.onTap});
  final Opportunity opportunity;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: Gap.m),
        child: Row(children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(opportunity.title, maxLines: 2, overflow: TextOverflow.ellipsis, style: IdeaType.body(c.text, size: 15, weight: FontWeight.w500, height: 1.3)),
              const SizedBox(height: 2),
              Text(velocityLabel(opportunity.stats.velocity), style: IdeaType.body(c.textMuted, size: 13)),
            ]),
          ),
          const SizedBox(width: Gap.l),
          SizedBox(width: 96, child: TrendGraph(values: opportunity.trend, height: 32)),
        ]),
      ),
    );
  }
}
