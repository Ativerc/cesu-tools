import os
from pathlib import Path



CESU_CONSUMER_PORTAL_1 = "117.239.112.120:8070"
CESU_CONSUMER_PORTAL_2 = "203.193.144.25:8080"

LOGIN_PAGE = "/ConsumerPortal/welcome.jsp"
LOGIN_URL = "/ConsumerPortal/Record_Check?strConsID=USERNAME&OptType=Login&strDivCode=0&strConsumerType=0&strConsNo=&txtInput=LOLTCHA&image2.x=73&image2.y=14"
BILLS_PAGE_URL = "/ConsumerPortal/bill_s4.jsp"
DETAILED_BILL_URL = "/ConsumerPortal/bill_det.jsp?DIVCODE=DC&CONS_ACC=USERNAME&CESU_DATE=DD-MM-YYYY"
SBM_BILL_URL = "/ConsumerPortal/SBM_Bill_Format.jsp?DIVCODE=DC&CONS_ACC=USERNAME&CESU_DATE=DD-MM-YYYY"

# FILEPATHS
CESU_TOOLS_DIRECTORY_PATH = ""
if 'MODE' in os.environ:
    CESU_TOOLS_DIRECTORY_PATH = os.getcwd()
else:
    CESU_TOOLS_DIRECTORY_PATH = os.path.join(str(Path.home()), 'cesu_tools')


BILLS_DIRPATH = os.path.join(CESU_TOOLS_DIRECTORY_PATH, 'bills/')
SBM_BILLS_DIRPATH = BILLS_DIRPATH + 'sbm_bills/'
DATA_DIRPATH = os.path.join(CESU_TOOLS_DIRECTORY_PATH, 'data/')
CONFIG_FILEPATH = os.path.join(CESU_TOOLS_DIRECTORY_PATH, 'config', 'cesu_tools_config.ini')


