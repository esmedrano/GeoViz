List<List<String>> shortenGeohashRings(List<List<String>> geohashRings, String optimalPrefix, bool initialQuery) {
  late List<List<String>> filteredRings;
  
  if (initialQuery) {
    // Filter out rings where all hashes start with optimalPrefix
    filteredRings = geohashRings.where((ring) {
      // Return true (keep the ring) if at least one hash does NOT start with optimalPrefix
      return ring.any((hash) => !hash.startsWith(optimalPrefix));
    }).toList();
  } 

  if (!initialQuery) {  // This removes the matching ring and all rings before
    final firstMatchIndex = geohashRings.indexWhere((ring) => ring.any((hash) => hash == optimalPrefix));
    filteredRings = firstMatchIndex != -1 ? geohashRings.sublist(firstMatchIndex + 2) : [];
  }

  // Log for debugging
  if (filteredRings.length == geohashRings.length) {
    print('No rings removed; all rings have at least one hash not matching prefix: $optimalPrefix');
  } else {
    print('Removed ${geohashRings.length - filteredRings.length} rings where all hashes matched prefix: $optimalPrefix');
  }

  return filteredRings;
}
