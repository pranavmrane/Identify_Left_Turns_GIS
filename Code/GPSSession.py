import geopy.distance
import os
import math

class GPSSession:
    def __init__(self, KML_storage_address, name):
        '''
        Declare variables required for class
        :param KML_storage_address: The location where KML file will be saved
        :param name: name of .txt file which will be duplicated for KML file
        '''
        self.gps_path_list = list()
        self.gps_path_list_cleaned = list()
        self.stop_locations = list()
        self.KML_storage_address = KML_storage_address
        self.KML_name = name

    def add_values(self, gps_path_object):
        '''
        Save GPS points in list
        :param gps_path_object: GPS Path Object to be saved in GPS Path List
        :return: NULL
        '''
        self.gps_path_list.append(gps_path_object)

    def get_size(self):
        '''
        :return: Return the count of all the GPS points added to the path
        '''
        return len(self.gps_path_list)

    def remove_redundant_points(self):
        '''
        Remove Redundant points from gps_path_list. New List will be made.
        :return:
        '''
        # Initialize to ensure list is empty at beginning
        self.stop_locations = list()
        # Save the 1st point
        original_point = self.gps_path_list[0].point
        for i in range(1, (self.get_size() - 1)):
            # Find the points that less than 0.5 meters away from 1st point
            if (geopy.distance.VincentyDistance(original_point,
                                        self.gps_path_list[i].point).km *
                    1000 < 0.5):
                # The points that within the 0.5 meters range will be removed
                # The index of such points will be recorded to be removed later
                self.stop_locations.append(i)
            else:
                # New Point is 0.5 meters away from the 1st point
                # Original Point updated here
                original_point = self.gps_path_list[i].point
        # Remove all Points in very close proximity
        self.remove_stops()

    def remove_stops(self):
        '''
        Remove stops that are very close to each other.
        :return:
        '''
        # Cleaned List is Free of Redundant Points
        self.gps_path_list_cleaned = list()
        self.gps_path_list_cleaned = self.gps_path_list.copy()

        for index in sorted(self.stop_locations, reverse=True):
            del self.gps_path_list_cleaned[index]

    def get_max_speed(self):
        '''
        Get Max Speed Attained on the route
        :return: Max Speed in Miles Per Hour
        '''

        if len(self.gps_path_list_cleaned) != 0:
            max_speed_in_mph = 0
            for i in self.gps_path_list_cleaned:
                if i.speed_in_mph > max_speed_in_mph:
                    max_speed_in_mph = i.speed_in_mph

            return max_speed_in_mph
        else:
            print("Please Clean File First")
            return 0

    def get_travel_time(self):
        '''
        :return: Total Time elapsed between trip start and trip end
        '''

        # We use the original list with redundant points as it more accurate
        # to specify time
        if len(self.gps_path_list) != 0:
            return ((self.gps_path_list[-1].date_time -
                     self.gps_path_list[0].date_time).seconds/60)
        else:
            print("File Empty Somehow, more investigation required")
            return 0

    def generate_cost(self):
        '''
        :return: Return cost for the trip expressed with travel time and
        max speed as variables
        '''
        return (self.get_travel_time() / 30) + \
               (0.5 * (self.get_max_speed()/60))

    def identify_stop_signs(self):
        '''
        This identifies all the gps points where car abruptly slows down
        :return: Stop points stored in a set
        '''
        # Stops for this Trip
        stop_set_data = set()
        # This will hold the 5 most recent values before the current value
        latest_speed_list = list()
        for i in self.gps_path_list_cleaned:
            # Ensure the count of elements stays 5
            if len(latest_speed_list) < 5:
                latest_speed_list.append(i.speed_in_mph)
            else:
                # Checkif current speed is less than 40% of average last5speeds
                # This means car has reduced speed
                # All speeds below 0.1 MPH are also dropped
                # After some trial and error, the numbers of 40% and 0.1 MPH
                # were chosen
                if ((i.speed_in_mph <
                     0.4*(sum(latest_speed_list)/len(latest_speed_list)))
                        and (i.speed_in_mph > 0.1)):
                    # There are a lot of values generated
                    # To crowding at certain spots only precision 4 is retained
                    # Basically we dont want two points which are 5.5555 and
                    #  5.55555
                    # We just want one point of 5.5555
                    generated_string = str(round(i.longitude_decimal, 4)) + \
                                       "," + str(round(i.latitude_decimal, 4))
                    stop_set_data.add(generated_string)
                # Delete first element from list
                del latest_speed_list[0]
                # Add the newest value
                latest_speed_list.append(i.speed_in_mph)
        return stop_set_data

    def get_angle_between_points(self, lat1, long1, lat2, long2):

        delta_phi = math.log(math.tan(lat2/2 + math.pi/4) /
                             math.tan(lat1/2 + math.pi/4))
        delta_lon = abs(long1 - long2)
        bearing = math.atan2(delta_lon, delta_phi) * (180/math.pi)
        return bearing

    def generate_left_turn_list(self):
        left_turn_indexes = list()

        for i in range(0, len(self.gps_path_list_cleaned)-1):
            value = self.get_angle_between_points(
                    self.gps_path_list_cleaned[i].latitude_decimal,
                    self.gps_path_list_cleaned[i].longitude_decimal,
                self.gps_path_list_cleaned[i+1].latitude_decimal,
                    self.gps_path_list_cleaned[i + 1].longitude_decimal)
            if value >30 and value<75:
                left_turn_indexes.append(i)

        discarded_indices = list()

        original_time = self.gps_path_list_cleaned[left_turn_indexes[0]].\
            date_time

        for i in range(1, len(left_turn_indexes) - 1):
            if(original_time -
               self.gps_path_list_cleaned[left_turn_indexes[i+1]].date_time).\
                    seconds < 60:
                discarded_indices.append(left_turn_indexes[i])
            else:
                original_time = \
                    self.gps_path_list_cleaned[left_turn_indexes[i]].date_time

        for discarded_index in discarded_indices:
            left_turn_indexes.remove(discarded_index)

        left_turn_coordinate_list = list()

        for left_turn_index in left_turn_indexes:
            generated_string = str(round(self.gps_path_list_cleaned
                                         [left_turn_index].longitude_decimal,
                                         6)) + \
                               "," + str(round(self.gps_path_list_cleaned
                                         [left_turn_index].latitude_decimal,
                                         6))
            left_turn_coordinate_list.append(generated_string)

        return left_turn_coordinate_list

    def generate_KML_file(self, stop_points, left_turns):
        '''
        Make a KML File
        :param stop_points: This is all the stop points from all the paths
        :return:
        '''
        filename = self.KML_name + '.kml'
        address = self.KML_storage_address + str(os.sep) + self.KML_name \
                  + ".kml"
        KMLfile = open(address, 'w')
        # Writing the kml file.
        KMLfile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        KMLfile.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
        KMLfile.write("\t<Document>\n")
        KMLfile.write("\t\t<name>" + filename + '.kml' + "</name>\n")
        KMLfile.write("\t\t<Style id='yellowLineGreenPoly'>\n")
        KMLfile.write("\t\t\t<LineStyle>\n")
        KMLfile.write("\t\t\t\t<color>7f00ffff</color>\n")
        KMLfile.write("\t\t\t\t<width>4</width>\n")
        KMLfile.write("\t\t\t</LineStyle>\n")
        KMLfile.write("\t\t\t<PolyStyle>\n")
        KMLfile.write("\t\t\t\t<color>7f00ff00</color>\n")
        KMLfile.write("\t\t\t</PolyStyle>\n")
        KMLfile.write("\t\t</Style>\n")
        KMLfile.write("\t\t<Placemark>\n")
        KMLfile.write("\t\t\t<name>Travel Points</name>\n")
        KMLfile.write("\t\t\t<styleUrl>#yellowLineGreenPoly</styleUrl>\n")
        KMLfile.write("\t\t\t<LineString>\n")
        KMLfile.write("\t\t\t\t<extrude>1</extrude>\n")
        KMLfile.write("\t\t\t\t<tessellate>1</tessellate>\n")
        KMLfile.write("\t\t\t\t<coordinates>\n")
        # Every Co-ordinate for this path is added here
        for row in self.gps_path_list_cleaned:
            KMLfile.write("\t\t\t\t" + str(row.longitude_decimal) + "," +
                          str(row.latitude_decimal) + "\n")
        KMLfile.write("\t\t\t\t</coordinates>\n")
        KMLfile.write("\t\t\t</LineString>\n")
        KMLfile.write("\t\t</Placemark>\n")

        KMLfile.write("\t\t<Style id='stop_location'>\n")
        KMLfile.write("\t\t\t<IconStyle>\n")
        KMLfile.write("\t\t\t\t<Icon>\n")
        KMLfile.write("\t\t\t\t\t<href>http://maps.google.com/mapfiles/kml/"
                      "pushpin/red-pushpin.png</href>\n")
        KMLfile.write("\t\t\t\t</Icon>\n")
        KMLfile.write("\t\t\t</IconStyle>\n")
        KMLfile.write("\t\t</Style>\n")

        # All Stop Points from all stop paths are added here
        for value in stop_points:
            KMLfile.write("\t\t<Placemark id='stop_location'>\n")
            KMLfile.write("\t\t\t<styleUrl>#stop_location</styleUrl>\n")
            KMLfile.write("\t\t\t<Point>\n")
            KMLfile.write("\t\t\t\t<coordinates>\n")
            KMLfile.write("\t\t\t\t" + value + "\n")
            KMLfile.write("\t\t\t\t</coordinates>\n")
            KMLfile.write("\t\t\t</Point>\n")
            KMLfile.write("\t\t</Placemark>\n")

        KMLfile.write("\t\t<Style id='left_turn'>\n")
        KMLfile.write("\t\t\t<IconStyle>\n")
        KMLfile.write("\t\t\t\t<Icon>\n")
        KMLfile.write(
            "\t\t\t\t\t<href>http://maps.google.com/mapfiles/kml/"
            "pushpin/yellow-pushpin.png</href>\n")
        KMLfile.write("\t\t\t\t</Icon>\n")
        KMLfile.write("\t\t\t</IconStyle>\n")
        KMLfile.write("\t\t</Style>\n")

        # Cleaned Left Turns
        for value in left_turns:
            KMLfile.write("\t\t<Placemark id='left_turn'>\n")
            #KMLfile.write("\t\t\t<styleUrl>#left_turn</styleUrl>\n")
            KMLfile.write("\t\t\t<Point>\n")
            KMLfile.write("\t\t\t\t<coordinates>\n")
            KMLfile.write("\t\t\t\t" + value + "\n")
            KMLfile.write("\t\t\t\t</coordinates>\n")
            KMLfile.write("\t\t\t</Point>\n")
            KMLfile.write("\t\t</Placemark>\n")

        KMLfile.write("</Document>\n")
        KMLfile.write("</kml>\n")
        KMLfile.close()
        print("KML File:", address, "Generated here")

