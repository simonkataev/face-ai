import os
import time
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim

from commons.common import Common
from commons.metadata_detail import MetadataDetail


class GetImageMetadata:

    def __init__(self):
        self.address = None
        self.lon = None
        self.lat = None
        self.tags = []
        self.values = []
        self.metadata_detail = MetadataDetail()

    def get_exif_data(self, image):
        """Extracts EXIF data from the given image file."""
        exif_data = {}
        try:
            with Image.open(image) as img:
                info = img._getexif()
                self.metadata_detail.width, self.metadata_detail.height = img.size
                self.metadata_detail.type = img.format
                dpi_info = img.info.get("dpi")
                if dpi_info is not None:
                    if len(dpi_info) == 2:
                        self.metadata_detail.XResolution = int(round(dpi_info[0], 0))
                        self.metadata_detail.YResolution = int(round(dpi_info[1], 0))
                mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime = os.stat(image)
                print(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)

                created = datetime.strptime(time.ctime(ctime), "%a %b %d %H:%M:%S %Y")
                self.metadata_detail.processed_time = created.strftime("%d/%m/%Y %I:%M %p")
                self.metadata_detail.fsize = str(round(size / 1024, 2)) + "KB"
                if info is not None:
                    for tag, value in info.items():
                        decoded_tag = TAGS.get(tag, tag)
                        if decoded_tag == 'GPSInfo':
                            gps_data = {}
                            for gps_tag in value:
                                sub_decoded_tag = GPSTAGS.get(gps_tag, gps_tag)
                                gps_data[sub_decoded_tag] = value[gps_tag]
                            exif_data[decoded_tag] = gps_data
                        else:
                            exif_data[decoded_tag] = value
                info_for_device = img.getexif()
                if info_for_device is not None:
                    for tag, value in info_for_device.items():
                        decoded_tag = TAGS.get(tag, tag)
                        if decoded_tag == 'Model':
                            self.metadata_detail.device = value
        except (IOError, AttributeError, KeyError, IndexError) as err:
            print("Error: ", err)
        return exif_data

    def print_exif_data(self, exif_data):
        for tag, value in exif_data.items():
            print(f"{tag}: {value}")
            self.tags.append(tag)
            self.values.append(value)
        # if exif_data.get("XResolution") is not None:
        #     self.metadata_detail.XResolution = str(exif_data.get("XResolution"))
        #
        # if exif_data.get("YResolution") is not None:
        #     self.metadata_detail.YResolution = str(exif_data.get("YResolution"))
        #
        # if exif_data.get("ExifImageHeight") is not None:
        #     self.metadata_detail.height = exif_data.get("ExifImageHeight")[0]
        #
        # if exif_data.get("ExifImageWidth") is not None:
        #     self.metadata_detail.width = exif_data.get("ExifImageWidth")[0]

    def dms_to_decimal(self, degrees, minutes, seconds, direction):
        """Converts GPS coordinates in degrees, minutes, and seconds format to decimal degrees."""
        decimal_degrees = float(degrees) + (float(minutes) / 60) + (float(seconds) / 3600)
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        return decimal_degrees

    def get_location_address(self, exif_data):
        geolocator = Nominatim(user_agent="metadata/1.0")
        if self.tags.count("GPSInfo"):
            if exif_data["GPSInfo"] is not None:
                lat_deg, lat_min, lat_sec = exif_data["GPSInfo"]["GPSLatitude"]
                lat_dir = exif_data["GPSInfo"]["GPSLatitudeRef"]
                lon_deg, lon_min, lon_sec = exif_data["GPSInfo"]["GPSLongitude"]
                lon_dir = exif_data["GPSInfo"]["GPSLongitudeRef"]

                self.lat = self.dms_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
                self.lon = self.dms_to_decimal(lon_deg, lon_min, lon_sec, lon_dir)
                self.metadata_detail.longitude = "%.5f" % self.lon
                self.metadata_detail.latitude = "%.5f" % self.lat
                try:
                    location = geolocator.reverse(f"{self.lat}, {self.lon}")
                    self.metadata_detail.street = location.address
                    print("Location Address: ", location.address)
                except Exception as ex:
                    print(ex)

    def get_metadata(self, img_path):
        self.tags.clear()
        self.values.clear()
        self.metadata_detail = MetadataDetail()
        exif_data = self.get_exif_data(img_path)
        # self.metadata_detail.type = Common.get_file_extension_from_path(img_path)
        self.print_exif_data(exif_data)
        self.get_location_address(exif_data)
        return self.metadata_detail
