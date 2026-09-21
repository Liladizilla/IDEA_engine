import 'package:flutter/material.dart';

import '../theme/theme.dart';
import '../theme/tokens.dart';

/// Daily signal counts as square bars. The last seven days are lit, matching how growth is calculated
/// (second week against first week), so the picture and the number cannot disagree.
class TrendGraph extends StatelessWidget {
  const TrendGraph({super.key, required this.values, this.height = 72, this.labels = false, this.startLabel = '', this.endLabel = ''});
  final List<int> values;
  final double height;
  final bool labels;
  final String startLabel;
  final String endLabel;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(height: height, width: double.infinity, child: CustomPaint(painter: _BarsPainter(values, c.filament, alpha(c.textMuted, 0.55)))),
        if (labels)
          Padding(
            padding: const EdgeInsets.only(top: Gap.xs),
            child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Text(startLabel, style: IdeaType.body(c.textMuted, size: 12)),
              Text(endLabel, style: IdeaType.body(c.textMuted, size: 12)),
            ]),
          ),
      ],
    );
  }
}

class _BarsPainter extends CustomPainter {
  _BarsPainter(this.values, this.lit, this.dim);
  final List<int> values;
  final Color lit;
  final Color dim;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;
    final maxV = values.reduce((a, b) => a > b ? a : b).toDouble();
    if (maxV == 0) return;
    const gap = 3.0;
    final w = (size.width - gap * (values.length - 1)) / values.length;
    for (var i = 0; i < values.length; i++) {
      final h = size.height * values[i] / maxV;
      final paint = Paint()..color = i >= values.length - 7 ? lit : dim;
      canvas.drawRect(Rect.fromLTWH(i * (w + gap), size.height - h, w, h), paint);
    }
  }

  @override
  bool shouldRepaint(_BarsPainter old) => old.values != values || old.lit != lit || old.dim != dim;
}
