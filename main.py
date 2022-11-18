import requests
import json
import pandas as pd
import streamlit as st
import time


class report_accident():
    def __init__(self):
        self.LATITUDE = 0
        self.LONGITUDE = 0
        self.url = "https://api.unl.global/v2/search"
        self.headers = {
            "x-unl-api-key": "VxiVKFXh0W80qWBvmNTBwya5bBWpnrnQ",
            "x-unl-vpm-id": "547b37f7-fef8-4e9e-b22b-0a7689276245",
        }

    def accept_location(self, ADDRESS):
        self.parameters = {
            "query": ADDRESS,
            "language": "en",
            "limit": 1,
            "country": "US",
            "sort_by": "distance"
        }

        self.response = requests.get(f"{self.url}", params=self.parameters, headers=self.headers)
        if self.response.status_code == 200:
            self.response = self.response.json()
            Features = json.loads((json.dumps(self.response["geojson:Features"])[1:-1]))
            Geometry = json.loads(json.dumps(Features['geojson:geometry']))
            self.LATITUDE = Geometry["coordinates"][1]
            self.LONGITUDE = Geometry["coordinates"][0]

            return self.LATITUDE, self.LONGITUDE


class emergency():
    def __init__(self):
        self.df_policeStation = pd.read_csv("police-stations.csv")
        self.df_fireStation = pd.read_csv("Fire_Stations.csv")
        self.TARGET_LATITUDE = 0
        self.TARGET_LONGITUDE = 0
        self.DISTANCES_PS = []
        self.DISTANCES_FS = []
        self.LATITUDE_FS = []
        self.LONGITUDE_FS = []
        self.url = 'https://api.unl.global/v1/routing?format=coordinates'
        self.headers = {
            'accept': 'application/json',
            "x-unl-api-key": "VxiVKFXh0W80qWBvmNTBwya5bBWpnrnQ",
            "x-unl-vpm-id": "547b37f7-fef8-4e9e-b22b-0a7689276245",
            "Content-Type": "application/json",
        }

    def loading_loations_PS(self, ADDRESS):
        xyz = report_accident()
        self.TARGET_LATITUDE, self.TARGET_LONGITUDE = xyz.accept_location(ADDRESS)

        for i in range(len(self.df_policeStation['LATITUDE'])):
            latitude_ps = self.df_policeStation['LATITUDE'][i]
            longitude_ps = self.df_policeStation['LONGITUDE'][i]
            self.DISTANCES_PS.append(
                pow((self.TARGET_LATITUDE - latitude_ps), 2) + pow((self.TARGET_LONGITUDE - longitude_ps), 2))

        self.newdf_policeStation = self.df_policeStation
        self.newdf_policeStation['DISTANCES'] = self.DISTANCES_PS

        self.newdf_policeStation = self.newdf_policeStation[
            ['DISTRICT NAME', 'ADDRESS', 'LATITUDE', 'LONGITUDE', 'DISTANCES']].sort_values(by=['DISTANCES']).head(5)

    def loading_locations_FS(self, ADDRESS):
        xyz = report_accident()
        self.TARGET_LATITUDE, self.TARGET_LONGITUDE = xyz.accept_location(ADDRESS)
        for i in self.df_fireStation['ADDRESS']:
            xx = report_accident()
            latitude, longitude = xx.accept_location(i)
            self.LATITUDE_FS.append(latitude)
            self.LONGITUDE_FS.append(longitude)
            self.DISTANCES_FS.append(
                pow((self.TARGET_LATITUDE - latitude), 2) + pow((self.TARGET_LONGITUDE - longitude), 2))

        self.newdf_fireStation = self.df_fireStation
        self.newdf_fireStation['LATITUDE'] = self.LATITUDE_FS
        self.newdf_fireStation['LONGITUDE'] = self.LONGITUDE_FS
        self.newdf_fireStation['DISTANCES'] = self.DISTANCES_FS

        self.newdf_fireStation = self.newdf_fireStation[
            ['NAME', 'ADDRESS', 'LATITUDE', 'LONGITUDE', 'DISTANCES']].sort_values(by=['DISTANCES']).head(5)

    def routing_PoliceStation(self):
        self.requestBody = {
            "mode": "fast",
            "waypoints": [
                {
                    "type": "point",
                    "coordinates": str(self.newdf_policeStation['LONGITUDE'][0]) + ', ' + str(
                        self.newdf_policeStation['LATITUDE'][0])
                },
                {
                    "type": "point",
                    "coordinates": str(self.TARGET_LONGITUDE) + ", " + str(self.TARGET_LATITUDE)
                }
            ]
        }

        self.response = requests.post(url=self.url, headers=self.headers,
                                      json=self.requestBody)
        return self.response.text, self.newdf_policeStation['DISTRICT NAME'][0]

    def routing_FireStation(self):
        self.requestBody = {
            "mode": "fast",
            "waypoints": [
                {
                    "type": "point",
                    "coordinates": str(self.newdf_fireStation['LONGITUDE'][0]) + ', ' + str(
                        self.newdf_fireStation['LATITUDE'][0])
                },
                {
                    "type": "point",
                    "coordinates": str(self.TARGET_LONGITUDE) + ", " + str(self.TARGET_LATITUDE)
                }
            ]
        }

        self.response = requests.post(url=self.url, headers=self.headers,
                                      json=self.requestBody)
        return self.response.text


# ADDRESS = input("Enter the Address (In Chicago City): ")
# x = emergency()
# x.loading_loations_PS(ADDRESS)
# x.routing_PoliceStation()

st.title("Emergency Routing")
with st.form("my_form1"):
    st.write("POLICE STATION ROUTE")
    address1 = st.text_input("Enter Address")
    dict1 = {}

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        x = emergency()
        x.loading_loations_PS(address1)
        dict1, name = x.routing_PoliceStation()
        dict1_json = json.loads(dict1)
        response_segments = dict1_json["segments"]

        response_name = dict1_json["name"]
        response_overview = dict1_json["overview"]
        response_length = response_overview["length"]/1000
        response_duration = response_overview["duration"]/60

        response_segment_length = len(dict1_json["segments"])
        text_collection = []

        for i in range(response_segment_length):
            temp_x = response_segments[i]
            text_collection.append(temp_x["text"])

        st.write("1) The Shortest route the ", name, " PD can take to reach the place of emergency is: ", response_name)
        st.write("2) Mode of Transport is: Car")
        st.write("3) The Distance that needs to be covered is: ", response_length, "KM")
        st.write("4) The Time needed to reach the place of Emergency is: ", response_duration,"Min")
        st.write("5) Instructions: ",text_collection)



with st.form("my_form2"):
    st.write("FIRE STATION ROUTE")
    address2 = st.text_input("Enter Address")
    dict2 = {}

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        y = emergency()
        y.loading_locations_FS(address2)
        dict2 = y.routing_FireStation()
        st.write("address: ", dict2)
