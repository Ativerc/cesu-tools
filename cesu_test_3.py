import requests
import os
from bs4 import BeautifulSoup as bs
import pprint
import json
from collections import defaultdict

consumer_account_no = os.environ['ACCOUNT']

consumer_id = consumer_account_no[4:]
division_code = consumer_account_no[:3]


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
focus_date = "01-MAY-2019"
r = s.get("http://" + ip_addrs['portal1'] + urls['detailed_bill_format'].replace("USERNAME", consumer_id).replace("DC", division_code).replace("DD-MM-YYYY", focus_date))
soup = bs(r.text, 'html.parser')


detailed_bill_dict = defaultdict(dict)

def bill_dict_generator(soup):
    detailed_bill_dict[focus_date] = {}
    for tableNo in [1,2,3,5]:                         #tableLoop
        table = soup.findAll('table')[tableNo]
        if tableNo == 1 or tableNo == 2 or tableNo == 5:
            for trNo in range(len(table.findAll('tr'))):  #trloop
                trow = table.findAll('tr')[trNo]
                for tdNo in range(len(trow.findAll('td'))):
                    td = trow.findAll('td')[tdNo]
                    if trNo != 0 and tdNo % 2 == 0:
                        # print("Key: " + td.text.strip())
                        # detailed_bill_dict[tablename][key] = ""
                        detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()][td.text.strip()] = ""
                    elif trNo == 0:
                        # print("\n\nTable No: " + str(tableNo) + "; Table Name: " + trow.findAll('td')[tdNo].text.strip())
                        # detailed_bill_dict[tablename] = {}
                        detailed_bill_dict[focus_date][trow.findAll('td')[tdNo].text.strip()] = {}
                    elif trNo != 0 and tdNo % 2 != 0: 
                        # print("Value: " + td.text.strip())
                        # detailed_bill_dict[tablename][key] = "value"
                        detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()][table.findAll('tr')[trNo].findAll('td')[tdNo-1].text.strip()] = td.text.strip()
        elif tableNo == 3:
            for trNo in range(len(table.findAll('tr'))): #trLoop
                trow = table.findAll('tr')[trNo]
                if trNo == 0:
                    # print("\n\nTable No: " + str(tableNo) +"; Table Name: " + trow.findAll('td')[0].text.strip())
                    detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()] = {}
                if trNo != 0 and trNo % 2 != 0:
                    for tdNo in range(len(trow.findAll('td'))):
                        key = table.findAll('tr')[trNo].findAll('td')[tdNo].text.replace("\n", "").replace("\r", "")
                        value = table.findAll('tr')[trNo+1].findAll('td')[tdNo].text.strip()
                        key = key.strip() #.replace("\n", "")
                        # detailed_bill_dict[tablename][value] = key
                        detailed_bill_dict[focus_date][table.findAll('tr')[0].findAll('td')[0].text.strip()][key] = value
                         # print("Key: " + key)
                         # print("Value: " + value.strip())


bill_dict_generator(soup)
pprint.pprint(detailed_bill_dict)

with open("./data/bill_data.json", "w") as write_file:
    json.dump(detailed_bill_dict, write_file)


