import dateutil.parser
import datetime

# This is used to override the datetime.datetime object's replace
# function, otherwise unincluded arguments default to the current date's
# value for some reason. This is undeniably a hack.
class DateTimeReplacementFunc():
    def replace(self, **fields):
        if any(f not in fields for f in ('year', 'month', 'day')):
            return False
        return datetime.datetime(2000, 1, 1).replace(**fields)

def wrap_parse(v):
    try:
        _actual = dateutil.parser.parse(v, default=DateTimeReplacementFunc())
    except ValueError:
        return False
    if _actual:
        return _actual.date()
    else:
        return False

# Take a date as a string and return it normalized to YYYY-MM-DD,
# or return False if it's not a valid date
def date_fixer(date):
    date = date.strip()
    month_int_dict = {'january':   1,
                      'february':  2,
                      'march':     3,
                      'april':     4,
                      'may':       5,
                      'june':      6,
                      'july':      7,
                      'august':    8,
                      'september': 9,
                      'october':   10,
                      'november':  11,
                      'december':  12}

    if (len(date.split('/')) == 3): # Match dates of the form 'MM/DD/YYYY'
        # Convert the date into a list of ints
        split_date = [int(string) for string in date.split('/')]
    elif (len(date.split(' ')) == 3): # Match dates of the form 'month day, year'
        split_date = date.split()
        split_date[0] = month_int_dict[split_date[0].lower()] # Fix the month
        split_date = map(int, split_date)
    else: # The date is invalid
        return False

    # Now stringify the month and day to make sure it's normalized
    for ind in range(2):
        current = str(split_date[ind])
        split_date[ind] = '0'*(len(current) % 2) + current
    year = split_date[-1]
    if year < 1000:
        if split_date >= 50: # Only works until 1950!
            split_date +=  1900
        else:
            split_date += 2000


