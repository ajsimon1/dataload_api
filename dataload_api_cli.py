'''
Author: Adam Simon
Date Created: 3/19/2019
Description:
CLI tool that can trigger actions on Dataload application by passing approiate
query parameter 'action'
'''
import argparse
import logging
import requests

import dataload_api_core as dac

 # ########################  DEFAULT URLs  ################################### #
dl_base_url = 'http://dataload.vcmww.com/dataload/'
dl_login_url = dl_base_url + 'DL_Login.jsp'
dl_work_url = dl_base_url + 'DL_Work.jsp'

# ########################## CREATE ARGS ##################################### #
parser = argparse.ArgumentParser(description='CLI tool to automate clicking '  \
                                             'of UI button to kickoff '        \
                                             'dataload application processes')
parser.add_argument('action', help='specify which action should be sent after'  \
                                  ' with query param to URL')
parser.add_argument('-u', '--user', help='valid username to pass to login page')
parser.add_argument('-p', '--password', help='valid pwd to pass to login page')
parser.add_argument('-l','--login_url',help='full url of login page')
parser.add_argument('-t', '--target_url', help='url to target adter login')
parser.add_argument('-o', '--output', help='folder path to send error file '   \
                                            'created if login unsucessful')

# ########################## MAIN FUNCTION ################################### #
def run(args):
    # post data applicaple to form on login page
    post_data = {
        'login': args.user,
        'password': args.password
    }
    # set action passed in CLI to 'action' param of target url query
    # newDriver requires submissionId of 0 to kick job off
    if args.action == 'driver':
        get_params = {
            'action': 'newDriver',
            'submissionId': '0'
        }
    # no submissionId needed for stage file job
    elif args.action == 'stage':
        get_params = {
            'action': 'stageFiles'
        }
    # extending capability in case script needs to hit another login
    if args.login_url:
        login_url = args.login_url
    else:
        login_url = dl_login_url
    # extending capabiilty to change target URl if needed
    if args.target_url:
        target_url = args.target_url
    else:
        target_url = dl_work_url

    response = dac.scrape_data(login_url, target_url, post_data, get_params)
    processed = dac.process_data(response)
    if processed[0][3].strip() == 'Driver 1 importing' or processed[0][3].strip() == 'Driver 1 scanning':
        logging.info('{} received, all is good'.format(processed[0][3]))
    else:
        logging.warning('Unexpected statement "{}" received back, check to '  \
                        'ensure dataload is functionality'                     \
                        ''.format(processed[0][3]))
    return None

if __name__ == '__main__':
    dac.build_logger()
    args = parser.parse_args()
    run(args)
    # TODO add logging warnings and info directly to core functions, the
    # log file will still generate in the approriate folder, ddont need to
    # call it from CLI
