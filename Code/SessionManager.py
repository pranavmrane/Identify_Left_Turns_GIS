
from Code.GPSStamp import GPSStamp
from Code.GPSSession import GPSSession
import os


class SessionManager:

    def __init__(self):
        pass

    def import_session(self, storage_folder, file_name):
        '''
        Determine all the lines(GPS Points) to be selected for a path
        :param storage_folder: The folder where .txts can be found for import
        :param file_name: The name of file to be imported
        :return: Object for particular GPS Point
        '''
        # Generate Address for .txt file
        address = storage_folder + str(os.sep) + file_name

        with open(address) as f:
            gps_stamp_details = []
            loop_count = 0
            for line in f:
                loop_count = loop_count + 1
                # if loop_count == 200:
                #     break

                # Conditions for reading line are specified
                # a line that contains ,,,, is unreadable
                if not(line.__contains__("$GPGGA")) \
                        and line.__contains__("$GPRMC") \
                        and not(line.__contains__(",,,,")):
                    gps_stamp_details.append(line)
        f.close()

        return gps_stamp_details

    def make_each_object(self, gps_stamps, gps_session_object):
        '''
        Initialize every line as an an object
        :param gps_stamps: list of GPS points whose objects will be made
        :param gps_session_object: This is the path object which is being updated
        :return:
        '''

        for gps_stamp in gps_stamps:
            gps_stamp_object = GPSStamp(gps_stamp)
            gps_session_object.add_values(gps_stamp_object)

        return gps_session_object

    def get_txt_filenames(self, txt_input_address):
        '''
        :param txt_input_address: Address where txt files can be found
        :return: Names of .txt files found in provided location
        '''
        txt_files = list()

        # Choose all filenames from a folder
        for root, dirs, files in os.walk(txt_input_address):
            for filename in files:
                txt_files.append(filename)
        return txt_files

    def generate_kml_file(self, txt_files, txt_input_address,
                          KML_store_address):
        '''
        All Lines in a Path are initialized as GPS Point Objects
        All GPS Points are used to define a Path
        Multiple paths and their comparisons are defined a session
        :param txt_files: Contains names of txt files which contain GPS data
        :param txt_input_address: Txt files location folder
        :param KML_store_address: Folder where kml file will be saved
        :return:
        '''
        # List of GPS Path Objects
        gps_session_object_list = list()
        # List of GPS Path Score
        gps_session_score_list = list()

        # Initialize Objects and add to list
        for filename in txt_files:
            gps_session_object = GPSSession(KML_store_address, filename)
            gps_session_object_list.append(gps_session_object)

        loop_count = 0
        # This will contain all stop points for all the paths
        complete_stop_set = set()
        left_turn_list_list = list()

        # For every path
        for gps_session_object in gps_session_object_list:
            # print(gps_session_object.KML_name)
            loop_count = loop_count + 1
            # if loop_count == 2:
            #     break

            # Get list of lines(GPS Points) to be accepted into the path
            session_gps_stamp_details = self.import_session(txt_input_address,
                                        gps_session_object.KML_name)
            # Initialize all Points as Objects
            gps_session_object = self.make_each_object(
                session_gps_stamp_details, gps_session_object)
            # Remove Redundant Points
            gps_session_object.remove_redundant_points()
            # Get Cleaned List of Left Turns
            left_turn_list_list.append(gps_session_object.generate_left_turn_list())
            # print(gps_session_object.generate_left_turn_list)
            # Take A union of all old Stop Points with new Stop Points
            complete_stop_set = complete_stop_set.union(gps_session_object.
                                                        identify_stop_signs())
            # Save Score List
            gps_session_score_list.append(gps_session_object.generate_cost())

        # Choose index for minimum score path
        min_index = gps_session_score_list.index(min(gps_session_score_list))
        print("Best Route", gps_session_object_list[min_index].KML_name)

        # print(left_turn_list_list[0])
        count = 0
        for gps_session_object in gps_session_object_list:
            # Make KML File with Minimum Path and all stop points
            gps_session_object.generate_KML_file(complete_stop_set,
                                                 left_turn_list_list[count])
            count = count + 1
