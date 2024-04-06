from pathlib import Path
from typing import NoReturn
import json
import re

import yaml
from frozendict import frozendict

CUSA_TITLE_ID = re.compile(r'CUSA\d{5}')

def is_ps4_title_id(input_str: str,/) -> bool: 
    return bool(CUSA_TITLE_ID.fullmatch(input_str))


def extract_drive_folder_id(link: str,/) -> str:
    return link.split('folders/')[-1].split('?')[0] if link.startswith('https://drive.google.com/drive') else ''


def extract_drive_file_id(link: str,/) -> str:
    if link.startswith('https://drive.google.com/file/d/'):
        return link.split('https://drive.google.com/file/d/')[-1].split('?')[0].split('/')[0]
    if link.startswith('https://drive.google.com/uc?id='):
        return link.split('https://drive.google.com/uc?id=')[-1].split('&')[0]
    
    return ''


def make_folder_name_safe(some_string_path_ig: str, /) -> str:
    some_string_path_ig = str(some_string_path_ig)
    some_string_path_ig = some_string_path_ig.replace(' ','_').replace('/','_').replace('\\','_').replace('\\','_')
    result = "".join(c for c in some_string_path_ig if c.isalnum() or c in ('_','-')).rstrip()
    return result[:254] if result else 'no_name'

def pretty_time(time_in_seconds: float) -> str:
    hours, extra_seconds = divmod(int(time_in_seconds),3600)
    minutes, seconds = divmod(extra_seconds,60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def _raise_bad_config(missing_key: str) -> NoReturn:
    raise Exception(f'Unconfigured config, unconfigured value {missing_key} or bad config')

_SILLY_SAVES = {'some_silly_save0', 'some_silly_save2', 'some_silly_save4', 'some_silly_save6', 'some_silly_save8', 'some_silly_save10', 'some_silly_save12', 'some_silly_save14', 'some_silly_save16', 'some_silly_save18', 'some_silly_save22', 'some_silly_save20'}
def load_config() -> frozendict:

    try:
        with open('config.yaml','r') as f:
            my_config: dict = yaml.load(f,yaml.Loader)
            
    except Exception as e:
        with open('config.yaml','w') as f:
            f.write("""\
# Watch https://youtu.be/GvK-ZigEV4Q on how to get your bot token! 
discord_token: 
    MTIxMzAQk2APdMtqdXTtSfJcD2.GaxeZo.SLW6IWM7qdSxyQhCvClXINFJF4AIbF6oJVahrb
# Go to https://ca.account.sony.com/api/v1/ssocookie while signed into psn and put the string here
ssocookie: 
    glgagbgcSDh3t50ABpfwINS9kfugLPqDY8Lzfz3UabgE2w3OAhss6tWEJCOH54Sm 
# :shrug: Watch https://youtu.be/fkWM7A-MxR0 up untill you get your credentials.json, make sure file in same folder as the program
google_credentials_file: 
    credentials.json 
# This one is easy, you can get it by looking at View Connection Status in Network settings (IP Address)
ps4_ip:
    192.168.1.256 
# You need sacrifice saves in order for this bot to work
# ill probably make a guide on how using save mounter
# each line here starts with "  - " because of yaml syntax
save_dirs:
  - some_silly_save0
  - some_silly_save2
  - some_silly_save4
  - some_silly_save6
  - some_silly_save8
  - some_silly_save10
  - some_silly_save12
  - some_silly_save14
  - some_silly_save16
  - some_silly_save18
  - some_silly_save22
  - some_silly_save20
# The title id of the saves, they all need to be of the same game
title_id: 
    FAKE78699 
# This is the user_id of your local account. NOT ACCOUNT ID! (i should be able to grab this but idk why it no work)
# you can get this by going to /user/home on a ftp client and the folder name will be your user_id.
# also in each folder there is a username.dat file with the local username, so you can open this to find your user
# eg for me in /user/home/1eb71bbd the username.dat has SaveBy_Zhaxxy in it, which is my local username so my will be 1eb71bbd
user_id: 
    1ej71bbd
# The admins of the bot's ids. You can get this by enabling developer mode in discord and click user profile and 3 dots Copy User ID
# each line here starts with "  - " because of yaml syntax
bot_admins:
  - l147836464353247343
  - l207983219845103687""")
        raise Exception(f'bad config file or missing, got error {type(e).__name__}: {e} Please edit the config.yml file') from None

    key = 'discord_token'
    if not (x := my_config.get(key)) or x == 'MTIxMzAQk2APdMtqdXTtSfJcD2.GaxeZo.SLW6IWM7qdSxyQhCvClXINFJF4AIbF6oJVahrb':
        _raise_bad_config(key)

    key = 'ssocookie'
    if not (x := my_config.get(key)) or x == 'glgagbgcSDh3t50ABpfwINS9kfugLPqDY8Lzfz3UabgE2w3OAhss6tWEJCOH54Sm':
        _raise_bad_config(key)

    key = 'google_credentials_file'
    if not (x := my_config.get(key)):
        _raise_bad_config(key)

    try:
        json.loads(Path(x).read_text())
    except Exception as e:
        raise Exception(f'Could not open {key}: {x} or not valid google_credentials_file, got error {type(e).__name__}: {e}') from None

    key = 'ps4_ip'
    if not (x := my_config.get(key)) or x == '192.168.1.256':
        _raise_bad_config(key)

    key = 'save_dirs'
    if not (x := my_config.get(key)):
        _raise_bad_config(key)

    for silly in x:
        if silly in _SILLY_SAVES:
            _raise_bad_config(key)

    my_config[key] = tuple(str(b) for b in x)

    key = 'title_id'
    if not (x := my_config.get(key)) or x == 'FAKE78699':
        _raise_bad_config(key)

    key = 'user_id'
    if not (x := my_config.get(key)) or x == '1ej71bbd':
        _raise_bad_config(key)

    key = 'bot_admins'
    if not (x := my_config.get(key)):
        _raise_bad_config(key)
    
    if not all(isinstance(a,int) for a in x):
        _raise_bad_config(key)

    my_config[key] = tuple(x)

    return frozendict(my_config)
    