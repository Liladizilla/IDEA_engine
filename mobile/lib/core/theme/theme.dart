import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'tokens.dart';

/// Two families, clearly different roles:
///  - Sofia Sans Condensed: numerals, scores, headlines (signage-like, reads as an instrument)
///  - Schibsted Grotesk: everything you read
class IdeaType {
  static const _tabular = [FontFeature.tabularFigures()];

  static TextStyle numeral(Color color, double size, {FontWeight weight = FontWeight.w700}) => GoogleFonts.sofiaSansCondensed(
        fontSize: size,
        fontWeight: weight,
        height: 1.0,
        color: color,
        fontFeatures: _tabular,
      );

  static TextStyle headline(Color color, {double size = 32}) => GoogleFonts.sofiaSansCondensed(
        fontSize: size,
        fontWeight: FontWeight.w700,
        height: 1.05,
        letterSpacing: -0.2,
        color: color,
      );

  static TextStyle body(Color color, {double size = 15, FontWeight weight = FontWeight.w400, double height = 1.45}) =>
      GoogleFonts.schibstedGrotesk(fontSize: size, fontWeight: weight, height: height, color: color, fontFeatures: _tabular);
}

ThemeData buildTheme(IdeaColors c, Brightness brightness) {
  final base = ThemeData(brightness: brightness, useMaterial3: true);
  return base.copyWith(
    scaffoldBackgroundColor: c.ground,
    canvasColor: c.ground,
    colorScheme: ColorScheme(
      brightness: brightness,
      primary: c.filament,
      onPrimary: c.onFilament,
      secondary: c.filament,
      onSecondary: c.onFilament,
      error: c.text,
      onError: c.ground,
      surface: c.surface,
      onSurface: c.text,
    ),
    textTheme: GoogleFonts.schibstedGroteskTextTheme(base.textTheme).apply(bodyColor: c.text, displayColor: c.text),
    dividerColor: c.line,
    splashFactory: NoSplash.splashFactory,
    highlightColor: alpha(c.raised, 0.6),
    extensions: [c],
    iconTheme: IconThemeData(color: c.text),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: c.surface,
      contentPadding: const EdgeInsets.symmetric(horizontal: Gap.l, vertical: Gap.m),
      border: OutlineInputBorder(borderRadius: kBorder, borderSide: BorderSide(color: c.line)),
      enabledBorder: OutlineInputBorder(borderRadius: kBorder, borderSide: BorderSide(color: c.line)),
      focusedBorder: OutlineInputBorder(borderRadius: kBorder, borderSide: BorderSide(color: c.text, width: 1.5)),
      hintStyle: IdeaType.body(c.textMuted),
    ),
    bottomSheetTheme: BottomSheetThemeData(
      backgroundColor: c.surface,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(kRadius))),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: c.raised,
      contentTextStyle: IdeaType.body(c.text),
      shape: RoundedRectangleBorder(borderRadius: kBorder),
      behavior: SnackBarBehavior.floating,
    ),
  );
}
