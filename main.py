# Python 3.7.1 - Briant J. Fabela (12/26/2019)

from selenium import webdriver # selenium v3.141.0

# for 'explicit' wait implementation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# tests
from helpfuncs import create_csv
import csv
import os

def make_file_structure(zipcode):
    """
    Generates a file structure and csv files for fuel types to store price info

    Does not provide validation that the zipcode exists.
    
    Args:
        zipcode (str): 5-digit number string of a valid U.S. zip code
    """

    # create 'fuelprices/{zipcode} along with fueltype csv files, with headers'
    path = os.path.join('fuel_prices', zipcode)

    for fuel_type in ['diesel', 'regular', 'midgrade', 'premium']:
        create_csv(path, fuel_type+'.csv')

for zipcode in ['92231', '85364', '85365', '10082', '01234']:
    make_file_structure(zipcode)

'''
helpfuncs.create_csv('fuel_prices/92231', 'diesel.csv')

headers = ['timestamp', 'Chevron 123 Main Street']
body  = ['01/01/2020', '3.49']

with open('fuel_prices/92231/diesel.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for row in [headers, body]:
        csv_writer.writerow(row)
'''