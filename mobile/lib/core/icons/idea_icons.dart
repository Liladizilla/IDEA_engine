import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../theme/tokens.dart';

/// Custom, angular icon set drawn on a 24 grid: square caps, mitred joins, one stroke weight.
/// The same path data drives the design preview, so what you approved is what ships.
/// (The bulb mark itself is drawn by BulbMark in idea_logo.dart.)
class IdeaIcons {
  static const discover =
      '<path d="M16.13 7.25A6.5 6.5 0 1 1 13.75 4.87"/><path d="M15.1 15.1L20.5 20.5"/>';
  static const radar =
      '<path d="M19.36 7.75A8.5 8.5 0 1 1 16.25 4.64"/><path d="M15.9 9.75A4.5 4.5 0 1 1 14.25 8.1"/><circle cx="12" cy="12" r="1.6" fill="currentColor" stroke="none"/>';
  static const saved = '<path d="M6.5 3.5H17.5V20.5L12 16L6.5 20.5Z"/>';
  static const profile =
      '<circle cx="12" cy="8" r="3.5"/><path d="M5 20.5V18.5L8.5 14.5H15.5L19 18.5V20.5"/>';
  static const back = '<path d="M14.5 5L7.5 12L14.5 19"/>';
  static const next = '<path d="M9.5 5L16.5 12L9.5 19"/>';
  static const filter = '<path d="M3.5 8H20.5M3.5 16H20.5"/><path d="M8.5 5V11M15.5 13V19" stroke-width="3"/>';
  static const close = '<path d="M6 6L18 18M18 6L6 18"/>';
  static const external =
      '<path d="M10 5.5H5.5V18.5H18.5V14"/><path d="M13 5.5H18.5V11M18.5 5.5L11 13"/>';
  static const create = '<path d="M4.5 19.5L5.5 15L15.5 5L19.5 9L9.5 19Z"/><path d="M13.5 7L17.5 11"/>';
  static const up = '<path d="M12 6L19 17H5Z" fill="currentColor" stroke="none"/>';
  static const down = '<path d="M12 18L19 7H5Z" fill="currentColor" stroke="none"/>';
  static const flat = '<path d="M4 9.5H20V14.5H4Z" fill="currentColor" stroke="none"/>';
  static const check = '<path d="M5 12.5L10 17.5L19 7"/>';
}

class IdeaIcon extends StatelessWidget {
  const IdeaIcon(this.body, {super.key, this.size = 24, this.color, this.filled = false});

  final String body;
  final double size;
  final Color? color;
  final bool filled;

  @override
  Widget build(BuildContext context) {
    final tint = color ?? context.c.text;
    final svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<g fill="${filled ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="1.75" '
        'stroke-linejoin="miter" stroke-linecap="butt">$body</g></svg>';
    return SvgPicture.string(
      svg,
      width: size,
      height: size,
      colorFilter: ColorFilter.mode(tint, BlendMode.srcIn),
    );
  }
}
