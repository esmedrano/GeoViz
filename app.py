from flask import Flask, request, render_template, redirect, send_from_directory, jsonify
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
    
    
    print("Columns in DataFrame:", column_names)
    
    m = folium.Map(location=[12.975563860577177, 77.5713505708612], zoom_start=10)
    
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
    app.run(debug=True)