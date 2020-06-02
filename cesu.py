import requests, os, argparse, configparser, json, pprint, time, string, random, sys
from bs4 import BeautifulSoup as bs
from collections import defaultdict
import date_tools
from constants import (LOGIN_PAGE_URL,
                        LOGIN_URL,
                        BILLS_PAGE_URL,
                        DETAILED_BILL_URL,
                        SBM_BILL_URL, 
                        SBM_BILLS_DIRPATH,
                        SBM_BILL_SUPPORTED_FORMATS)
import webscreenshot

consumer_account_no = os.environ['ACCOUNT']
consumer_id = consumer_account_no[4:]
division_code = consumer_account_no[:3]

def basic_config_creator(account):
    config = configparser.ConfigParser()
    config['BASIC']['CESU Consumer Account No.'] = account
    with open('cesu.ini', 'w') as configfile: #constants.CONFIG_FILEPATH
        configfile.write(configfile)


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


loginparams = {
    'strConsID': consumer_account_no,
    'OptType': 'Login',
    'strDivCode': '0',
    'strConsumerType': '0',
    'strConsNo': '',
    'txtInput': old_loltcha_gen(),
    'image2.x': '45',
    'image2.y': '11',
}

s = requests.Session()
try:
    r = s.get(LOGIN_PAGE_URL)
    r = s.get(LOGIN_URL, params=loginparams, cookies=s.cookies, headers=s.headers) # SUBMIT button
    print(r.status_code)
except requests.RequestException as exception:
    print("Network Error Occured!")
    print(exception)
    sys.exit(1)

#TODO check the redirect above and see if redirected to `not_found_server.jsp` or to `loginindex.jsp`.

#single request for 01-MMM-YYYY detailed_bill_format.jsp  


def install_date_finder():
    # Arguments: None
    # Function: Returns the installation date of the meter as a dt_object from the bill_det page (Fetches the latest available bill_det page for this.)
    # Returns: dt_object
    focus_date = date_tools.previous_month_string() # TODO If the current month's bill hasn't been generated then the previous month bill won't be available on detailed_bill
    print("focus date in install_date_finder",focus_date)
    r = s.get(DETAILED_BILL_URL.replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date)) 
    soup = bs(r.text, 'html.parser') # TODO This soup needs checking by table data checker; if data is not found then previous to previous month data needs to be fetched.
    installation_date_string = soup.select('body > div:nth-child(2) > center:nth-child(1) > table:nth-child(3) > tr:nth-child(2) > td:nth-child(6) > div:nth-child(1) > b:nth-child(1) > font:nth-child(1)')[0].text.strip()
    print("installation_date_sting in install_date_finder",installation_date_string)
    installation_dt_object = date_tools.dt_string_to_dt_object(installation_date_string, "DD/MM/YYYY")
    return installation_dt_object


def table_data_checker(request_data):
    # The reason this function exists is because sometimes I get an empty or half populated detailed bill page due to server-side errors. 
    # This happens rarely but can be a headscratcher. This is something quick that I wrote. There's probably a better way to do this.
    # Arguments: request_data [beautifulsoup soup]
    # Function: Checks the first 'td' each table in detailed bill to check if the string within it matches a predefined string.
    # Returns: True when all td strings match the predefined string, else returns False.
    # :TODO: This is currently set up so that it prints every time. But I will make it so that it outputs only when verbose mode is
    # activated or an Error occurs.
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
            print(f"Expected: {expected_text}. Not found!")
            return False
    print(matched_elements)
    return True
    

def first_bill_month_finder():
    # The reason this function exists is because the installation date of the meter can preceed the first bill generated, by almost 2-3 months.
    # Hitting the endpoint for the 2-3 months in between will return empty detailed bill pages.
    # Arguments: None
    # Function: Returns the dt_string DD-MMM-YYYY for the first bill.
    # Returns: dt_object for the first bill month
    # This prints all the time. Make it print on verbosity ON or Error
    month_object = install_date_finder()  #
    print("month_object in first_bill_month_finder()",month_object)
    sentinel = False
    while (sentinel == False):
        focus_date = date_tools.dt_object_to_mmm_yyyy(month_object)# focus date = 01-MMM-YYYY(month_object)
        url = DETAILED_BILL_URL.replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date) # url = .com/focus-date/userid/bill-det
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
    # Arguments: date_list [list of MMM-YYYY date_strings]
    # Function: Given the date_list this will request detailed bill for each month in that list and store the corresponding soups in soup_list
    # and return the soup_list
    # Returns:  soup_list [List of bs4 soups of detailed_bill for each MMM-YYYY in date_list]
    soup_list = []
    for focus_date in date_list:
        time.sleep(5) 
        r = s.get(DETAILED_BILL_URL.replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date))
        soup = bs(r.text, 'html.parser')
        soup_list.append(soup)
        print(f"requester's focus_date: {focus_date}")
    return soup_list



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

def all_detailed_bill_data_json():
    first_bill_month = first_bill_month_finder()
    previous_month = date_tools.previous_month()
    date_list = date_tools.mmm_yyyy_month_range(first_bill_month, previous_month)
    print(date_list)
    detailed_bill_soup_list = detailed_bill_requester(date_list)
    focus_date_count = 0
    for soup in detailed_bill_soup_list:
        detailed_bill_dict_generator(soup, date_list[focus_date_count])
        focus_date_count += 1
    pprint.pprint(detailed_bill_dict)
    with open("./data/bill_data.json", "w") as write_file:
        json.dump(detailed_bill_dict, write_file)


def check_latest_sbm_bill_present(verbosity=False):
    #check bills page if latestbill element exists
        # count the number of tr in the last table of the page.
            # if the count == 18 then 15,16,17 tr are important 
                    # 15 - Bill Details for Current/Latest Month(s) ; 
                    # 16 - Row of theads Bill Month - Bill Date; Current Reading; Unit bill; Energy Charge; Electricity Duty; Meter Rent; Fix Charge; Current Total; Rebate Amt; Rebate Date; Amount Paid; Collection Date
                    # 17 - Link to bill and data
                # Match 17's first column's MMM-YYYY string to current month's MMM-YYYY
            # 
    # fetch sbm details for that MMM-YYYY month
        # have to get the html
        # have to get the data as a json as well.
        # get the screenshot. needed for TG bot and quick share
    r = s.get(BILLS_PAGE_URL)
    soup = bs(r.text, "html.parser")
    last_tables_trs = len(soup.select("body > table:nth-child(4) > tr"))
    bill_gen_month_name = soup.select("body > table:nth-child(4) > tr:nth-child(17) > td:nth-child(1) > div > a")[0].text.strip()
    print(bill_gen_month_name)
    current_month_mmm_yyyy_string = date_tools.current_month_string()
    previous_month_mmm_yyyy_string = date_tools.previous_month_string()
    print(current_month_mmm_yyyy_string)
    if last_tables_trs == 18:
        # print(f"No. of 'tr's contained in the last table of bills page: Expected: 18; Received: {last_tables_trs}\n")
        if (bill_gen_month_name == current_month_mmm_yyyy_string):
            return (True, bill_gen_month_name)
        elif (bill_gen_month_name == previous_month_mmm_yyyy_string):
            return (True, bill_gen_month_name)
    elif last_tables_trs != 18:
        print("SBM Bills haven't been generated by CESU or else malformed HTML!")
        return (False, "")


def get_sbm_bill(stringornot="latest", date_string=""):
    current_month_mmm_yyyy_string = date_tools.current_month_string()
    previous_month_mmm_yyyy_string = date_tools.previous_month_string()
    focus_date = "01-"
    if stringornot == "latest":
        print("Checking for the latest SBM Bill...")
        check_for_sbm = check_latest_sbm_bill_present()
        if check_for_sbm[0] == True:
            print(f"SBM Bill found for the month: {check_for_sbm[1]}")
            focus_date += check_for_sbm[1]
        else:
            sys.exit("SBM Bills were not found or else malformed HTML.")
    if stringornot == "datestring":
        print(f"Fetching SBM Bill data for the month: {date_string}")
        focus_date += date_string
    sbm_params = {
        'DIVCODE': division_code,
        'CONS_ACC': consumer_id,
        'CESU_DATE': focus_date
    }
    sbm_bill_response = s.get(SBM_BILL_URL, cookies=s.cookies, headers=s.headers, params= sbm_params)
    output_sbm_bill(sbm_bill_response, focus_date)


def output_sbm_bill(sbm_bill_response, focus_date):
    print("Please choose the format that you want the bill in:")
    for i in range(len(SBM_BILL_SUPPORTED_FORMATS)):
        print(f"{i+1}. {SBM_BILL_SUPPORTED_FORMATS[i]}")
    selected_format = input()
    if selected_format == 1:
        with open(SBM_BILLS_DIRPATH + f"{focus_date}.html", "w") as sbm_html_file:
            sbm_html_file.write(sbm_bill_response)

get_sbm_bill()
