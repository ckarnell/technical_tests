from bs4 import BeautifulSoup
import json
import urllib2


def get_url_without_path(url):
    """
    Takes a url as a string and simply returns the same
    url stripped of it's suffixed path, or returns False
    if the url has no valid scheme
    """
    parsed = urllib2.urlparse.urlparse(url)
    if parsed.scheme:
        return parsed.scheme + '://' + parsed.netloc
    return False


def get_soup(url):
    """
    Takes a url as a string and returns a BeautifulSoup object
    ready for html parsing
    """
    response = urllib2.urlopen(url)
    html = response.read()
    return BeautifulSoup(html)


def parse_table_rows_for_company_data(soup):
    """
    Takes the soup object of a company page and returns a dict of
    what will become the json of that company's data
    """
    result = {}
    rows = soup.find_all('tr')
    for r in rows:
        tds = r.find_all('td')
        result[str(tds[0].b.text)] = str(tds[1].text)
    return result


def get_path_to_next_page(soup):
    """
    Takes the soup object of a company listing page and returns a
    path to the next page of company listings, or an empty string
    if there is no next page
    """
    list_rows = soup.find_all('li')
    # Get only rows that have the 'next' class
    next_row = [l for l in list_rows if 'class' in l.attrs
                if l['class'] == ['next']]
    if next_row:
        return next_row[0].a['href']
    else:
        return ''


def get_tds_containing_links(soup):
    """
    Takes a soup object and returns a list of the 'td'
    elements inside that contain hyperlinks
    """
    tds = soup.find_all('td')
    result = []
    # Get the relevant values from the tds
    for td in tds:
        # Make sure this element has an 'a' attribute
        if td.a:
            result.append(td)
    return result


def parse_td_link_for_company_path(td):
    """
    Takes a 'td' tag object with a hyperlink and returns its
    hyperlink as a string, fixed to be readable by urllib2
    """
    href = td.a['href']
    # Replace white space with chars readable by the url lib
    href = '%20'.join(href.split(' '))
    return href


def get_company_paths_on_page(soup):
    """
    Takes a BeautifulSoup object and uses our other functions to return
    a list of the company paths (note: not full urls) found on the page
    """
    page_tds = get_tds_containing_links(soup)
    return [parse_td_link_for_company_path(td) for td in page_tds]


def web_scrape(url, output_filename):
    "Main function for scraping the site for company data"

    base_url = get_url_without_path(url)  # Used to complete a url when we only have a path

    def recurse_path_finder(url, result=[], visited_pages=[]):
        """
        Adds the company paths on the given url to it's result list,
        and then searches for a "next" link on the page. It then calls itself if it
        finds a link using the new url as input, or returns the result list if it doesn't
        """
        soup = get_soup(url)
        visited_pages.append(url)  # Used to prevent an infinite loop
        result.extend(get_company_paths_on_page(soup))
        new_path = get_path_to_next_page(soup)
        new_url = base_url + new_path
        if new_path and new_url not in visited_pages:
            return recurse_path_finder(new_url, result)
        else:
            return result

    # Execute the recursive call to get every company page url
    print 'Collecting urls to company pages...'
    company_urls = [base_url+path for path in recurse_path_finder(url)]
    company_urls = list(set(company_urls))  # Get rid of duplicates
    total_companies = len(company_urls)  # Used to print progress updates

    json_result = {}  # A json dict with company names as keys and their data as values
    name_string = 'Company Name'

    # Finally, loop over the company urls and retrieve their data, compiling it
    # into a json object
    for url in company_urls:
        # Print a progress update once for every ten urls processed
        index = company_urls.index(url)
        if (company_urls.index(url) % 10 == 9):
            print 'Processing company url {} of {}...'.format(index+1, total_companies)

        # Parse and process the table rows for the company urls, building
        # the final result
        soup = get_soup(url)
        rows = parse_table_rows_for_company_data(soup)
        rows_without_company_name = {key: value for key, value in rows.items()
                                     if key != name_string}
        json_result[rows[name_string]] = rows_without_company_name

    # Write the result to a file
    with open(output_filename, 'wb') as json_solution:
        json.dump(json_result, json_solution, indent=4)


if __name__ == '__main__':
    debug = False  # Set to True to run tests, or False to run the program

    if debug:
        import unittest

        class WebScraperTest(unittest.TestCase):

            def test_get_url_without_path_valid_inputs(self):
                inputs = (('http://data-interview.enigmalabs.org/companies/',
                           'http://data-interview.enigmalabs.org'),
                          ('https://test_url.com/test1/test2/test3',
                           'https://test_url.com'))
                self.assertTrue(all(get_url_without_path(t[0]) == t[1] for t in inputs))

            def test_get_url_without_path_invalid_inputs(self):
                inputs = ('data-interview.enigmalabs.org/companies/',
                          'test_url.com/test1/test2/test3')
                self.assertFalse(any(get_url_without_path(i) for i in inputs))

            # NOTE: Removed tests that rely on local HTML to
            #       manipulate BeutifulSoup objects

        unittest.main()

    else:
        origin_url = 'http://data-interview.enigmalabs.org/companies/'
        output_filename = 'solution.json'
        web_scrape(origin_url, output_filename)
