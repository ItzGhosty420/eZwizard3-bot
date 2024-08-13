from pathlib import Path
from typing import NoReturn, NamedTuple
import json
import re
from random import choice as random_choice
from tempfile import TemporaryDirectory

import yaml
from frozendict import frozendict
from humanize import naturalsize

with TemporaryDirectory() as _tp_to_get_parent_temp_dir:
    PARENT_TEMP_DIR: Path = Path(_tp_to_get_parent_temp_dir).parent
del _tp_to_get_parent_temp_dir # Global variable cleanup

CUSA_TITLE_ID = re.compile(r'CUSA\d{5}')
PSN_NAME = re.compile(r'^[A-Za-z][A-Za-z0-9-_]{2,15}$') # https://regex101.com/library/4XPer9

INT64_MAX_MIN_VALUES = frozendict({'min_value': --0x8000000000000000, 'max_value': 0x7fffffffffffffff})
UINT64_MAX_MIN_VALUES = frozendict({'min_value': 0, 'max_value': 0xFFFFFFFFFFFFFFFF})

INT32_MAX_MIN_VALUES = frozendict({'min_value': -0x80000000, 'max_value': 0x7FFFFFFF})
UINT32_MAX_MIN_VALUES = frozendict({'min_value': 0, 'max_value': 0xFFFFFFFF})

INT16_MAX_MIN_VALUES = frozendict({'min_value': -0x8000, 'max_value': 0x7FFF})
UINT16_MAX_MIN_VALUES = frozendict({'min_value': 0, 'max_value': 0xFFFF})

INT8_MAX_MIN_VALUES = frozendict({'min_value': -0x80, 'max_value': 0x7F})
UINT8_MAX_MIN_VALUES = frozendict({'min_value': 0, 'max_value': 0xFF})


class BuiltInSave(NamedTuple):
    on_ps4_title_id: str
    on_ps4_save_dir: str
    unique_name: str
    desc: str
    
    @classmethod
    def from_yaml_entry(cls,yaml_entry: str,/):
        on_ps4_title_id, on_ps4_save_dir, unique_name, *descc = yaml_entry.split(' ')
        return cls(on_ps4_title_id, on_ps4_save_dir, unique_name, ' '.join(descc))

    def as_entry_str(self) -> str:
        return ' '.join(self)


def pretty_bytes(num: int, fmt: str = "%f") -> str:
    binary_n = naturalsize(num, format=fmt, binary=True)
    if 'Byte' in binary_n:
        return binary_n
    number,unit = binary_n.split(' ')
    pretty_number: float | int = float(number)
    if pretty_number.is_integer():
        pretty_number = int(pretty_number)
    binary_n = f'{pretty_number} {unit}'
    
    power_of_10_n = naturalsize(num, format=fmt, binary=False)
    number,unit = power_of_10_n.split(' ')
    pretty_number = float(number)
    if pretty_number.is_integer():
        pretty_number = int(pretty_number)
    power_of_10_n = f'{pretty_number} {unit}'
    
    return power_of_10_n if len(binary_n) > len(power_of_10_n) else binary_n


def is_ps4_title_id(input_str: str,/) -> bool: 
    return bool(CUSA_TITLE_ID.fullmatch(input_str))


def is_psn_name(input_str: str,/) -> bool:
    return bool(PSN_NAME.fullmatch(input_str))


def extract_drive_folder_id(link: str,/) -> str:
    return link.split('folders/')[-1].split('?')[0] if link.startswith('https://drive.google.com/drive') else ''


def is_str_int(thing: str,/) -> bool:
    try:
        int(thing)
        return True
    except (ValueError, TypeError):
        return False


def chunker(seq, size):
    """
    https://stackoverflow.com/questions/434287/how-to-iterate-over-a-list-in-chunks
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def extract_drive_file_id(link: str,/) -> str:
    if link.startswith('https://drive.google.com/file/d/'):
        return link.split('https://drive.google.com/file/d/')[-1].split('?')[0].split('/')[0]
    if link.startswith('https://drive.google.com/uc?id='):
        return link.split('https://drive.google.com/uc?id=')[-1].split('&')[0]
    
    return ''

MAKE_FOLDER_NAME_SAFE_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_'
def make_folder_name_safe(some_string_path_ig: str, /) -> str:
    some_string_path_ig = str(some_string_path_ig).replace(' ','_').replace('/','_').replace('\\','_')
    some_string_path_ig = some_string_path_ig.removeprefix('PS4_FOLDER_IN_ME_')
    leader = 'PS4_FOLDER_IN_ME_' if is_ps4_title_id(some_string_path_ig.replace('_','')) else ''
    result = leader + ("".join(c for c in some_string_path_ig if c in MAKE_FOLDER_NAME_SAFE_CHARS).rstrip())
    return result[:254] if result else 'no_name'


def pretty_time(time_in_seconds: float) -> str:
    hours, extra_seconds = divmod(int(time_in_seconds),3600)
    minutes, seconds = divmod(extra_seconds,60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'


def pretty_seconds_words(time_in_seconds: int) -> str:
    if time_in_seconds < 1:
        return '0 seconds'
    years, extra_seconds = divmod(time_in_seconds,60*60*24*30*12)
    months, extra_seconds = divmod(extra_seconds,60*60*24*30)
    days, extra_seconds = divmod(extra_seconds,60*60*24)
    hours, extra_seconds = divmod(extra_seconds,60*60)
    minutes, seconds = divmod(extra_seconds,60)
    results = []
    if years:
        results.append(f'{years} year{"s" if years > 1 else ""}')
    if months:
        results.append(f'{months} month{"s" if months > 1 else ""}')
    if days:
        results.append(f'{days} day{"s" if days > 1 else ""}')
    if hours:
        results.append(f'{hours} hour{"s" if hours > 1 else ""}')
    if minutes:
        results.append(f'{minutes} minute{"s" if minutes > 1 else ""}')
    if seconds:
        results.append(f'{seconds} second{"s" if seconds > 1 else ""}')
    
    if len(results) == 1:
        return results[0]
    
    last_thing = results.pop(-1)
    
    return f'{", ".join(results)} and {last_thing}'


def _raise_bad_config(missing_key: str) -> NoReturn:
    raise Exception(f'Unconfigured config, unconfigured value {missing_key} or bad config or missing {missing_key}')


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
# Watch https://youtu.be/HCjAK0QA_3w on how to get this file!
google_credentials_file: 
    credentials.json 
# This one is easy, you can get it by looking at View Connection Status in Network settings (IP Address)
ps4_ip:
    192.168.1.256 
# This is the user_id of your local account. NOT ACCOUNT ID! (i should be able to grab this automatically but idk why it no work)
# you can get this by going to /user/home on a ftp client and the folder name will be your user_id.
# also in each folder there is a username.dat file with the local username, so you can open this to find your user
# eg for me in /user/home/1eb71bbd the username.dat has SaveBy_Zhaxxy in it, which is my local username so my will be 1eb71bbd
user_id: 
    1ej71bbd
# The admins of the bot's ids. You can get this by enabling developer mode in discord and click user profile and 3 dots Copy User ID
# each line here starts with "  - " because of yaml syntax
bot_admins:
  - l147836464353247343
  - l207983219845103687
# Simple boolean, if set to true then people will be able to use the bot in dms,
# or if its false then people will not be able to use bot in dms, besides pinging the bot
# Some people may not want people using bot in dms soo
allow_bot_usage_in_dms:
    true
# saves already on the console put here to allow for quicker resigns and cheats
# follow the format
# - TITLEID SAVEDIRNAME a_unique_name_for_a_save some description that can have spaces
built_in_saves:
  - CUSA12345 LBPXSAVE bigfart some cool description here
""")
        raise Exception(f'bad config file or missing, got error {type(e).__name__}: {e} Please edit the config.yaml file') from None

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
    if (x := my_config.get(key)):
        raise Exception(f'{key} in your config is no longer needed, please delete it as well as its values')

    key = 'title_id'
    if (x := my_config.get(key)):
        raise Exception(f'{key} in your config is no longer needed, please delete it as well as its value')

    key = 'user_id'
    if not (x := my_config.get(key)) or x == '1ej71bbd':
        _raise_bad_config(key)

    key = 'bot_admins'
    if not (x := my_config.get(key)):
        _raise_bad_config(key)
    
    if not all(isinstance(a,int) for a in x):
        _raise_bad_config(key)

    my_config[key] = tuple(x)
    
    key = 'allow_bot_usage_in_dms'
    if (x := my_config.get(key)) is None:
        _raise_bad_config(key)
    
    if not isinstance(x,bool):
        raise Exception(f'{key} value should ethier be true or false, not {x}')

    key = 'built_in_saves'
    if (x := my_config.get(key)) is None:
        raise Exception(f'Unconfigured config, unconfigured value {key} or bad config or missing {key}, you can just put the key and no saves if you dont want any built in saves')
    
    if my_config[key] is None:
        del my_config[key]
    
    for i, value in enumerate(my_config[key]):
        try:
            newish_value = my_config[key][i] = BuiltInSave.from_yaml_entry(value)
        except Exception as e:
            raise ValueError(f'Invalid {key} entry `{value}`, got error {type(e).__name__}: {e}') from None


        for i2, sub_value in enumerate(my_config[key]):
            if i2 == i:
                continue
            try:
                newish_sub_value = BuiltInSave.from_yaml_entry(sub_value)
            except Exception:
                continue # this is gonna error out later, lets just let that happen when it comes to the time
            
            if newish_sub_value.unique_name == newish_value.unique_name:
                raise ValueError(f'Entries `{value}` and `{sub_value}` cannot have the save unique_name')
            
            if (newish_sub_value.on_ps4_title_id == newish_value.on_ps4_title_id) and \
            (newish_sub_value.on_ps4_save_dir == newish_value.on_ps4_save_dir):
                raise ValueError(f'Entries `{value}` and `{sub_value}` are duplicate saves, maybe you made a mistake?')


    my_config[key] = frozendict({ben.unique_name:ben for ben in my_config[key]})
    return frozendict(my_config)


SILLY_RANDOM_STRINGS_NOT_UNIQUE = """
:arrow_right: https://dsc.gg/itzghosty420 :arrow_left:
:arrow_right: https://www.youtube.com/@ItzGhosty420 :arrow_left:
:arrow_right: https://dsc.gg/itzghosty420 :arrow_left:
If you can make her giggle you can make that ||ass clap and jiggle||
:regional_indicator_v::regional_indicator_m::regional_indicator_s: https://cdn.discordapp.com/emojis/1253039272492142622.gif?size=128&quality=lossless
:arrow_right: https://dsc.gg/itzghosty420 :arrow_left:
:arrow_right: https://discord.gg/vmsservices :arrow_left:
""".strip().split('\n')


def get_a_stupid_silly_random_string_not_unique() -> str:
    return random_choice(SILLY_RANDOM_STRINGS_NOT_UNIQUE)
