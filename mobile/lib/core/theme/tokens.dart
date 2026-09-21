import 'package:flutter/material.dart';

/// One accent (filament). Everything else is a neutral. No gradients, no shadows.
/// The accent means one thing: this is lit, i.e. there is evidence here.
@immutable
class IdeaColors extends ThemeExtension<IdeaColors> {
  const IdeaColors({
    required this.ground,
    required this.surface,
    required this.raised,
    required this.line,
    required this.text,
    required this.textMuted,
    required this.filament,
    required this.onFilament,
    required this.accentText,
  });

  final Color ground;
  final Color surface;
  final Color raised;
  final Color line;
  final Color text;
  final Color textMuted;
  final Color filament;
  final Color onFilament;

  /// Filament colour that is safe to use as TEXT on [ground] (darker amber in light mode).
  final Color accentText;

  static const dark = IdeaColors(
    ground: Color(0xFF12202B),
    surface: Color(0xFF182A37),
    raised: Color(0xFF203648),
    line: Color(0xFF2C4356),
    text: Color(0xFFE8EEF1),
    textMuted: Color(0xFF8DA2B0),
    filament: Color(0xFFF4BF4F),
    onFilament: Color(0xFF12202B),
    accentText: Color(0xFFF4BF4F),
  );

  static const light = IdeaColors(
    ground: Color(0xFFE9EEF1),
    surface: Color(0xFFF3F6F8),
    raised: Color(0xFFDCE4E8),
    line: Color(0xFFC0CDD5),
    text: Color(0xFF12202B),
    textMuted: Color(0xFF4A5F6D),
    filament: Color(0xFFF4BF4F),
    onFilament: Color(0xFF12202B),
    accentText: Color(0xFF7A5300),
  );

  @override
  IdeaColors copyWith() => this;

  @override
  IdeaColors lerp(ThemeExtension<IdeaColors>? other, double t) {
    if (other is! IdeaColors) return this;
    return t < 0.5 ? this : other;
  }
}

/// One radius for every control. Dividers are square.
const double kRadius = 4;
final BorderRadius kBorder = BorderRadius.circular(kRadius);

class Gap {
  static const double xs = 4;
  static const double s = 8;
  static const double m = 12;
  static const double l = 16;
  static const double xl = 24;
  static const double xxl = 32;
  static const double xxxl = 48;
}

extension IdeaContext on BuildContext {
  IdeaColors get c => Theme.of(this).extension<IdeaColors>()!;
}

Color alpha(Color color, double a) => color.withAlpha((a * 255).round());
