'''
app to login into dataload and attempt to scrape down all file processed
for the day and any errors that might have occired
auth: adam
date: 11/21/18
'''
import datetime as dt
import html
import logging
import os
import pandas as pd
import re
import requests

from bs4 import BeautifulSoup

# constants
COLS = ['id', 'media', 'name', 'state1', 'state2', 'file', 'receipt',
        'format', 'load']

basedir = os.path.abspath(os.path.dirname(__file__))

# ######################## format logger #################################### #
# grab date script is run for logging date

def build_logger():
    log_date = dt.datetime.now()
    # grab dir script exitst in, logging dir exists in that dir as well
    # TODO possibly differnet logpath as CLI arg
    log_dir = os.path.join(basedir,'log\\')
    # create logger config object with date in filename, filename concats actual
    # filename with basedir & logging dir
    logging.basicConfig(filename=log_dir + 'dl_api_log.txt',
                                 level=logging.INFO,
                                 format='%(asctime)s %(message)s')

# ######################### scrape data ##################################### #
def scrape_data(login_url, target_url, post_data, get_params):
    # opening session object in 'with' context to ensure proper closure once
    # data is scraped and instantiated as bs4 object
    with requests.Session() as sess:
        # post to login form with approriate payload data created earlier
        login_response = sess.post(login_url, data=post_data)
        # check status code of returned response, 200 is expected if login was
        # successful, otherwise print status code
        if login_response.status_code != 200:
            logging.warning('Uh oh, response code of {0} '                     \
                  'received back!?'.format(login_response.status_code))
        else:
            # if login was successful, scrape data off redirect page from login
            homepage_response = sess.get(target_url, params=get_params)
            return homepage_response

# ####################### process raw data ################################### #
def process_data(response):
    # instatiate beautiful soup object to parse out data from html tree
    targetpage_soup = BeautifulSoup(response.text, 'html.parser')
    # declare list var to hold parsed raw data
    delim = []
    # regex pattern to pull text from within html tags, pattern only tracks
    # alphanumeric and the following specials [&,.';-()], if any other specials
    # are passed they text will not be captured
    p2 = r">([\d\s\w&,.\';\-\(\)]+)<"
    # find all 'tr' html tags, this equates to the html table on the target page
    # that holds the data.  html.unescape() method translates any html chars
    # into regular unicode
    for i in targetpage_soup.find_all('tr'):
        delim.append([html.unescape(i) for i in re.findall(p2, str(i))])
    return delim

# ##################### build result dataframe ############################### #
def build_df(processed_data):
    # grab only 1st 9 cols of the parsed data, the rest is not needed, also
    # exculde last item, it's blank
    delim2 = [i[:9] for i in processed_data[:-1]]
    # grab index of column headers to exclude unecessary items, add 1 so col
    # headers are not grabbed along with data
    idx = int([delim2.index(i) for i in delim2 if i[0]  == 'Id'][0]) + 1
    # drop data in dataframe for easy processing
    df = pd.DataFrame.from_records(delim2[idx:], columns=COLS)
    df['extension'] = df['file'].apply(lambda x :x.split('.')[-1])
    return df

# ################ check dataframe for fails and log ######################### #
def alert_on_fails(df):
    df_fails = df[df['state2'] == 'failed']
    # TODO write the function to send the email inside of the gmail_pull_attach
    # script, you need to turn that long script into function calls anyway
    # then just import with the approriate information
    if df_fails.empty:
        logging.warning('No failed fails found')
        return None
    else:
        logging.info('{}'.format(df_fails))
        return df_fails
