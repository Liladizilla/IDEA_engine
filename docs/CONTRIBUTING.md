# Contributing

- Backend: `PYTHONPATH=. pytest -q` must pass. New scoring or clustering behavior needs a test using the synthetic data in `tests/factories.py`.
- Never let the pipeline emit an opportunity without evidence. If you add a path that can, add a test that it returns `InsufficientSignal` instead.
- Sample data comes from `scripts/generate_sample.py` through the real scoring engine. Regenerate, do not hand-edit `data.json`.
- Flutter: `flutter analyze` and `flutter test`. Strings go in `core/l10n/strings.dart`. Colours and spacing come from `core/theme/tokens.dart`. One accent, one 4px radius, no gradients or shadows. Icons come from `IdeaIcons`, not a package.
- Design changes: update `preview/template.html` in the same change so the preview stays the reference.
