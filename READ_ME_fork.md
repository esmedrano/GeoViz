This is a modified version of the original GeoViz that takes lists of geohashes and shows their location on the map

To use, download the code and open a terminal at the path of the folder.

Start GeoViz with: python app.py

Generate csv files with rings of geohashes using the script in the lib folder titled: get_hashrings.dart
- open the project folder in vsCode and run dart pub get in the terminal
- in the main function at the bottom of the file, adjust the vars to generate the hash files one at a time 
- they will appear in the root of the project

Use the generated .csv files in GeoViz
