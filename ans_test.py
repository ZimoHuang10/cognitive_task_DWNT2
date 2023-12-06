from IPython.display import display, Image, clear_output, HTML
import time
import random
import os 
import pandas as pd
import numpy as np
import ipywidgets as widgets
from jupyter_ui_poll import ui_events

# load stimuli
stimuli        = ['10vs9.png', '12vs9.png','14vs12.png',
                  '16vs12.png','18vs16.png','20vs15.png',
                  '20vs18.png','21vs18.png','9vs10.png','9vs12.png','12vs14.png','12vs16.png','16vs18.png',
                  '15vs20.png','18vs20.png','18vs21.png']

stim_ans        = ['l','l','l','l','l','l','l','l','l','r','r','r','r','r','r','r','r']
stim_ans_button = ["Left" if ans == 'l' else "Right" if ans == 'r' else ans for ans in stim_ans]
stim_ratio      = [10/9, 12/9, 14/12, 16/12, 18/16, 20/15, 20/18, 21/18, 9/10, 9/12, 12/14, 12/16, 16/18, 15/20, 18/20, 18/21]
stim_ratio      = [round(ratio, 2) for ratio in stim_ratio]


stimuli_ratio_dict = dict(zip(stimuli, stim_ratio))
stimuli_dict       = dict(zip(stimuli, stim_ans_button))

stim = stimuli.copy()


# for button press

event_info = {
    'type': '',
    'description': '',
    'time': -1
}

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):    
    start_wait = time.time()

    # set event info to be empty
    # as this is dict we can change entries
    # directly without using
    # the global keyword
    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:
            # process UI events
            ui_poll(n_proc)

            # end loop if we have waited more than the timeout period
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False
                
            # end loop if event has occured
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False
                
            # add pause before looping
            # to check events again
            time.sleep(interval)
    
    # return event description after wait ends
    # will be set to empty string '' if no event occured
    return event_info

# this function lets buttons 
# register events when clicked
def register_btn_event(btn):
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()
    return

# send results 

import requests
from bs4 import BeautifulSoup
import json

def send_to_google_form(data_dict, form_url):
    ''' Helper function to upload information to a corresponding google form 
        You are not expected to follow the code within this function!
    '''
    form_id = form_url[34:90]
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]
    form_dict = {}
    
    loaded_all = True
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]
    
    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok



def ans_test(id):

    gender = input('please enter your gender')
    
                                     
    answer = []    # participants's response 
    rt     = []    # reaction time per trial
    track  = []    # permutation tracking 

    n_trials = 16
    n_block  = 4

    
    
    rematrix = []
    # collect all response, 1 for correct, 0 for incorrect, -3 for missing 
    # length of matix will be number of trials 
    
    random.seed(1)    
    

    re     = []      # response, for checking the answering time window 
    score  = 0     # scoring initialization 
    list_ratio = []
    
    for b in range(n_block): 
        random.shuffle(stim)
        for i in range (n_trials):
                bottom_area = widgets.Output(layout={"height":"60px"})
                # in range of trial numbers x blocks 
                # display fixation point
                fix = Image('fixation.png')
                display(fix)
                display(bottom_area)
                time.sleep(1.5)
                clear_output()
                
                # display ans stimuli
                dots=Image(stim[i])
                display(dots)
                display(bottom_area)
                time.sleep(0.75)
                clear_output()
    
                # tracking time window for answering 
                start_time = time.time()
    
               
                # back to fixation use a image to present the task instruction 
        
                bottom_area = widgets.Output(layout={"height":"60px"})
                        
                btn1 = widgets.Button(description="Left")
                btn2 = widgets.Button(description="Right")
                        
                btn1.on_click(register_btn_event)
                btn2.on_click(register_btn_event)

                btn1.layout.width = '500px'
                btn2.layout.width = '500px'
                        
                panel = widgets.HBox([btn1, btn2])
            

                que = Image('question.png')
                display(que)
                bottom_area.append_display_data(panel)
            
                display(bottom_area)
    
            
                re         = wait_for_event(timeout=3)
                # re = input("which side has more dots? left or right? (press l or r on keyboard)")
            
        
                end_time   = time.time()
                time_taken = end_time - start_time

                ratio = stimuli_ratio_dict[stim[i]]
                list_ratio.append(ratio)
                track.append(stim[i])
    
               # tracking time window for answering 
                # if out of 3s: labeled as mising answers
           
                if time_taken <= 3.0:
                    answer.append(re['description'])
                else:
                    answer.append('missing')
    
                # check valid answer for scoring and collect the type of response 
                if answer[len(answer)-1] == stimuli_dict[stim[i]]:
                    score +=1
                    rematrix.append(1)
                elif answer[len(answer)-1] == 'missing':
                     rematrix.append(-3)
                else:
                    score = score
                    rematrix.append(0)
                    
                # collect time used per trial 
                rt.append(time_taken)
                clear_output()
          
           

    _dict = {'score': score, 'button_response': answer, 'RT': rt, 'response_cat':rematrix, 'Stimuli_ratio': list_ratio, 'stim_used': track}
    
    result_df       = pd.DataFrame(_dict)
    result_df_tojsn = result_df.to_json()

    result_dict = {'Participant ID': id, 'score': score, 'gender': gender, 'result_json': result_df_tojsn}

    return result_dict


def data_consent():
        data_consent_info = """DATA CONSENT INFORMATION:
        
        Please read:
        
        we wish to record your response data
        
        to an anonymised public data repository.
        
        Your data will be used for educational teaching purposes
        
        practising data analysis and visualisation.
        
        Please type yes in the box below if you consent to the upload."""
        
        print(data_consent_info)
        
        result = input("> ")
        
        if result == "yes":
            
            print("Thanks for your participation.")
            
            print("Please contact philip.lewis@ucl.ac.uk")
            
            print("If you have any questions or concerns")
            
            print("regarding the stored results.")
        
        else:
        
        # end code execution by raising an exception
        
            raise(Exception("User did not consent to continue test."))


def id_instruction():
    id_instructions = """
    
    Enter your anonymised ID
    
    To generate an anonymous 4-letter unique user identifier please enter:
    
    - two letters based on the initials (first and last name) of a childhood friend
    
    - two letters based on the initials (first and last name) of a favourite actor / actress
    
    e.g. if your friend was called Charlie Brown and film star was Tom Cruise
    
    then your unique identifer would be CBTC
    
    """
    
    print(id_instructions)
    
    user_id = input("> ")
    
    print("User entered id:", user_id)

    return user_id


def run_ans():

    data_consent()
    clear_output()
    
    id = id_instruction()
    clear_output()
    
    all_ = ans_test(id)
    send_to_google_form(data_dict = all_, 
                        form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSe-7g4EraDqz4HAUI0o1ed2inaMEJ3rWC-wzeWVN9RksPwqJA/viewform')
    
    return 
