# -*- coding: utf-8 -*-
"""
Created on Wed May 29 11:08:10 2024

@author: caioc
"""

import ee
import csv
import pandas as pd

# Initialize the Earth Engine API
ee.Authenticate()
ee.Initialize()

# Function to extract median pixel values in a 3x3 window for each point
def extract_pixel_values(point):
    try:
        # Convert the input tuple to an ee.Geometry.Point
        point_gee = ee.Geometry.Point([point[2], point[1]])
        
        # Define the pixel window size in meters. Sentinel-2 has a resolution of 10m/pixel.
        pixel_size = 10 # meters
        n = 3 # number of pixels for buffer
        buffer_size = (n * pixel_size) / 2
        
        # Create a buffer around the point
        window_geometry = point_gee.buffer(buffer_size)
        
        # Convert the date to a format acceptable by Earth Engine
        date = ee.Date(point[3])
        
        # Define a time window for the image (e.g., 1 day before and after the date)
        time_window = ee.DateRange(date.advance(-2, 'day'), date.advance(2, 'day'))
        
        # Filter the image collection for the time window and point of interest
        image_collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                            .filterBounds(point_gee) \
                            .filterDate(time_window)
        
        # Check if the filtered image collection contains any images
        num_images = image_collection.size().getInfo()
        if num_images == 0:
            return (point[0], None, None)  # Return None if no image is found
        
        # If there are images, use the first image in the collection
        image = image_collection.first()
        
        # Extract the median pixel value for the window of interest
        pixel_value = image.reduceRegion(reducer=ee.Reducer.median(), geometry=window_geometry, scale=10).getInfo()
        
        # Extract the date and time of the image
        image_date = ee.Date(image.get('system:time_start'))
        image_date_string = image_date.format('Y-M-d-hh-mm-ss').getInfo()
        
        # Return ID, median pixel values, and the date/time of the image
        return (point[0], pixel_value, image_date_string)
    
    except Exception as e:
        print(f"Error processing point {point[0]}: {e}")
        return (point[0], None, None)

# Path to the CSV file
csv_file_path = r'C:\Users\caioc\Desktop\RDO.csv'

# List to store the points from the CSV file
points_list = []

# Read the CSV file and extract the points
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    # Skip the header if present
    next(csv_reader, None)
    for line in csv_reader:
        # Extract id, latitude, longitude, and date
        point = (line[0], float(line[1]), float(line[2]), line[3])
        points_list.append(point)

# Iterate over the list of points and extract pixel values
pixel_values_list = [extract_pixel_values(point) for point in points_list]

# Create a dictionary to store the results
results = {'ID': [], 'Data_Hora_Imagem': []}
for band_num in range(1, 13):
    results[f'B{band_num}'] = []

# Fill the dictionary with pixel values and the date/time of the image
for id_point, pixel_values, datetime_image in pixel_values_list:
    results['ID'].append(id_point)
    results['Data_Hora_Imagem'].append(datetime_image)
    if isinstance(pixel_values, dict):
        for band_num in range(1, 13):
            band_name = f'B{band_num}'
            results[band_name].append(pixel_values.get(band_name, None))
    else:
        for band_num in range(1, 13):
            results[f'B{band_num}'].append(None)

# Create a pandas DataFrame with the results
df = pd.DataFrame(results)

# Save the DataFrame to a CSV file
df.to_csv('pixel_values_datetime.csv', index=False)

print("Table saved successfully!")

