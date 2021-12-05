from datetime import *
from dateutil.relativedelta import *
from dateutil.parser import ParserError, parse
from dateutil.rrule import *
import constants

TODAY = datetime.now()

def month_cycler(output_format, input_data="", day=1, month_cycle=0):
    if output_format in constants.VALID_DATE_FORMATS:
        if output_format == "MMMYYYY":
            date_string = datetime.strftime(month_cycler("DTObject", month_cycle=month_cycle, day=day), "%b-%Y").upper()
        if output_format == "DDMMMYYYY":
            date_string = datetime.strftime(month_cycler("DTObject", month_cycle=month_cycle, day=day), "%d-%b-%Y").upper()
        return date_string
    elif output_format == "DTObject":
        delta_month = relativedelta(day = day, months=month_cycle)
        month_dto = TODAY + delta_month
        return month_dto


def installation_date_parser(installation_date):
    # parse date from given string from soup
    # return date object and string of the installation date
    pass
 

def date_validator(date_string, dt_string_format="DD-MM-YYYY"):
    """date_validator(date_string, dt_string_format)
    gets particular date/month ("DD-MM-YYYY" or "MMM-YYYY") string; 
    if string can be converted to a tuple is returned
    (True, dt_object of the month string, the original month 
    string)

    Args:
        date_string (str): [description]
        dt_string_format (str, optional): [description] 
        Defaults to "DD-MM-YYYY".

    Returns:
        if True:
            tuple:(Boolean, date object, string)
        if False:
            tuple:(Boolean, string error message, string)
    """
    try:
        if dt_string_format == "DD-MM-YYYY" or "DD/MM/YYYY":
            dt_object = parse(date_string, dayfirst=True)
    except ParserError as pe:                  # 
        return (False, f"{pe}", date_string)
    else:
        return (True, dt_object, date_string)

def date_string_to_mmm_yyyy(date_string, dt_string_format="DD-MM-YYYY"):
    """date_string_to_mmm_yyyy() Converts the random date 
    string DD-MM-YYYY/DD-MMM-YYYY to 01-MMM-YYYY string

    Args:
        date_string (str): [description]
        dt_string_format (str, optional): [description]. 
        Defaults to "DD-MM-YYYY".

    Returns:
        str: A "01-MM-YYYY" string. Eg. "01-MAY-2019" "01-SEP-2020"
    """
    dt_object = date_validator(date_string, dt_string_format)[1]
    dt_object = dt_object.replace(day=1)
    return datetime.strftime(dt_object, "%d-%b-%Y").upper()

def dt_string_to_dt_object(date_string, dt_string_format="DD-MM-YYYY"):
    """
    dt_string_to_dt_object(date_string, dt_string_format="DD-MM-YYYY")
    for a given date_string it returns the respective 
    datetime object with day set to 1.

    Args:
        date_string (string): [description]
        dt_string_format (str, optional): [description]. 
        Defaults to "DD-MM-YYYY".

    Returns:
        [type]: [description]
    """
    dt_object = date_validator(date_string, dt_string_format)[1]
    dt_object = dt_object.replace(day=1)
    return dt_object 

def dt_object_to_mmm_yyyy(dt_object):
    #TODO Needs a name change since it returns a 01-MMM-YYYY string
    """dt_object_to_mmm_yyyy(dt_object)
    For a given datetime object it returns a 01-MMM-YYYY string.

    Args:
        dt_object (datetime object): [description]

    Returns:
        str: [description]
    """
    dt_object = dt_object.replace(day=1)
    return datetime.strftime(dt_object, "%d-%b-%Y").upper()

def next_month(dt_object):
    #TODO needs a name change since it returns a datetime object
    #TODO change it to next_month_dto()
    """next_month(dt_object)
    For a given datetime object it returns the datetime object of
    the next month.
    Args:
        dt_object (datetime object): [description]

    Returns:
        [type]: [description]
    """
    dt_object = dt_object+relativedelta(months=+1)
    return dt_object

# def date_within_range(installation_month_date_string, previous_month_date_string, month_string):
#     installation_dt_object = date_object(installation_month_date_string)
#     previous_dt_object = date_object(previous_month_date_string)
#     month_string = date_object(month_string)
#     # if installation dt_object < 

def mmm_yyyy_month_range(start_dt_obj, end_dt_obj):
    #TODO Change function name
    #TODO Change argument names to start_dto, end_dto maybe? 
    """mmm_yyyy_month_range(start_dt_obj, end_dt_obj)
        Given two datetime objects this gives the list of 
        01-MMM-YYYY strings from start_dt_obj to end_dt_obj
        (inclusive).
    Args:
        start_dt_obj (datetime object): Start month datetime object
        end_dt_obj (datetime object): End month datetime object

    Returns:
        list: [description]
    """
    print("start_dt_obj_type", type(start_dt_obj))
    print("end_dt_object_type", type(end_dt_obj))
    rrule_obj = rrule(freq=MONTHLY, dtstart=start_dt_obj, until=end_dt_obj)
    return [datetime.strftime(i, "%d-%b-%Y").upper() for i in rrule_obj]






# def date_list_creator(start_date, end_date, duration):
#     # This function is used for:
#     #   Single Month's Bill (This Month, a Particular Month's bill, Previous Month's Bill) [where start_date == end_date] OR [there's just the start_month]
#     #   Range of Months Bill 
#     #   All Data (From Installation until now)
#     if duration == "duration_this_month" or "duration_previous_month" or "duration_particluar_month":
#         # find date from start_date
#         date_list = list[start_date]
#     elif duration == "range":