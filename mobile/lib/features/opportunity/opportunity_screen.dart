import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/format.dart';
import '../../core/icons/idea_icons.dart';
import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';
import '../../core/widgets/inputs.dart';
import '../../core/widgets/score.dart';
import '../../core/widgets/trend_graph.dart';
import '../../data/providers.dart';
import '../../domain/models.dart';

class OpportunityScreen extends ConsumerWidget {
  const OpportunityScreen({super.key, required this.id});
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final c = context.c;
    final s = context.s;
    final saved = ref.watch(savedProvider).contains(id);
    return Scaffold(
      body: SafeArea(
        child: BundleView(
          builder: (context, b) {
            final o = b.opportunity(id);
            if (o == null) {
              return Center(child: Padding(padding: const EdgeInsets.all(Gap.xl), child: Text('That opportunity is no longer on the radar. It may have expired.', textAlign: TextAlign.center, style: IdeaType.body(c.text, size: 16))));
            }
            return Column(children: [
              Expanded(child: _Body(o: o, saved: saved, onSave: () => ref.read(savedProvider.notifier).toggle(id))),
              Container(
                padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.m, Gap.xl, Gap.m),
                decoration: BoxDecoration(color: c.ground, border: Border(top: BorderSide(color: c.line))),
                child: Row(children: [
                  Expanded(child: IdeaButton(label: s.research, primary: false, onPressed: () => context.push('/research/$id'))),
                  const SizedBox(width: Gap.m),
                  Expanded(flex: 2, child: IdeaButton(label: s.createContent, icon: IdeaIcons.create, onPressed: () => _createSheet(context))),
                ]),
              ),
            ]);
          },
        ),
      ),
    );
  }

  void _createSheet(BuildContext context) {
    showModalBottomSheet<void>(context: context, isScrollControlled: true, builder: (_) => const _CreateSheet());
  }
}

class _Body extends StatelessWidget {
  const _Body({required this.o, required this.saved, required this.onSave});
  final Opportunity o;
  final bool saved;
  final VoidCallback onSave;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    final st = o.stats;
    final sourceLine = st.sources.entries.map((e) => '${sourceLabel(e.key)} ${e.value}').join(', ');
    return ListView(padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.s, Gap.xl, Gap.xxl), children: [
      Row(children: [
        InkWell(onTap: () => context.canPop() ? context.pop() : context.go('/home'), child: const Padding(padding: EdgeInsets.symmetric(vertical: Gap.s), child: IdeaIcon(IdeaIcons.back))),
        const Spacer(),
        InkWell(onTap: onSave, child: Padding(padding: const EdgeInsets.all(Gap.s), child: IdeaIcon(IdeaIcons.saved, filled: saved, color: saved ? c.accentText : c.text))),
      ]),
      const SizedBox(height: Gap.m),
      Text(o.title, style: IdeaType.headline(c.text, size: 34)),
      const SizedBox(height: Gap.xl),
      OpportunityScore(score: o.score),
      const SizedBox(height: Gap.m),
      Text('Confidence ${o.confidence}. ${st.relatedQuestions} questions from ${st.sources.length} sources. ${s.scoreCaveat}', style: IdeaType.body(c.textMuted, size: 13)),
      const SizedBox(height: Gap.xl),
      FactorBars(factors: o.factors),
      ResearchSection(title: s.whyDetected, child: Text(o.whyDetected, style: IdeaType.body(c.text, size: 16))),
      ResearchSection(title: s.theQuestion, child: QuestionClusterCard(question: o.coreQuestion, count: st.relatedQuestions)),
      ResearchSection(
        title: s.whoIsAsking,
        child: Text('${o.audience}. ${st.askers} different people asked, across ${st.communities} communities.', style: IdeaType.body(c.text, size: 16)),
      ),
      ResearchSection(title: s.signalEvidence, child: Column(children: [for (final e in o.evidence) _EvidenceRow(e: e)])),
      ResearchSection(
        title: s.trend,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          TrendGraph(values: o.trend, labels: true, startLabel: s.daysAgoLabel, endLabel: s.today),
          const SizedBox(height: Gap.m),
          Text('${velocityLabel(st.velocity)}. ${formatPercent(st.growth7d)} this week compared with last week.', style: IdeaType.body(c.text, size: 15)),
        ]),
      ),
      ResearchSection(
        title: s.competition,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${levelLabel(o.competitionLevel)}. ${o.creators} creators cover the general topic.', style: IdeaType.body(c.text, size: 16, weight: FontWeight.w500)),
          const SizedBox(height: Gap.xs),
          Text(o.competitionNote, style: IdeaType.body(c.textMuted, size: 15)),
        ]),
      ),
      ResearchSection(
        title: s.answerGap,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(levelLabel(o.answerGapLevel), style: IdeaType.body(c.accentText, size: 16, weight: FontWeight.w600)),
          const SizedBox(height: Gap.xs),
          Text(o.answerGapNote, style: IdeaType.body(c.textMuted, size: 15)),
        ]),
      ),
      ResearchSection(
        title: s.relatedQuestions,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          for (final q in o.relatedQuestions) Padding(padding: const EdgeInsets.only(bottom: Gap.m), child: Text(q, style: IdeaType.body(c.text, size: 15))),
        ]),
      ),
      ResearchSection(title: s.contentAngles, child: Column(children: [for (final i in o.ideas) IdeaCard(idea: i)])),
      ResearchSection(title: s.sources, child: Text(sourceLine, style: IdeaType.body(c.text, size: 15))),
    ]);
  }
}

class _EvidenceRow extends StatelessWidget {
  const _EvidenceRow({required this.e});
  final Evidence e;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: Gap.l),
      decoration: BoxDecoration(border: Border(top: BorderSide(color: c.line))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [SourceChip(sourceLabel(e.source)), const SizedBox(width: Gap.s), Expanded(child: Text(e.where, style: IdeaType.body(c.textMuted, size: 13)))]),
        const SizedBox(height: Gap.s),
        Text(e.excerpt, style: IdeaType.body(c.text, size: 16, height: 1.4)),
        const SizedBox(height: Gap.s),
        Row(children: [
          Expanded(child: Text('${e.engagement}. ${e.daysAgo} days ago', style: IdeaType.body(c.textMuted, size: 13))),
          if (e.isSample) Text(s.sampleSource, style: IdeaType.body(c.textMuted, size: 12)) else InkWell(onTap: () {}, child: Row(children: [Text(s.openSource, style: IdeaType.body(c.accentText, size: 13, weight: FontWeight.w600)), const SizedBox(width: 4), IdeaIcon(IdeaIcons.external, size: 16, color: c.accentText)])),
        ]),
      ]),
    );
  }
}

class _CreateSheet extends StatefulWidget {
  const _CreateSheet();
  @override
  State<_CreateSheet> createState() => _CreateSheetState();
}

class _CreateSheetState extends State<_CreateSheet> {
  String? _format;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(Gap.xl),
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(s.chooseFormat, style: IdeaType.headline(c.text, size: 26)),
          const SizedBox(height: Gap.m),
          Flexible(child: SingleChildScrollView(child: Column(children: [for (final f in contentFormats) ChoiceRow(label: formatLabel(f), selected: _format == f, onTap: () => setState(() => _format = f))]))),
          const SizedBox(height: Gap.l),
          Text(s.generationNotConnected, style: IdeaType.body(c.textMuted, size: 13)),
          const SizedBox(height: Gap.m),
          IdeaButton(label: s.createContent, onPressed: null),
        ]),
      ),
    );
  }
}
