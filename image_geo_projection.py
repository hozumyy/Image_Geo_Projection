#! /usr/bin/env python
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import yaml
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class ImageGeoProjection:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.image = Image.open(self.config['image_path'])

    def mapping(self):
        width, height = self.image.size

        # Create a mesh grid
        array_width, array_height = np.mgrid[-1*int(width/2):int(width/2):complex(width+1), -1*int(height/2):int(height/2):complex(height+1)]

        # Calculate azimuth and elevation
        self.azimuth = self.config['azimuth_center'] + array_width * self.config['azimuth_width'] / width
        self.elevation = self.config['elvation_center'] - array_height * self.config['elevation_width'] / height

        # Convert to geographic coordinates
        re = self.config['Re']
        A = re + self.config['alt_camera']
        C = re + self.config['alt_mapping']
        c_angle = np.deg2rad(90. + self.elevation)
        a_angle = np.arcsin((A/C) * np.sin(c_angle))
        b_angle = np.pi - a_angle - c_angle
        r = re * b_angle

        ygeo = r * np.cos(np.deg2rad(self.azimuth))
        xgeo = r * np.sin(np.deg2rad(self.azimuth))

        # Latitude and longitude conversion
        circ = 2.0 * np.pi * re
        deglatperkm = 360.0 / circ
        radlat = re * np.cos(np.deg2rad(self.config['lat_camera']))
        circlat = 2.0 * np.pi * radlat
        deglonperkm = 360.0 / circlat
        self.r  = r

        self.xlon = xgeo * deglonperkm + self.config['lon_camea']
        self.ylat = ygeo * deglatperkm + self.config['lat_camera']


    def plot(self):
        # Plot on latitude and longitude
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

        if self.config['map_crop']:
            lat0, lat1 = self.config['lat_map0'], self.config['lat_map1']
            lon0, lon1 = self.config['lon_map0'], self.config['lon_map1']
            self.xlon = np.clip(self.xlon, lon0, lon1)
            self.ylat = np.clip(self.ylat, lat0, lat1)
            crop_suffix = '_cropped'  # Suffix for cropped output
        else:
            crop_suffix = ''  # No suffix if no cropping

        # Convert image data to a NumPy array
        image_array = np.array(self.image)

        # Plot the result on the map
        mesh = ax.pcolormesh(self.xlon, self.ylat, image_array[:, :, 0].T, transform=ccrs.PlateCarree(), cmap='gray', zorder=10)

        # Add coastlines and states
        ax.coastlines()
        ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)

        # Add gridlines and configure labels
        gl = ax.gridlines(draw_labels=True, linestyle='--')
        gl.top_labels = False  # Disable top labels
        gl.right_labels = False  # Disable right labels
        gl.bottom_labels = True  # Enable bottom labels
        gl.left_labels = True  # Enable left labels
        gl.xlabel_style = {'size': 10, 'color': 'black'}
        gl.ylabel_style = {'size': 10, 'color': 'black'}

        # Get the camera position from the config file (lat, lon)
        camera_lat = self.config['lat_camera']
        camera_lon = self.config['lon_camea']

        # Plot the camera position as a star using scatter
        ax.scatter(camera_lon, camera_lat, color='red', marker='*', s=200, transform=ccrs.PlateCarree(), label='Camera', zorder=20)

        # Add a color bar
        plt.colorbar(mesh, ax=ax, orientation='vertical', label='Image Intensity')

        # Save the result
        if not os.path.exists(self.config['result_path']):
            os.makedirs(self.config['result_path'])

        base_image_name = os.path.splitext(os.path.basename(self.config['image_path']))[0]
        output_file_name = f"{self.config['result_path']}/{base_image_name}_mapped_image{crop_suffix}.png"
        plt.savefig(output_file_name)
        plt.show()


if __name__ == "__main__":
    projection = ImageGeoProjection(config_path='config.yaml')
    projection.mapping()
    projection.plot()
