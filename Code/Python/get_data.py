#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 13:19:48 2021

@author: Viktoria
"""

import samples
import json
import util
import requests
import os


#Define the way of generating a token to acces the Octoparse API with 
def log_in(base_url, username, password): 	
    
        print('Get token:')
        content = 'username={0}&password={1}&grant_type=password'.format(username, password)
        token_entity = requests.post(base_url + 'token', data = content).json()

        if 'access_token' in token_entity:
                print(token_entity)
                return token_entity
        else:
                print(token_entity['error_description'])
                os._exit(-2)
                

#GO TO OCTOPARSE
base_url = 'https://dataapi.octoparse.com/'

#Get the token used for accessing the Octoparse API
token_entity = log_in(base_url, 'Aditthana', 'March_FlawlessMoney')

samples.refresh_token(base_url, token_entity['refresh_token'])

token = token_entity['access_token']

#get a list of the groups in which the scrapers are organised in Octoparse
groups = samples.get_task_group(base_url, token)

#define the target group in Octoparse
target_group = [n for n in groups if n.get('taskGroupName')=='e_money']

#tasks are the individual scrapers for the websites
tasks = samples.get_task_by_group_id(base_url, token, target_group[0]['taskGroupId'])

#extract data from individual scrapers (=tasks)
for i,t in enumerate(tasks):
    
    task_id = tasks[i]['taskId']
    name = tasks[i].get('taskName')
    
    #EXPORT DATA
    
    #first extract the first n lines and check the total number of lines to be extracted
    url = 'api/notExportData/getTop?taskId=' + task_id + '&size=1'
    check_len = util.request_t_get(base_url, url, token)
    n = check_len.get('data').get('total')
    
    #if there is unexported data
    if n > 0: 
    
        #now get all of it
        results = []
        while n > 100:
            #extract them by the hundred
            url = 'api/notExportData/getTop?taskId=' + task_id + '&size=' + str(100)
            data = util.request_t_get(base_url, url, token)
            results.extend(data.get('data').get('dataList'))
            samples.mark_data_as_exported(base_url, token, task_id)
            n = n - 100
            
        #now extract the last little bit
        url = 'api/notExportData/getTop?taskId=' + task_id + '&size=' + str(n)
        data = util.request_t_get(base_url, url, token)
        results.extend(data.get('data').get('dataList'))
        samples.mark_data_as_exported(base_url, token, task_id)
        
        with open(name + '.txt', 'w') as outfile:
            json.dump(results, outfile, indent=4)




