# Shannon Cheng, 2021
# Tool to search google for predefined queries using custom search API


# Standard imports
import datetime
import time
import pandas as pd
import numpy as np
import requests
import nest_asyncio
nest_asyncio.apply()


# Enter Google API key
API_KEY = ''

# Input search queries
search_input = pd.read_excel('search_input.xlsx')

# Search parameters
NUMBER_OF_RESULTS_PAGES = 10
AVG_SLEEP_TIME = 10

# Results storage
all_results = pd.DataFrame()

# Search all queries
for index_number in search_input.index:
    site_search_data = search_input.loc[index_number].to_dict()
    site_to_search = site_search_data['site_searched']
    print('Starting search of ' + site_to_search)
    search_queries = site_search_data['all_search_queries'].split(', ')
    search_engine_id = site_search_data['search_engine']

    for text_to_search in search_queries:
        query_to_search = text_to_search+' '+'site:'+site_to_search
        print('Searching' + query_to_search)
        ran_out_of_results = False
        for page in range(1, NUMBER_OF_RESULTS_PAGES+1):
            if not ran_out_of_results:
                start = (page - 1) * 10 + 1
                url = (f"https://www.googleapis.com/customsearch/v1?"
                       f"key={API_KEY}&cx={search_engine_id}"
                       f"&q={query_to_search}&start={start}&filter=0")
                req = requests.get(url)
                if req.status_code == 200:
                    data = req.json()
                    search_results = data.get("items")
                    if not str(type(search_results)) == "<class 'NoneType'>":
                        print('Found ' + str(len(search_results)) +
                              ' results on page ' + str(page)
                              + ' for ' + query_to_search)
                        formatted_results = pd.DataFrame(search_results)
                        formatted_results['search_engine'] = 'Google'
                        formatted_results['search_terms'] = text_to_search
                        formatted_results['site_searched'] = site_to_search
                        formatted_results['date_of_search'] = format(
                            datetime.datetime.now(), '%Y-%m-%d')
                        formatted_results['result_number'] = (
                            formatted_results.index + 1)
                        formatted_results['total_results'] = len(
                            search_results)
                        formatted_results['page_number'] = page
                        formatted_results['full_query'] = query_to_search
                        formatted_results = formatted_results[
                            ['date_of_search', 'search_engine',
                             'site_searched', 'search_terms', 'page_number',
                             'result_number', 'title', 'link',  'snippet',
                             'kind', 'htmlTitle', 'displayLink',
                             'htmlSnippet', 'formattedUrl', 'htmlFormattedUrl',
                             'pagemap',
                             'full_query',
                             ]]
                        formatted_results['total_results'] = (
                            data['searchInformation']['totalResults'])

                    else:
                        print('Found 0 results on page ' +
                              str(page) + ' for ' + query_to_search)
                        ran_out_of_results = True
                        formatted_results = pd.DataFrame()
                        formatted_results.loc[1, 'search_engine'] = 'Google'
                        formatted_results.loc[1,
                                              'search_terms'] = text_to_search
                        formatted_results.loc[1,
                                              'site_searched'] = site_to_search
                        formatted_results.loc[1, 'date_of_search'] = format(
                            datetime.datetime.now(), '%Y-%m-%d')
                        formatted_results.loc[1, 'result_number'] = 0
                        formatted_results.loc[1, 'page_number'] = page
                        formatted_results.loc[1, 'title'] = 'No results'
                        formatted_results.loc[1,
                                              'full_query'] = query_to_search
                        formatted_results.loc[1, 'total_results'] = 0

                else:
                    formatted_results = pd.DataFrame()
                    formatted_results.loc[1, 'search_engine'] = 'Google'
                    formatted_results.loc[1, 'search_terms'] = text_to_search
                    formatted_results.loc[1, 'site_searched'] = site_to_search
                    formatted_results.loc[1, 'date_of_search'] = format(
                        datetime.datetime.now(), '%Y-%m-%d')
                    formatted_results.loc[1, 'result_number'] = 0
                    formatted_results.loc[1, 'page_number'] = page
                    formatted_results.loc[1, 'title'] = (
                        'Search error' + str(req.status_code))
                    formatted_results.loc[1, 'full_query'] = query_to_search
                    formatted_results.loc[1, 'total_results'] = 0

                all_results = all_results.append(formatted_results)
                time.sleep(AVG_SLEEP_TIME*(1+2*np.random.rand()))

all_results.to_csv('search_output' + format(datetime.datetime.now(),
                   '%Y%m%d-%H%M%S') + '.csv', index=False)

print('Done!')
