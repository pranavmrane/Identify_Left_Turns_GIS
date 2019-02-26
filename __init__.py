from Code.SessionManager import SessionManager

txt_input_address = input("Enter the location for KML files directory\n")

# txt_input_address = "/home/pranavmrane/PycharmProjects/" \
#                     "GPS_interpretation_and_optimzation/DataResource"

KML_store_address = input("Enter the location where KML files can be stored\n")
# KML_store_address = "/home/pranavmrane/PycharmProjects/" \
#                     "GPS_interpretation_and_optimzation/GeneratedKMLFile"

session_object = SessionManager()
txt_files = session_object.get_txt_filenames(txt_input_address)
session_object.generate_kml_file(txt_files, txt_input_address, KML_store_address)

'''
Enter the location for KML files directory
/home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/DataResource
Enter the location where KML files can be stored
/home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile
Best Route ZIAA_CTU_2018_10_10_1255.txt
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZIAB_CIU_2018_10_11_1218.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZI8N_DG8_2018_08_23_1316.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZI8G_ERF_2018_08_16_1428.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZI8H_HJC_2018_08_17_1745.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZIAC_CO0_2018_10_12_1250.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZI8K_EV7_2018_08_20_1500.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZIAA_CTU_2018_10_10_1255.txt.kml Generated here
KML File: /home/pranavmrane/PycharmProjects/GPS_interpretation_and_optimzation/GeneratedKMLFile/ZI8J_GKX_2018_08_19_1646.txt.kml Generated here
'''