import 'package:flutter/widgets.dart';

/// Every user-facing string lives here, never inline in a widget.
///
/// To add a language: subclass [Strings], override what differs (anything not overridden falls back to English),
/// and register it in [Strings.forLocale]. When you outgrow this, move to ARB files with `flutter gen-l10n`;
/// call sites (`context.s.xyz`) stay the same.
class Strings {
  const Strings();

  static Strings forLocale(Locale locale) {
    switch (locale.languageCode) {
      // case 'sw': return const StringsSw();
      default:
        return const Strings();
    }
  }

  // Brand
  String get tagline => 'Find what people want to know.';
  String get productName => 'IDEA';

  // Navigation
  String get navHome => 'Home';
  String get navDiscover => 'Discover';
  String get navRadar => 'Radar';
  String get navSaved => 'Saved';
  String get navProfile => 'Profile';

  // Home
  String greeting(int hour) => hour < 12 ? 'Good morning.' : hour < 18 ? 'Good afternoon.' : 'Good evening.';
  String get homePrompt => 'What are you creating today?';
  String get findAnIdea => 'Find an idea';
  String get exploreRadar => 'Explore radar';
  String get todaysOpportunities => 'Today\'s opportunities';
  String get newQuestions => 'New questions';
  String get yourNiche => 'Your niche';
  String get trendingSignals => 'Trending signals';
  String get seeAll => 'See all';

  // Discover
  String get searchHint => 'What are people asking about?';
  String get filters => 'Filters';
  String get minScore => 'Minimum opportunity score';
  String get apply => 'Apply';
  String get reset => 'Reset';
  String get noResults => 'Nothing matches yet. Try a broader phrase or lower the minimum score.';
  String get categories => 'Categories';

  // Radar
  String get radarTitle => 'Radar';
  String get radarIntro => 'Questions people are asking right now, grouped by what they have in common.';
  String get gatheringEvidence => 'Still gathering evidence';

  // Opportunity
  String get opportunityScore => 'Opportunity score';
  String get scoreCaveat => 'Strength of the evidence found. Not a prediction of views.';
  String get whyDetected => 'Why this was detected';
  String get theQuestion => 'The question';
  String get whoIsAsking => 'Who is asking';
  String get signalEvidence => 'Evidence';
  String get trend => 'Trend';
  String get competition => 'Competition';
  String get answerGap => 'Answer gap';
  String get relatedQuestions => 'Related questions';
  String get contentAngles => 'Content angles';
  String get sources => 'Sources';
  String get research => 'Research';
  String get createContent => 'Create content';
  String get save => 'Save';
  String get saved => 'Saved';
  String get openSource => 'Open source';
  String get sampleSource => 'Sample item. No live link.';
  String get lowerIsBetter => 'Lower is better for you';
  String get lastFourteenDays => 'Last 14 days';
  String get daysAgoLabel => '14 days ago';
  String get today => 'Today';
  String get whyNow => 'Why now';

  // Insufficient signal
  String get insufficientTitle => 'Insufficient signal';
  String insufficientBody(String scope, int found, int needed, int sources, int sourcesNeeded) =>
      'IDEA found $found of $needed questions and $sources of $sourcesNeeded sources for $scope. '
      'That is not enough evidence to name a reliable opportunity, so none is shown.';

  // Onboarding
  String get onbCreateQ => 'What do you create?';
  String get onbNicheQ => 'Do you have a niche?';
  String get onbNicheYes => 'Yes, I have one';
  String get onbNicheNo => 'No, help me find one';
  String get onbNicheField => 'Your niche';
  String get onbAudienceQ => 'Who is your audience?';
  String get onbAudienceHint => 'For example: first-time founders in Nairobi';
  String get onbNotifyQ => 'How often should IDEA tell you what it found?';
  String get onbContinue => 'Continue';
  String get onbFinish => 'Start';
  String get skip => 'Skip';

  // Scan
  String get scanTitle => 'Looking for gaps';
  String get scanDone => 'opportunities found';
  String get scanNone => 'No reliable opportunity yet';

  // Saved
  String get savedEmptyTitle => 'Nothing saved yet';
  String get savedEmptyBody => 'Save an opportunity and it will stay here, even offline.';

  // Profile
  String get creatorProfile => 'Creator profile';
  String get usage => 'AI use today';
  String get aiProvider => 'AI provider';
  String get dataMode => 'Data';
  String get notifications => 'Notifications';

  // Status
  String get sampleData => 'Sample data';
  String get offlineNotice => 'You are offline. Showing your last saved results.';
  String get errorLoad => 'IDEA could not load your opportunities. Check your connection and try again.';
  String get retry => 'Try again';

  // Create content
  String get chooseFormat => 'Choose a format';
  String get generationNotConnected => 'Content generation needs the AI provider connected on the backend.';
}

extension StringsContext on BuildContext {
  Strings get s => Strings.forLocale(Localizations.maybeLocaleOf(this) ?? const Locale('en'));
}
