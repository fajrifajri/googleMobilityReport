import requests
import urllib
from urllib.request import urlopen
import wget
import os
from bs4 import BeautifulSoup

import pandas as pd 
import re
from iso3166 import countries
import plotly.express as px


from tika import parser



from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

metric = ["Retail & recreation",\
    "Grocery & pharmacy",\
    "Parks",\
    "Transit stations",\
    "Workplaces",\
    "Residential"\
    ]

data = []

def get_pdf():
    url = "https://www.google.com/covid19/mobility/"
    result = requests.get(url, verify=False)\
    
    soup = BeautifulSoup(result.text, "html.parser")
    country_data = soup.find_all('div', class_='country-data')
    
    # Country Dat
    for i in country_data:
        pdf_url = i.findAll('a', {'class': 'download-link'})[0]['href']
        wget.download(pdf_url, "google/")
    
    # US Data
    us_data = soup.find_all('div', class_='region-data')
    for i in us_data:
        pdf_url = i.findAll('a', {'class': 'download-link'})[0]['href']
        wget.download(pdf_url, "google/")

def process_pdf(location):
    #FIPS Data https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697
    fips_data = pd.read_csv('state_county_fips.csv',names=['state','county','fips'], engine='python')

    for file in os.listdir("google/"):
        if file.endswith(".pdf"):
            filename = "google/" +file
            country = file.split("_")[1]
            if location == "US":
                if country == "US" and file.split("_")[2] != "Mobility":
                
                    state = re.findall(r"US_(\w+?)_Mobility_",file)[0].replace("_", " ")
                    rawText = parser.from_file(filename)
                    rawList = rawText['content'].splitlines()
                    loc = []  
                    b = 0            
                    for i in rawList:
                        b+=1
                        if i == "Retail & recreation":
                            loc.append(b)

                    for i in range(1,len(loc)):
                        temp = []
                        temp.append("USA")
                        temp.append(state)
                    
                        county = rawList[loc[i]-3]
                        temp.append(county)
                        try:
                            fips = fips_data[fips_data.state.str.contains(state) & fips_data.county.str.contains(county)]['fips'].values
                            temp.append(str(fips[0]))
                        except (IndexError, ValueError, TypeError) as e:
                            temp.append(0)

                        try:
                            retail  = rawList[loc[i]+1].split(' ')[0]
                            temp.append(retail)
                        except (IndexError, ValueError) as e:
                            temp.append(0)
                        try:
                            grocery  = rawList[loc[i]+5].split(' ')[0]
                            temp.append(grocery)
                        except (IndexError, ValueError) as e:
                            temp.append(0)
                        try:
                            park  = rawList[loc[i]+9].split(' ')[0]
                            temp.append(park)
                        except (IndexError, ValueError) as e:
                            temp.append(0)
                        try:
                            transit  = rawList[loc[i]+13].split(' ')[0]
                            temp.append(transit)
                        except (IndexError, ValueError) as e:
                            temp.append(0)
                        try:
                            workplace  = rawList[loc[i]+17].split(' ')[0]
                            temp.append(workplace)
                        except (IndexError, ValueError) as e:
                            temp.append(0)
                        try:
                            residential  = rawList[loc[i]+21].split(' ')[0]
                            temp.append(residential)
                        except (IndexError, ValueError) as e:
                            temp.append(0)

                        data.append(temp)

            else:        
                if file.split("_")[2] == "Mobility":
                    temp = []
                    country = countries.get(country).alpha3
                    rawText = parser.from_file(filename)
                    rawList = rawText['content'].splitlines()

                    temp.append(country)
                    temp.append(country)
                    temp.append("")
                    temp.append(country)
                    for i in metric:
                        try:
                            temp.append(rawList[2+rawList.index(i)])
                        except ValueError:
                            temp.append(0)
                    data.append(temp)


def generate_maps(metric):

    fig = px.choropleth(df, locations="Country", color=metric,
                    color_continuous_scale=px.colors.diverging.BrBG,
                    color_continuous_midpoint=0,
                    title="Google Mobility Report - " + metric) 
    fig.show()

if __name__ == "__main__":
    #get_pdf()
    process_pdf("World")
    df = pd.DataFrame(data, columns=['Country','state','county','fips','Retail & recreation','Grocery & pharmacy','Parks','Transit stations','Workplaces','Residential']).fillna(0)
    
    for i in metric:
        generate_maps(i)


     