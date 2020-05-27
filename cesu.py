import requests, os, argparse, configparser, date_tools, json, pprint, time, string, random
from bs4 import BeautifulSoup as bs
from collections import defaultdict
from constants import (CESU_CONSUMER_PORTAL_1, 
                        CESU_CONSUMER_PORTAL_2,
                        LOGIN_PAGE,
                        LOGIN_URL,
                        BILL_DETAILS,
                        DETAILED_BILL_URL,
                        SBM_BILL_URL)

consumer_account_no = os.environ['ACCOUNT']
consumer_id = consumer_account_no[4:]
division_code = consumer_account_no[:3]

def basic_config_creator(account):
    config = configparser.ConfigParser()
    config['BASIC']['CESU Consumer Account No.'] = account
    with open('cesu.ini', 'w') as configfile: #constants.CONFIG_FILEPATH
        config.write(configfile)


def scraper(url):
    pass

def url_maker(): 
    pass



# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument('--register', help="Register your User/Consumer ID.")
parser.add_argument('-r', '--range', help='A range of months between installation month and previous month(inclusive).')
parser.add_argument('-a', '--all-data', help='')
parser.add_argument('-m', '--month', help='A particular month')


# Need an URL gen function?

# Check which ip_addrs is up

# captcha/loltcha generator function
def old_loltcha_gen():
    letters = string.ascii_uppercase + string.ascii_lowercase
    old_loltcha = ''
    for i in range(6):
        old_loltcha += random.choice(letters)
    return old_loltcha


welcome_url = "http://" + CESU_CONSUMER_PORTAL_1 + LOGIN_PAGE
print(welcome_url)
s = requests.Session()
r = s.get(welcome_url)
loltcha = old_loltcha_gen()
r = s.get("http://" + CESU_CONSUMER_PORTAL_1 + LOGIN_URL.replace("USERNAME", consumer_account_no).replace("LOLTCHA", loltcha)) # SUBMIT button

#TODO check the redirect above and see if redirected to `not_found_server.jsp` or to `loginindex.jsp`.

#single request for 01-MMM-YYYY detailed_bill_format.jsp  


def install_date_finder():
    # Arguments: None
    # Function: Returns the installation date of the meter as a dt_object from the bill_det page (Fetches the latest available bill_det page for this.)
    # Returns: dt_object
    focus_date = date_tools.previous_month_string() # TODO If the current month's bill hasn't been generated then the previous month bill won't be available on detailed_bill
    print("focus date in install_date_finder",focus_date)
    r = s.get("http://" + CESU_CONSUMER_PORTAL_1 + DETAILED_BILL_URL.replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date)) 
    soup = bs(r.text, 'html.parser') # TODO This soup needs checking by table data checker; if data is not found then previous to previous month data needs to be fetched.
    installation_date_string = soup.select('body > div:nth-child(2) > center:nth-child(1) > table:nth-child(3) > tr:nth-child(2) > td:nth-child(6) > div:nth-child(1) > b:nth-child(1) > font:nth-child(1)')[0].text.strip()
    print("installation_date_sting in install_date_finder",installation_date_string)
    installation_dt_object = date_tools.dt_string_to_dt_object(installation_date_string, "DD/MM/YYYY")
    return installation_dt_object

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
        "5": ["Payment & Arrear  Information", "body > div:nth-child(2) > center:nth-child(1) > table:nth-child(9) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > span:nth-child(1) > font:nth-child(1)"]
    }
    elements = [i[0] for i in data_checker_dict.values()]
    matched_elements = []
    for i,j in data_checker_dict.items():
        expected_text = data_checker_dict[i][0]
        selected_element = soup.select(data_checker_dict[i][1])
        if (len(selected_element) == 1) and (selected_element[0].text.strip() == expected_text):
            print("expected_text: " + expected_text + " Len[" + str(len(expected_text)) + "] " + " received_text: " + selected_element[0].text.strip() +  " Len[" + str(len(selected_element[0].text.strip())) + "]" )
            matched_elements.append(selected_element[0].text.strip())
        else: 
            return False
    print(matched_elements)
    return True
    

def first_bill_month_finder():
    # Arguments: None
    # Function: Returns the dt_string DD-MMM-YYYY for the first bill.
    # Returns: dt_object
    month_object = install_date_finder()  #
    print("month_object in first_bill_month_finder()",month_object)
    sentinel = False
    while (sentinel == False):
        focus_date = date_tools.dt_object_to_mmm_yyyy(month_object)# focus date = 01-MMM-YYYY(month_object)
        url = "http://" + CESU_CONSUMER_PORTAL_1 + DETAILED_BILL_URL.replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date) # url = .com/focus-date/userid/bill-det
        print("Table Data Checker URL: ",url)
        request_data = s.get(url)
        sentinel = table_data_checker(request_data)
        if sentinel == True:
            print("sentinel value in while loop if con sentinel == True: ", sentinel)
            break
        elif sentinel == False:
            print("sentinel value in while loop if con sentinel ==False:", sentinel)
            month_object = date_tools.next_month(month_object)
    print(f"month_object: {month_object} focus_date: {focus_date}")
    return month_object


# TODO send first_bill_finder() and previousmonth() to a function to create a generator 

def detailed_bill_requester(date_list):
    soup_list = []
    for focus_date in date_list:
        time.sleep(5) # TODO Add a limiter; Download all data first , store it and then call bill_dict_generator() on the stored data
        r = s.get("http://" + CESU_CONSUMER_PORTAL_1 + DETAILED_BILL_URL.replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date))
        soup = bs(r.text, 'html.parser')
        soup_list.append(soup)
        print(f"requester's focus_date: {focus_date}")



detailed_bill_dict = defaultdict(dict)
def detailed_bill_dict_generator(soup, focus_date): # TODO This will fail or present erroneous data if blank data is received from Server. 
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


first_bill_month = first_bill_month_finder()
previous_month = date_tools.previous_month()
date_list = date_tools.month_range(first_bill_month, previous_month)
print(date_list)

detailed_bill_soup_list = detailed_bill_requester(date_list)
focus_date_count = 0
for soup in detailed_bill_soup_list:
    detailed_bill_dict_generator(soup, date_list[focus_date_count])
    focus_date_count += 1
pprint.pprint(detailed_bill_dict)

with open("./data/bill_data.json", "w") as write_file:
    json.dump(detailed_bill_dict, write_file)


