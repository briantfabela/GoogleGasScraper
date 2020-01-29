# Python 3.7.1 - Briant J. Fabela (12/26/2019)

from selenium import webdriver # selenium v3.141.0

# for 'explicit' wait implementation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# tests
import os

from helpfuncs import GasStationScraper

gas_txt_path = os.path.normpath('fuel_prices\85364\_gas_stations_85364.txt')
zipcode = '85364'

gss = GasStationScraper(gas_txt_path, zipcode, 20)
gss.scrape_results()

'''
for zipcode in ['85364']:
    make_file_structure(zipcode)

helpfuncs.create_csv('fuel_prices/92231', 'diesel.csv')

headers = ['timestamp', 'Chevron 123 Main Street']
body  = ['01/01/2020', '3.49']

with open('fuel_prices/92231/diesel.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for row in [headers, body]:
        csv_writer.writerow(row)
'''