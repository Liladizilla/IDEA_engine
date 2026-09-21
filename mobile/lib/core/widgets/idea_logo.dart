import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/theme.dart';
import '../theme/tokens.dart';

double _rad(double deg) => deg * math.pi / 180;

/// The IDEA mark: a bulb whose glass has a gap where the light gets out, and a filament dot that is either lit or not.
/// Drawn on a 24 grid so it stays crisp from the 24dp tab icon up to the splash screen.
class BulbMark extends StatelessWidget {
  const BulbMark({super.key, this.size = 48, this.color, this.filament, this.lit = 1});

  final double size;
  final Color? color;
  final Color? filament;

  /// 0 = unlit (same colour as the glass), 1 = lit (filament accent). Animate this for the splash.
  final double lit;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size.square(size),
      painter: _BulbPainter(color ?? context.c.text, filament ?? context.c.filament, lit),
    );
  }
}

class _BulbPainter extends CustomPainter {
  _BulbPainter(this.color, this.filament, this.lit);

  final Color color;
  final Color filament;
  final double lit;

  @override
  void paint(Canvas canvas, Size size) {
    final k = size.width / 24;
    canvas.scale(k, k);
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.75
      ..strokeCap = StrokeCap.butt
      ..strokeJoin = StrokeJoin.miter
      ..color = color;
    final glass = Rect.fromCircle(center: const Offset(12, 9.5), radius: 6.5);
    canvas.drawArc(glass, _rad(117.5), _rad(192.5), false, stroke);
    canvas.drawArc(glass, _rad(335), _rad(87.5), false, stroke);
    final base = Path()
      ..moveTo(9, 15.27)
      ..lineTo(9, 17.75)
      ..lineTo(15, 17.75)
      ..lineTo(15, 15.27);
    canvas.drawPath(base, stroke);
    canvas.drawLine(const Offset(10.5, 20.5), const Offset(13.5, 20.5), stroke);

    final glow = Color.lerp(color, filament, lit)!;
    canvas.drawCircle(const Offset(12, 9.5), 1.9 + 0.3 * lit, Paint()..color = glow);
  }

  @override
  bool shouldRepaint(_BulbPainter old) => old.color != color || old.filament != filament || old.lit != lit;
}

class IdeaLogo extends StatelessWidget {
  const IdeaLogo({super.key, this.size = 40, this.showWordmark = true, this.lit = 1});

  final double size;
  final bool showWordmark;
  final double lit;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        BulbMark(size: size, lit: lit),
        if (showWordmark) ...[
          SizedBox(width: size * 0.18),
          Text('IDEA', style: IdeaType.headline(context.c.text, size: size * 0.9).copyWith(letterSpacing: size * 0.06)),
        ],
      ],
    );
  }
}
