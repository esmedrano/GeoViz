import 'dart:io';

Future<void> generateCsvFile(List<List<String>> datasetA, {String prefix = 'dataset', double defaultValue = 1.0}) async {
  try {
    // // Get the temporary directory to save CSVs
    // final directory = await getTemporaryDirectory();
    // final String dirPath = directory.path;

    // // Save CSVs in the current working directory (not project root)
    // final String dirPath = Directory.current.path;

    // Use the explicitly specified project root path
    final String dirPath = Directory.current.path;
    
    // Generate CSV for Dataset A (flatten List<List<String>>)
    final fileA = File('$dirPath${prefix}_a.csv');
    final bufferA = StringBuffer();
    bufferA.writeln('geohash,value'); // CSV header
    for (List<String> geohashList in datasetA) {
      for (String geohash in geohashList) {
        bufferA.writeln('$geohash,$defaultValue');
      }
    }
    await fileA.writeAsString(bufferA.toString());
    print('CSV file generated: ${fileA.path}');

    // if (await fileA.exists()) {
    //   final contents = await fileA.readAsString();
    //   print('Dataset A contents:\n$contents');
    // } else {
    //   print('Error: Dataset A file does not exist');
    // }if (await fileA.exists()) {
    //   final contents = await fileA.readAsString();
    //   print('Dataset A contents:\n$contents');
    // } else {
    //   print('Error: Dataset A file does not exist');
    // }

    // // Generate CSV for Dataset B (List<String>)
    // final fileB = File('$dirPath/${prefix}_b.csv');
    // final bufferB = StringBuffer();
    // bufferB.writeln('geohash,value');
    // for (String geohash in datasetB) {
    //   bufferB.writeln('$geohash,$defaultValue');
    // }
    // await fileB.writeAsString(bufferB.toString());
    // print('CSV file generated: ${fileB.path}');
  } catch (e) {
    print('Error generating CSV files: $e');
  }
}
