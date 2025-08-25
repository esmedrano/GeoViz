# Original GeoViz
""" from flask import Flask, request, render_template, redirect, send_from_directory, jsonify
import os
import pandas as pd
import folium
import numpy as np
import pygeohash as pgh

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def geohash_to_polygon(geohash):
    bbox = pgh.decode_exactly(geohash)
    lat, lon, lat_err, lon_err = bbox
    return [
        (lat - lat_err, lon - lon_err),
        (lat - lat_err, lon + lon_err),
        (lat + lat_err, lon + lon_err),
        (lat + lat_err, lon - lon_err),
        (lat - lat_err, lon - lon_err)
    ]


@app.route('/')
def index():
    return render_template('index.html')

# Variable to store thresholds globally
thresholds = []

@app.route('/thresholds', methods=['POST'])
def update_thresholds():
    global thresholds
    thresholds = request.json.get('thresholds', [])
    return jsonify({'status': 'success'})

def get_color(file, metric_value, metric_name):
    if metric_name is None or metric_name not in file.columns:
        return 'gray'

    for threshold in thresholds:
        threshold_type = threshold['type']
        operator = threshold['operator']
        value = float(threshold['value'])
        color = threshold['color']

        # Calculate percentile if threshold type is percentile
        if threshold_type == 'percentile':
            value = np.percentile(file[metric_name], value)

        # Apply comparison based on operator
        if operator == '>' and metric_value > value:
            return color
        elif operator == '≥' and metric_value >= value:
            return color
        elif operator == '<' and metric_value < value:
            return color
        elif operator == '≤' and metric_value <= value:
            return color
        elif operator == '=' and metric_value == value:
            return color

    return 'gray'

@app.route('/map', methods=['POST'])
def map_view():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400
    
    
    metric = request.form.get('metric')
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    data_frame = pd.read_csv(file_path)
    data_frame = data_frame.apply(lambda col: pd.to_numeric(col.replace(',', '', regex=True), errors='coerce') if col.name != 'geohash' else col)
    column_names = data_frame.columns.tolist()
    print(data_frame.dtypes)
    
    if 'geohash' in column_names:
        column_names.remove('geohash')

    # Calculate the bounding box (min/max lat and lon)
    lats = []
    lons = []
    
    for idx, row in data_frame.iterrows():
        geohash = row['geohash']
        polygon_points = geohash_to_polygon(geohash)
        for lat, lon in polygon_points:
            lats.append(lat)
            lons.append(lon)
    
    if not lats or not lons:
        return jsonify({'error': 'Invalid geohash data.'}), 400

    # Calculate centroid
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    
    print("Columns in DataFrame:", column_names)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
    
    for idx, row in data_frame.iterrows():
        geohash = row['geohash']
        

        if metric is None or metric not in data_frame.columns:
            print(f"Invalid metric: {metric}")
            continue  
        
        metric_value = row[metric] if metric in row else 0  
        
        
        print(f"Row {idx}, Geohash: {geohash}, Metric: {metric}, Metric Value: {metric_value}")

        fill_color = get_color(data_frame, metric_value, metric)
        polygon_points = geohash_to_polygon(geohash)
        tooltip_text = f'Geohash: {geohash}<br>{metric.replace("_", " ").title()}: {metric_value:.2f}'
        
        folium.Polygon(
            locations=polygon_points,
            color='black',
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.6,
            weight=2,
            tooltip=tooltip_text
        ).add_to(m)
    
    map_path = os.path.join(app.config['UPLOAD_FOLDER'], 'map.html')
    m.save(map_path)
    
    return jsonify({'map_path': map_path, 'columns': column_names})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True) """

# When changing versions, the map.html and upload.html templates in geoviz-main\templates\ must also be changed to the appropriate version number

# fork version 1 - minimal 
""" from flask import Flask, render_template, request
import folium
import pandas as pd
import geohash2

app = Flask(__name__)

def geohash_to_polygon(geohash):
    lat, lon, lat_err, lon_err = geohash2.decode_exactly(geohash)
    lat, lon = float(lat), float(lon)
    return [
        [lat - lat_err, lon - lon_err],
        [lat - lat_err, lon + lon_err],
        [lat + lat_err, lon + lon_err],
        [lat + lat_err, lon - lon_err],
        [lat - lat_err, lon - lon_err],
    ]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file_a = request.files['file_a']
        file_b = request.files['file_b']
        df_a = pd.read_csv(file_a)
        df_b = pd.read_csv(file_b)

        # Center map on average coordinates
        lat_lon = [geohash2.decode(gh) for gh in pd.concat([df_a, df_b])['geohash']]
        map_center = [sum(float(x[0]) for x in lat_lon) / len(lat_lon),
                      sum(float(x[1]) for x in lat_lon) / len(lat_lon)]
        folium_map = folium.Map(location=map_center, zoom_start=2)

        # Plot Dataset A (blue)
        for _, row in df_a.iterrows():
            geohash = row['geohash']
            value = row.get('value', 1)
            polygon = geohash_to_polygon(geohash)
            folium.Polygon(
                locations=polygon,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=min(0.2 + value * 0.01, 0.6),
                weight=1,
                popup=geohash  # Optional: Show geohash on click
            ).add_to(folium_map)

        # Plot Dataset B (red)
        for _, row in df_b.iterrows():
            geohash = row['geohash']
            value = row.get('value', 1)
            polygon = geohash_to_polygon(geohash)
            folium.Polygon(
                locations=polygon,
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=min(0.2 + value * 0.01, 0.6),
                weight=1,
                popup=geohash  # Optional: Show geohash on click
            ).add_to(folium_map)

        map_html = folium_map._repr_html_()
        return render_template('map.html', map_html=map_html)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True) """

from flask import Flask, render_template, request, jsonify, send_from_directory, session
import folium
import pandas as pd
import geohash2
import numpy as np
import os
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your-secret-key'  # Required for session

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def geohash_to_polygon(geohash):
    try:
        lat, lon, lat_err, lon_err = geohash2.decode_exactly(geohash)
        lat, lon = float(lat), float(lon)
        return [
            [lat - lat_err, lon - lon_err],
            [lat - lat_err, lon + lon_err],
            [lat + lat_err, lon + lon_err],
            [lat + lat_err, lon - lon_err],
            [lat - lat_err, lon - lon_err],
        ]
    except Exception as e:
        logging.error(f"Error decoding geohash {geohash}: {str(e)}")
        return None

def generate_geohash_grid(min_lat, max_lat, min_lon, max_lon, precisions=[1, 2, 3, 4, 5, 6]):
    """Generate geohashes for the map's bounds at specified precision levels."""
    grid_data = {}
    for precision in precisions:
        step_factor = 2 ** (6 - precision) * 100
        lat_step = (max_lat - min_lat) / step_factor
        lon_step = (max_lon - min_lon) / step_factor
        geohashes = set()
        
        for lat in np.arange(min_lat, max_lat, lat_step):
            for lon in np.arange(min_lon, max_lon, lon_step):
                gh = geohash2.encode(lat, lon, precision=precision)
                geohashes.add(gh)
        
        grid_data[precision] = [
            {'geohash': gh, 'polygon': geohash_to_polygon(gh)}
            for gh in geohashes if geohash_to_polygon(gh) is not None
        ]
        logging.debug(f"Generated {len(geohashes)} geohashes for precision {precision}")
    
    return grid_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if files are uploaded or use session-stored filenames
        if 'file_a' in request.files and 'file_b' in request.files:
            file_a = request.files['file_a']
            file_b = request.files['file_b']
            if file_a.filename == '' or file_b.filename == '':
                return jsonify({'error': 'No selected file.'}), 400
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_a_name = file_a.filename
            file_b_name = file_b.filename
            file_a.save(os.path.join(app.config['UPLOAD_FOLDER'], file_a_name))
            file_b.save(os.path.join(app.config['UPLOAD_FOLDER'], file_b_name))
            session['file_a_name'] = file_a_name
            session['file_b_name'] = file_b_name
        elif 'file_a_name' in session and 'file_b_name' in session:
            file_a_name = session['file_a_name']
            file_b_name = session['file_b_name']
        else:
            return jsonify({'error': 'No file information available.'}), 400

        file_a_path = os.path.join(app.config['UPLOAD_FOLDER'], file_a_name)
        file_b_path = os.path.join(app.config['UPLOAD_FOLDER'], file_b_name)

        try:
            df_a = pd.read_csv(file_a_path)
            df_b = pd.read_csv(file_b_path)
        except Exception as e:
            logging.error(f"Error reading CSV files: {str(e)}")
            return jsonify({'error': 'Error reading CSV files.'}), 400

        logging.debug(f"Dataset A columns: {df_a.columns.tolist()}")
        logging.debug(f"Dataset B columns: {df_b.columns.tolist()}")

        columns_a = [col for col in df_a.columns if col != 'geohash']
        columns_b = [col for col in df_b.columns if col != 'geohash']
        columns = list(set(columns_a + columns_b))

        # Calculate map bounds
        lat_lon = []
        for gh in pd.concat([df_a, df_b])['geohash']:
            try:
                lat, lon = geohash2.decode(gh)
                lat_lon.append((float(lat), float(lon)))
            except Exception as e:
                logging.error(f"Error decoding geohash {gh}: {str(e)}")
                continue
        
        if not lat_lon:
            return jsonify({'error': 'Invalid geohash data.'}), 400
        
        min_lat, max_lat = min(x[0] for x in lat_lon), max(x[0] for x in lat_lon)
        min_lon, max_lon = min(x[1] for x in lat_lon), max(x[1] for x in lat_lon)
        map_center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]

        # Get selected grid precisions
        precisions = [int(p) for p in request.form.getlist('precisions') if p in ['1', '2', '3', '4', '5', '6']]
        logging.debug(f"Selected precisions: {precisions}")

        # Generate map
        folium_map = folium.Map(location=map_center, zoom_start=8, control_scale=True, tiles="OpenStreetMap")

        # Plot Dataset A (blue)
        for _, row in df_a.iterrows():
            geohash = row['geohash']
            try:
                value = row.get('value', 1)
                polygon = geohash_to_polygon(geohash)
                if polygon is None:
                    continue
                logging.debug(f"Processing Dataset A geohash: {geohash}, value: {value}")
                folium.Polygon(
                    locations=polygon,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=min(0.2 + value * 0.01, 0.6),
                    weight=1,
                    popup=geohash,
                    tooltip=f"Geohash: {geohash}"
                ).add_to(folium_map)
            except Exception as e:
                logging.error(f"Error processing Dataset A geohash {geohash}: {str(e)}")
                continue

        # Plot Dataset B (red)
        for _, row in df_b.iterrows():
            geohash = row['geohash']
            try:
                value = row.get('value', 1)
                polygon = geohash_to_polygon(geohash)
                if polygon is None:
                    continue
                logging.debug(f"Processing Dataset B geohash: {geohash}, value: {value}")
                folium.Polygon(
                    locations=polygon,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=min(0.2 + value * 0.01, 0.6),
                    weight=1,
                    popup=geohash,
                    tooltip=f"Geohash: {geohash}"
                ).add_to(folium_map)
            except Exception as e:
                logging.error(f"Error processing Dataset B geohash {geohash}: {str(e)}")
                continue

        # Add grid polygons
        if precisions:
            grid_data = generate_geohash_grid(min_lat, max_lat, min_lon, max_lon, precisions)
            for precision in precisions:
                for item in grid_data.get(precision, []):
                    folium.Polygon(
                        locations=item['polygon'],
                        color='black',
                        # fill=True,
                        # fill_color='black',
                        # fill_opacity=0.1,
                        weight=1,
                        popup=item['geohash'],
                        #tooltip=f"Geohash: {item['geohash']}"
                    ).add_to(folium_map)

        # Save map to uploads
        map_path = os.path.join(app.config['UPLOAD_FOLDER'], 'map.html')
        folium_map.save(map_path)

        return render_template('map.html', map_path='map.html', columns=columns, precisions=precisions)

    return render_template('upload.html')

@app.route('/Uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
