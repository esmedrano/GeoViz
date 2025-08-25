List<List<String>> shortenGeohashRings(List<List<String>> geohashRings, String optimalPrefix, bool initialQuery) {
  late List<List<String>> filteredRings;
  
  if (initialQuery) {
    // Filter out rings where all hashes start with optimalPrefix
    filteredRings = geohashRings.where((ring) {
      // Return true (keep the ring) if at least one hash does NOT start with optimalPrefix
      return ring.any((hash) => !hash.startsWith(optimalPrefix));
    }).toList();
  } 

  if (!initialQuery) {
    // Find the index of the first ring containing a hash that exactly matches optimalPrefix
    final firstMatchIndex = geohashRings.indexWhere((ring) => ring.any((hash) => hash == optimalPrefix));
    
    // Keep the matching ring and all subsequent rings, or empty list if no match
    filteredRings = firstMatchIndex != -1 ? geohashRings.sublist(firstMatchIndex) : [];
  }

  // Log for debugging
  if (filteredRings.length == geohashRings.length) {
    print('No rings removed; all rings have at least one hash not matching prefix: $optimalPrefix');
  } else {
    print('Removed ${geohashRings.length - filteredRings.length} rings where all hashes matched prefix: $optimalPrefix');
  }

  return filteredRings;
}