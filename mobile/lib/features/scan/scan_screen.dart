import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/icons/idea_icons.dart';
import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/async_view.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/cards.dart';
import '../../core/widgets/idea_logo.dart';

const _stages = [
  'Collecting public posts and comments',
  'Pulling out the questions',
  'Grouping similar questions',
  'Checking which answers already exist',
  'Scoring the evidence',
];

/// The first-run proof (spec section 69). The stage list is honest: it names steps, never invents counts.
/// With the live backend, replace the timer with polling the scan job's real stage.
class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});
  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  int _done = 0;

  @override
  void initState() {
    super.initState();
    _tick();
  }

  Future<void> _tick() async {
    for (var i = 1; i <= _stages.length; i++) {
      await Future.delayed(const Duration(milliseconds: 650));
      if (!mounted) return;
      setState(() => _done = i);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    final finished = _done >= _stages.length;
    return Scaffold(
      body: SafeArea(
        child: BundleView(
          builder: (context, b) {
            final top = b.opportunities.take(3).toList();
            return ListView(padding: const EdgeInsets.all(Gap.xl), children: [
              Row(children: [
                InkWell(onTap: () => context.canPop() ? context.pop() : context.go('/home'), child: const IdeaIcon(IdeaIcons.close)),
                const Spacer(),
                BulbMark(size: 28, lit: finished ? 1 : 0),
              ]),
              const SizedBox(height: Gap.xxl),
              Text(finished ? (top.isEmpty ? s.scanNone : '${top.length} ${s.scanDone}') : s.scanTitle, style: IdeaType.headline(c.text, size: 38)),
              const SizedBox(height: Gap.xl),
              for (var i = 0; i < _stages.length; i++)
                Padding(
                  padding: const EdgeInsets.only(bottom: Gap.m),
                  child: Row(children: [
                    SizedBox(width: 28, child: i < _done ? IdeaIcon(IdeaIcons.check, size: 20, color: c.accentText) : Container(width: 8, height: 8, margin: const EdgeInsets.all(6), color: c.line)),
                    Expanded(child: Text(_stages[i], style: IdeaType.body(i < _done ? c.text : c.textMuted, size: 15))),
                  ]),
                ),
              if (finished) ...[
                const SizedBox(height: Gap.l),
                for (final o in top) OpportunityCard(opportunity: o, onTap: () => context.push('/opportunity/${o.id}')),
                const SizedBox(height: Gap.xl),
                IdeaButton(label: s.exploreRadar, primary: false, onPressed: () => context.go('/radar')),
              ],
            ]);
          },
        ),
      ),
    );
  }
}
