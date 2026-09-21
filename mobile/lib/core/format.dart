String formatAgo(int minutes) {
  if (minutes < 60) return '$minutes min ago';
  if (minutes < 1440) return '${minutes ~/ 60} h ago';
  return '${minutes ~/ 1440} d ago';
}

String formatPercent(double ratio) {
  final pct = (ratio * 100).round();
  return pct > 0 ? '+$pct%' : '$pct%';
}

String sourceLabel(String key) {
  switch (key) {
    case 'youtube':
      return 'YouTube';
    case 'reddit':
      return 'Reddit';
    case 'search':
      return 'Search';
    case 'rss':
      return 'Feeds';
    default:
      return key.isEmpty ? key : key[0].toUpperCase() + key.substring(1);
  }
}

String velocityLabel(String v) {
  switch (v) {
    case 'accelerating':
      return 'Accelerating';
    case 'emerging':
      return 'Emerging';
    case 'declining':
      return 'Declining';
    case 'stable':
      return 'Stable';
    default:
      return 'Unknown';
  }
}

String levelLabel(String level) => level.isEmpty ? level : level[0].toUpperCase() + level.substring(1);

String formatLabel(String f) {
  switch (f) {
    case 'youtube_long':
      return 'YouTube long-form';
    case 'youtube_short':
      return 'YouTube Short';
    case 'tiktok':
      return 'TikTok';
    case 'reel':
      return 'Instagram Reel';
    case 'linkedin':
      return 'LinkedIn post';
    case 'x_thread':
      return 'X thread';
    case 'blog':
      return 'Blog post';
    case 'newsletter':
      return 'Newsletter';
    case 'podcast':
      return 'Podcast';
    default:
      return f;
  }
}

const contentFormats = ['youtube_long', 'youtube_short', 'tiktok', 'reel', 'linkedin', 'x_thread', 'blog', 'newsletter', 'podcast'];
