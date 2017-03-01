import csv
import sys
import dateutil.parser
import datetime


def csv_to_dictionary(csv_filename):
    """
    Takes the filename of a two column CSV file
    and returns a dictionary of the rows as key-value pairs
    """
    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        result_dict = {row[0]: row[1] for row in reader}
        return result_dict


class DateTimeReplacement():
    """
    This is used to override the datetime.datetime object's replace
    function. Otherwise, unincluded arguments default to today's date's
    values for some reason. This is undeniably a hack, but it's a much simpler
    solution than writing a custom parser.
    Credit for this idea:
        stackoverflow.com/questions/8434854/parsing-a-date-in-python-without-using-a-default
    """
    def replace(self, **kwargs):
        if any(f not in kwargs for f in ('year', 'month', 'day')):
            return False
        date_obj = datetime.datetime(datetime.MINYEAR, 1, 1).replace(**kwargs)
        return str(date_obj.date())


def date_fixer(date):
    """
    Takes a date as a string and returns it normalized to YYYY-MM-DD,
    or returns False if it's not a valid date
    """
    try:
        fixed_date = dateutil.parser.parse(date, default=DateTimeReplacement())
    except (ValueError, AttributeError, OverflowError):
        # These errors simply mean the input date isn't valid
        return False
    return fixed_date


def normalize_whitespace(string):
    """
    Strips a string of all whitespace, and returns
    the resulting string delimited by spaces
    """
    return ' '.join(string.split())


def write_fixed_csv(input_filename, output_filename):
    """
    The main function for cleaning an input CSV's rows and
    putting them into a given output file
    """
    state_abbr_dict = csv_to_dictionary('state_abbreviations.csv')

    with open(input_filename, 'rb') as csv_file:
        # Open as a CSV file for reading
        csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

        # Nesting the reader/writer context managers allows us to only open each
        # file once, minimizing the use of an expensive process
        with open(output_filename, 'wb') as csv_solution:
            solution_writer = csv.writer(csv_solution, delimiter=',', quotechar='"')

            # Get relevant indices for for fixing the output CSV
            first_line = csv_file_reader.next()
            bio_ind = first_line.index('bio')
            state_ind = first_line.index('state')
            start_date_ind = first_line.index('start_date')
            start_date_desc_ind = start_date_ind + 1

            # Add the column for filtering invalid dates, and write to output
            first_line.insert(start_date_desc_ind, 'start_date_description')
            solution_writer.writerow(first_line)

            # Iterate over the lines and perform the desired fixes
            # before writing the fixed line to the output CSV
            for line in csv_file_reader:
                line[bio_ind] = normalize_whitespace(line[bio_ind])  # Fix bio
                line[state_ind] = state_abbr_dict[line[state_ind]]  # Fix state
                # Fix starting date, or starting date desc if the date is invalid
                fixed_date = date_fixer(line[start_date_ind])
                if fixed_date:
                    line[start_date_ind] = fixed_date
                    line.insert(start_date_desc_ind, '')
                else:
                    line.insert(start_date_desc_ind, line[start_date_ind])
                    line[start_date_ind] = ''

                # Now that the row is fixed, write it to the output file
                solution_writer.writerow(line)


if __name__ == '__main__':
    debug = False  # Set to True to run tests, or False to run the program

    if debug:
        import unittest
        sys.argv = sys.argv[:1]  # Avoids an error when inputting a filename

        class CSVCleanerTest(unittest.TestCase):
            def test_csv_to_dictionary(self):
                test_dict = csv_to_dictionary('state_abbreviations.csv')
                self.assertTrue(isinstance(test_dict, dict))
                inputs = (('ID', 'Idaho'),
                          ('IA', 'Iowa'),
                          ('NY', 'New York'))
                self.assertTrue(test_dict[t[0]] == t[1] for t in inputs)

            def test_date_fixer_valid_inputs(self):
                inputs = (('Sep 5th, 2014', '2014-09-05'),
                          ('5 oct 1995', '1995-10-05'),
                          ('2005 31 JANUARY', '2005-01-31'),
                          ('22nd, december, 90', '1990-12-22'),
                          ('11-25-89', '1989-11-25'),
                          ('2000-12-08', '2000-12-08'))
                self.assertTrue(all(date_fixer(t[0]) == t[1] for t in inputs))

            def test_date_fixer_invalid_inputs(self):
                inputs = ('', '1950, october', 'nov 2001',
                          '2002 March', '7th, 2002,' '2017',
                          '5/13', '7/73', '02/02', 'test',
                          '3/12/2330420330')
                self.assertFalse(any(date_fixer(i) for i in inputs))

            def test_normalize_whitespace(self):
                inputs = (('', ''),
                          ('\tinput1\tinput1\t', 'input1 input1'),
                          ('\ninput2\ninput2\n', 'input2 input2'),
                          (' input3 input3 ', 'input3 input3'),
                          ('\n\t input4  \n\n\t   input4  \n\t', 'input4 input4'))
                result = all(normalize_whitespace(t[0]) == t[1] for t in inputs)
                self.assertTrue(result)

        unittest.main()

    else:
        try:
            input_filename = sys.argv[1]
        except IndexError:
            sys.exit('IndexError: Please include a csv filename as ' +
                     'an argument to the program')
        output_filename = 'solution.csv'
        state_csv_filename = 'state_abbreviations.csv'

        # Run the csv cleaner
        write_fixed_csv(input_filename, output_filename)
