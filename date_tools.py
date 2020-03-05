from datetime import *
from dateutil.relativedelta import *
from dateutil.parser import parse
from dateutil.rrule import *


today = datetime.now()
#Current Month
def current_month():
    delta_current_month = relativedelta(day=1) # delta for first day of the month
    current_month_dt_object = today + delta_current_month
    return current_month_dt_object


#Preceeding Month
def previous_month():
    delta_preceeding_month = relativedelta(day=1, months=-1) #delta for the firt day of preceeding month
    previous_month_dt_object = today + delta_preceeding_month
    return previous_month_dt_object

def current_month_string():
    # when called returns the previous month "MMM-YYYY" string
    return datetime.strftime(current_month(), "%b-%Y").upper()

def previous_month_string():
    # when called returns the preious month string
    return datetime.strftime(previous_month(), "%b-%Y").upper()


def installation_date_parser(installation_date):
    # parse date from given string from soup
    # return date object and string of the installation date
    pass
 

def date_validator(date_string, dt_string_format):
    # Argument: month_string "MMM-YYYY"; Type: String
    # Function: get particular month "MMM-YYYY" string and check if valid; 
    # if string can be converted to a valid date object returns (True, dt_object of the month string and the original month string)
    # Returns: Tuple containing (Boolean, date object, string)
    try:
        if dt_string_format == "DD-MM-YYYY" or "DD/MM/YYYY":
            dt_object = parse(date_string, dayfirst=True) # TODO Add more cases here as per the string format requirements
        else:
            raise ValueError
    except ValueError:                  # 
        print("You entered an invalid month or year!")
    else:
        return (True, dt_object, date_string)

def date_string_to_mmm_yyyy(date_string, dt_string_format):
    # Argument: Receives any datetime string "DD-MM-YYYY" "DD/MM/YYYY" etc.
    # Function: Converts the random date string to MMM-YYYY string
    # Returns: A "MMM-YYYY" string. Eg. "MAY-2019" "SEP-2020"
    dt_object = date_validator(date_string, dt_string_format)[1]
    dt_object = dt_object.replace(day=1)
    return datetime.strftime(dt_object, "%b-%Y").upper()

def string_to_dt_object(month_string, dt_string_format):
    dt_object = date_validator(month_string, dt_string_format)[1]
    dt_object = dt_object.replace(day=1)
    return dt_object 

# def date_within_range(installation_month_date_string, previous_month_date_string, month_string):
#     installation_dt_object = date_object(installation_month_date_string)
#     previous_dt_object = date_object(previous_month_date_string)
#     month_string = date_object(month_string)
#     # if installation dt_object < 

def month_range(start_dt_obj, end_dt_obj):
    # Argument: two datetime objects 
    # Function: Given two datetime objects this gives the list of months from start_dt_obj to end_dt_obj
    # Returns: Return a list of MMM-YYYY strings 
    return [datetime.strftime(i, "%b-%Y").upper() for i in rrule(freq=MONTHLY, dtstart=start_dt_obj, until=end_dt_obj)]






# def date_list_creator(start_date, end_date, duration):
#     # This function is used for:
#     #   Single Month's Bill (This Month, a Particular Month's bill, Previous Month's Bill) [where start_date == end_date] OR [there's just the start_month]
#     #   Range of Months Bill 
#     #   All Data (From Installation until now)
#     if duration == "duration_this_month" or "duration_previous_month" or "duration_particluar_month":
#         # find date from start_date
#         date_list = list[start_date]
#     elif duration == "range":