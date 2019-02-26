import datetime
import geopy.point

class GPSStamp:
    def __init__(self, GPS_stamp):
        all_values = GPS_stamp.split(",")
        # Pick up all the individual fields
        if len(all_values) > 0:
            self.type = all_values[0]
            self.time = all_values[1]
            self.latitude_base = all_values[3]
            self.latitude_zone = all_values[4]
            self.latitude_decimal = self.get_cleaned_latitude_longitude(
                self.latitude_base, self.latitude_zone)
            self.longitude_base = all_values[5]
            self.longitude_zone = all_values[6]
            self.longitude_decimal = self.get_cleaned_latitude_longitude(
                self.longitude_base, self.longitude_zone)
            self.speed_in_knots = float(all_values[7])
            self.speed_in_mph = self.speed_in_knots * 1.151
            self.tracking_angle = all_values[8]
            self.date = all_values[9]

            # This is used to identify errors
            if self.date.__contains__("\n"):
                # TODO: Find a cleaner way to fix this
                self.date = "101018"

            # make a datetime object so that time subtraction is done with ease
            self.date_time = datetime.datetime(int(str(20) + self.date[4:6]),
                                           int(self.date[2:4]),
                                           int(self.date[0:2]),
                                           int(self.time[0:2]),
                                           int(self.time[2:4]),
                                           int(self.time[4:6]))
            # Make a Point from Latitude and Longitude
            # This will make finding distance between points easier
            self.point = geopy.Point(self.latitude_decimal,
                                     self.longitude_decimal)

    def get_cleaned_latitude_longitude(self, base, zone):
        '''

        :param base: The Numbers for latitude or longitude
        :param zone: The Zone for latitude or longitude
        :return: Numeric Latitude or Longitude
        '''

        # This is used to break the values in the right place
        # This changes for latitude and longitude
        break_spot = 0
        if zone == "N" or zone == "S":
            # Latitude Value
            break_spot = 2
        elif zone == "E" or zone == "W":
            # Longitude Value
            break_spot = 3

        degrees = int(base[0:break_spot])
        minutes = float(base[break_spot:])
        value = degrees + (minutes/60)

        if zone == "S" or zone == "W":
            value = -1 * value

        return value
