import os
from pathlib import Path



CESU_CONSUMER_PORTAL_1 = "http://117.239.112.120:8070"
CESU_CONSUMER_PORTAL_2 = "http://203.193.144.25:8080"

def is_portal_up():
    # Code to check when/which one of the portals(1or2) of the CESU is up:
    # This is hard to check because CESU won't turn up an error. 
    # But returns 200 and shows an error page while the entire backend is down
    # this happens so less that, its hard for me to reproduce this error in order to debug and write code for it.
    # for now this code returns CESU_CONSUMER_PORTAL_1 
    return CESU_CONSUMER_PORTAL_1

CESU_WORKING_PORTAL = is_portal_up()

LOGIN_PAGE_URL = CESU_WORKING_PORTAL + "/ConsumerPortal/welcome.jsp"
LOGIN_URL = CESU_WORKING_PORTAL + "/ConsumerPortal/Record_Check"
BILLS_PAGE_URL = CESU_WORKING_PORTAL + "/ConsumerPortal/bill_s4.jsp"
DETAILED_BILL_URL = CESU_WORKING_PORTAL + "/ConsumerPortal/bill_det.jsp"
SBM_BILL_URL = CESU_WORKING_PORTAL + "/ConsumerPortal/SBM_Bill_Format.jsp"

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


