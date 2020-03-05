import requests
import os
from bs4 import BeautifulSoup as bs
import pprint
import json
from collections import defaultdict
import argparse
import configparser
import date_tools
import time

consumer_account_no = os.environ['ACCOUNT']

consumer_id = consumer_account_no[4:]
division_code = consumer_account_no[:3]

# Argument Parser
parser = argparse.ArgumentParser()

parser.add_argument('--register', help="Register your User/Consumer ID.")

# parser.add_argument('-r', '--range', help='A range of months between installation month and previous month(inclusive).')
# parser.add_argument('-a', '--all-data', help='')
# parser.add_argument('-m', '--month', help='A particular month')

ip_addrs = {
    "portal1": "117.239.112.120:8070",
    "portal2": "203.193.144.25:8080"
}

urls = {
    "login_page": "/ConsumerPortal/welcome.jsp", # /ConsumerPortal/welcome.jsp?link=IP_ADDR
    "login_url": "/ConsumerPortal/Record_Check?strConsID=USERNAME&OptType=Login&strDivCode=0&strConsumerType=0&strConsNo=&txtInput=LOLTCHA&image2.x=73&image2.y=14",
    "bill_details": "/ConsumerPortal/bill_s4.jsp",
    "detailed_bill_format": "/ConsumerPortal/bill_det.jsp?DIVCODE=DC&CONS_ACC=USERNAME&CESU_DATE=DD-MM-YYYY",
    "sbm_bill_format": "/ConsumerPortal/SBM_Bill_Format.jsp?DIVCODE=DC&CONS_ACC=USERNAME&CESU_DATE=DD-MM-YYYY"    
}

# Need an URL gen function?

# Check which ip_addrs is up

# captcha/loltcha generator function
# def loltcha_gen():
#     pass
welcome_url = "http://" + ip_addrs['portal1'] + urls['login_page']
print(welcome_url)
s = requests.Session()
r = s.get(welcome_url)
r = s.get("http://" + ip_addrs['portal1'] + urls["login_url"].replace("USERNAME", consumer_account_no).replace("LOLTCHA", "XVrTfz")) # SUBMIT button

#TODO check the redirect above and see if redirected to `not_found_server.jsp` or to `loginindex.jsp`.

#single request for 01-MMM-YYYY detailed_bill_format.jsp  


def install_date_finder():
    focus_date = date_tools.previous_month_string()
    r = s.get("http://" + ip_addrs['portal1'] + urls['detailed_bill_format'].replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date))
    soup = bs(r.text, 'html.parser')
    installation_date_string = soup.findAll('body > div:nth-child(2) > center:nth-child(1) > table:nth-child(3) > tr:nth-child(2) > td:nth-child(6) > div:nth-child(1) > b:nth-child(1) > font:nth-child(1).text')
    return date_tools.dt_string_to_dt_object(installation_date_string, "DD/MM/YYYY")

# installation_month
previous_month_dt_object = date_tools.previous_month()

def table_data_checker(request_data):
    # TODO
    soup = bs(request_data.text, 'html.parser')
    data_checker_dict = {
        "1": ["Consumer Information", "body > div:nth-child(2) > center:nth-child(1) > table:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > span:nth-child(1) > font:nth-child(1)"],
        "2": ["Meter Information", "body > div:nth-child(2) > center:nth-child(1) > table:nth-child(3) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > span:nth-child(1) > font:nth-child(1)"],
        "3": ["Billing Information", "body > div:nth-child(2) > center:nth-child(1) > table:nth-child(5) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > span:nth-child(1) > font:nth-child(1)"],
        "4": ["Adjustment Information", "body > div:nth-child(2) > center:nth-child(1) > table:nth-child(7) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > span:nth-child(1) > font:nth-child(1)"],
        "5": ["Payment & Arrear Information", "body > div:nth-child(2) > center:nth-child(1) > table:nth-child(9) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > span:nth-child(1) > font:nth-child(1)"]
    }
    count = 0
    for i,j in data_checker_dict.items():
        parsed_text = soup.findAll(j[1]).text
        if j[0] == parsed_text:
            count+=1
            print(i + ": " +j[0] + " = " + parsed_text)
        else:
            return False
    print("Found " + count + " of 5 table data.")
    return True
    # get request bill data
    # make soup
    # check soup for all 5 table data (create dict with {'table no.': ["CSS Selector", "Data Supposed to be contained"]})
    # for each soup print the name of table found or not found
    # if all tables are found return True else return False
    

def first_bill_month_finder():
    # TODO
    month_object = install_date_finder()
    sentinel = False
    while (sentinel == False):
        focus_date = date_tools.dt_object_to_mmm_yyyy(month_object)
        r = s.get("http://" + ip_addrs['portal1'] + urls['detailed_bill_format'].replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date))
        sentinel = table_data_checker(r)
        month_object = date_tools.next_month(month_object)
    print(focus_date)
    return date_tools.date_string_to_mmm_yyyy(focus_date, "DD-MMM-YYYY")
    # get dt_object from install_date_finder()
    # replace dt_object by day=1
    # convert 1_dt_object to MMM-YYYY
    # fetch data for that date (LOOP)
    # send data to table_data_checker() for every subsequent month until you get True (LOOP)
    # Once you hit True get the dt_object of the month that returned True
    # return a dt_object of the fill bill month

date_list = date_tools.month_range(first_bill_month_finder(), date_tools.previous_month())

# date_list = ["01-MAY-2019"]

# TODO send first_bill_finder() and previousmonth() to a function to create a generator 
    


detailed_bill_dict = defaultdict(dict)

soup_list = []
def requester(date_list):
    for focus_date in date_list:
        time.sleep(5) # TODO Add a limiter; Download all data first , store it and then call bill_dict_generator() on the stored data
        r = s.get("http://" + ip_addrs['portal1'] + urls['detailed_bill_format'].replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date))
        soup = bs(r.text, 'html.parser')
        soup_list.append(soup)

focus_date_count = 0
for soup in soup_list:
    bill_dict_generator(soup, date_list[focus_date_count])
    focus_date_count += 1

def bill_dict_generator(soup, focus_date): # TODO This will fail or present erroneous data if blank data is received from Server. 
    # Table 1 Consumer Information []
    # Table 2 Meter Information []
    # Table 3 Billing Information []
    # Table 4 Adjustment Information []
    # Table 5 Payment and Arrear Information 
    # Table 6 Remarks (Not Scraped)

    # Table 1, 2, 5 scraping format is equal
    detailed_bill_dict[focus_date] = {}
    for tableNo in [1,2,3,5]:                         #tableLoop
        table = soup.findAll('table')[tableNo]
        if tableNo == 1 or tableNo == 2 or tableNo == 5:
            for trNo in range(len(table.findAll('tr'))):  #trloop
                trow = table.findAll('tr')[trNo]
                for tdNo in range(len(trow.findAll('td'))):
                    td = trow.findAll('td')[tdNo]
                    if trNo != 0 and tdNo % 2 == 0:  # Key td: row number != 0 and even td
                        # detailed_bill_dict[focus_date][tablename][key] = ""
                        detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()][td.text.strip()] = ""

                    elif trNo == 0:                  # Tablename td: row number 0 containing the table name
                        # detailed_bill_dict[focus_date][tablename] = {}
                        detailed_bill_dict[focus_date][trow.findAll('td')[tdNo].text.strip()] = {}

                    elif trNo != 0 and tdNo % 2 != 0: # Value td: row number != 0 and td is odd
                        # detailed_bill_dict[focus_date][tablename][key] = value
                        detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()][table.findAll('tr')[trNo].findAll('td')[tdNo-1].text.strip()] = td.text.strip()
                        
        elif tableNo == 3:
            for trNo in range(len(table.findAll('tr'))): #trLoop
                trow = table.findAll('tr')[trNo]
                if trNo == 0:                        # Tablename td: row number 0 containing the table name
                    # print("\n\nTable No: " + str(tableNo) +"; Table Name: " + trow.findAll('td')[0].text.strip()) 
                    detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()] = {}

                if trNo != 0 and trNo % 2 != 0:      # row number != 0  and row number is odd; key td  = row_td; value_td = row+1_td
                    for tdNo in range(len(trow.findAll('td'))):
                        key = table.findAll('tr')[trNo].findAll('td')[tdNo].text.replace("\n", "").replace("\r", "")
                        value = table.findAll('tr')[trNo+1].findAll('td')[tdNo].text.strip()
                        key = key.strip() #.replace("\n", "")
                        # detailed_bill_dict[focus_date][tablename][value] = key
                        detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()][key] = value



requester(date_list)
pprint.pprint(detailed_bill_dict)

with open("./data/bill_data.json", "w") as write_file:
    json.dump(detailed_bill_dict, write_file)


