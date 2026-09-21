import 'package:flutter/material.dart';

import '../icons/idea_icons.dart';
import '../theme/theme.dart';
import '../theme/tokens.dart';

class IdeaButton extends StatelessWidget {
  const IdeaButton({super.key, required this.label, required this.onPressed, this.primary = true, this.icon, this.expand = true});

  final String label;
  final VoidCallback? onPressed;
  final bool primary;
  final String? icon;
  final bool expand;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final enabled = onPressed != null;
    final fg = primary ? c.onFilament : c.text;
    final child = Row(
      mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (icon != null) ...[IdeaIcon(icon!, size: 20, color: fg), const SizedBox(width: Gap.s)],
        Text(label, style: IdeaType.body(fg, size: 16, weight: FontWeight.w600, height: 1.2)),
      ],
    );
    return Opacity(
      opacity: enabled ? 1 : 0.45,
      child: Material(
        color: primary ? c.filament : Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: kBorder, side: primary ? BorderSide.none : BorderSide(color: c.line, width: 1.5)),
        child: InkWell(
          onTap: onPressed,
          borderRadius: kBorder,
          child: Container(constraints: const BoxConstraints(minHeight: 52), padding: const EdgeInsets.symmetric(horizontal: Gap.xl, vertical: Gap.m), alignment: Alignment.center, child: child),
        ),
      ),
    );
  }
}

class Hairline extends StatelessWidget {
  const Hairline({super.key});
  @override
  Widget build(BuildContext context) => Container(height: 1, color: context.c.line);
}

/// Section title. Sentence case, one style, no eyebrow labels.
class SectionTitle extends StatelessWidget {
  const SectionTitle(this.text, {super.key, this.trailing, this.onTrailing});

  final String text;
  final String? trailing;
  final VoidCallback? onTrailing;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Padding(
      padding: const EdgeInsets.only(top: Gap.xxl, bottom: Gap.m),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(child: Text(text, style: IdeaType.headline(c.text, size: 24))),
          if (trailing != null)
            InkWell(
              onTap: onTrailing,
              child: Padding(padding: const EdgeInsets.symmetric(vertical: Gap.xs), child: Text(trailing!, style: IdeaType.body(c.accentText, size: 14, weight: FontWeight.w600))),
            ),
        ],
      ),
    );
  }
}

class ScreenPad extends StatelessWidget {
  const ScreenPad({super.key, required this.child, this.bottom = Gap.xxl});
  final Widget child;
  final double bottom;
  @override
  Widget build(BuildContext context) => Padding(padding: EdgeInsets.fromLTRB(Gap.xl, 0, Gap.xl, bottom), child: child);
}

class SourceChip extends StatelessWidget {
  const SourceChip(this.label, {super.key});
  final String label;
  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Gap.s, vertical: 3),
      decoration: BoxDecoration(border: Border.all(color: c.line), borderRadius: kBorder),
      child: Text(label, style: IdeaType.body(c.textMuted, size: 12, weight: FontWeight.w500, height: 1.3)),
    );
  }
}

/// Small stripe shown wherever fixture data is on screen, so it can never pass for real evidence.
class SampleStrip extends StatelessWidget {
  const SampleStrip({super.key, required this.label, required this.detail});
  final String label;
  final String detail;
  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: Gap.xl, vertical: Gap.s),
      color: c.raised,
      child: Text.rich(TextSpan(children: [
        TextSpan(text: '$label  ', style: IdeaType.body(c.text, size: 12, weight: FontWeight.w700, height: 1.3)),
        TextSpan(text: detail, style: IdeaType.body(c.textMuted, size: 12, height: 1.3)),
      ])),
    );
  }
}
