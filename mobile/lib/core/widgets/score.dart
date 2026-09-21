import 'package:flutter/material.dart';

import '../../core/l10n/strings.dart';
import '../../domain/models.dart';
import '../theme/theme.dart';
import '../theme/tokens.dart';

/// The one memorable element. A ruler of 51 ticks; the ones the score reaches are lit.
class OpportunityScore extends StatelessWidget {
  const OpportunityScore({super.key, required this.score});
  final int score;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: score.toDouble()),
      duration: const Duration(milliseconds: 900),
      curve: Curves.easeOutCubic,
      builder: (context, v, _) => Semantics(
        label: '${context.s.opportunityScore} $score of 100',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text('${v.round()}', style: IdeaType.numeral(score >= 75 ? c.accentText : c.text, 96)),
                const SizedBox(width: Gap.s),
                Text('of 100', style: IdeaType.body(c.textMuted, size: 15)),
              ],
            ),
            const SizedBox(height: Gap.l),
            SizedBox(height: 26, width: double.infinity, child: CustomPaint(painter: _RulerPainter(v, c.filament, c.line))),
            const SizedBox(height: Gap.xs),
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Text('0', style: IdeaType.body(c.textMuted, size: 12)),
              Text('50', style: IdeaType.body(c.textMuted, size: 12)),
              Text('100', style: IdeaType.body(c.textMuted, size: 12)),
            ]),
          ],
        ),
      ),
    );
  }
}

class _RulerPainter extends CustomPainter {
  _RulerPainter(this.value, this.lit, this.dim);
  final double value;
  final Color lit;
  final Color dim;

  @override
  void paint(Canvas canvas, Size size) {
    const n = 50;
    final span = size.width - 2;
    for (var i = 0; i <= n; i++) {
      final v = i * 2;
      final h = i % 5 == 0 ? size.height : size.height * 0.5;
      final x = 1 + span * i / n;
      final paint = Paint()
        ..color = v <= value ? lit : dim
        ..strokeWidth = 2
        ..strokeCap = StrokeCap.butt;
      canvas.drawLine(Offset(x, size.height), Offset(x, size.height - h), paint);
    }
  }

  @override
  bool shouldRepaint(_RulerPainter old) => old.value != value || old.lit != lit || old.dim != dim;
}

/// Ten segments, one per 10 points. Pressure factors (competition, answer coverage) are drawn muted
/// because a high value there works against the opportunity.
class SegmentBar extends StatelessWidget {
  const SegmentBar({super.key, required this.value, this.muted = false, this.height = 8});
  final double value;
  final bool muted;
  final double height;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final filled = (value / 10).round().clamp(0, 10);
    return Row(
      children: List.generate(10, (i) {
        return Expanded(
          child: Container(
            height: height,
            margin: EdgeInsets.only(right: i == 9 ? 0 : 2),
            color: i < filled ? (muted ? c.textMuted : c.filament) : c.line,
          ),
        );
      }),
    );
  }
}

class FactorBars extends StatelessWidget {
  const FactorBars({super.key, required this.factors});
  final List<Factor> factors;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final f in factors)
          Padding(
            padding: const EdgeInsets.only(bottom: Gap.m),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    SizedBox(width: 124, child: Text(f.label, style: IdeaType.body(c.text, size: 14, weight: FontWeight.w500))),
                    Expanded(child: SegmentBar(value: f.value, muted: f.inverted)),
                    SizedBox(width: 44, child: Text(f.points.toStringAsFixed(1), textAlign: TextAlign.right, style: IdeaType.numeral(c.text, 18, weight: FontWeight.w600))),
                  ],
                ),
                if (f.note.isNotEmpty || f.inverted)
                  Padding(
                    padding: const EdgeInsets.only(top: 4, right: 44),
                    child: Text(f.note.isNotEmpty ? f.note : context.s.lowerIsBetter, style: IdeaType.body(c.textMuted, size: 12, height: 1.35)),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}

class CompetitionMeter extends StatelessWidget {
  const CompetitionMeter({super.key, required this.value, required this.label});
  final double value;
  final String label;
  @override
  Widget build(BuildContext context) => Row(children: [
        SizedBox(width: 90, child: Text(label, style: IdeaType.body(context.c.text, size: 14, weight: FontWeight.w500))),
        Expanded(child: SegmentBar(value: value, muted: true)),
      ]);
}

class UsageMeter extends StatelessWidget {
  const UsageMeter({super.key, required this.used, required this.limit});
  final int used;
  final int limit;
  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Text(context.s.usage, style: IdeaType.body(c.text, size: 14, weight: FontWeight.w500)),
        Text('$used of $limit', style: IdeaType.numeral(c.text, 18, weight: FontWeight.w600)),
      ]),
      const SizedBox(height: Gap.s),
      SegmentBar(value: limit == 0 ? 0 : used / limit * 100, muted: true),
    ]);
  }
}
