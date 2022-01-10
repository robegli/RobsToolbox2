import datetime
import re
import time
import os
import logzero
import functools
import pprint

DEBUG = logzero.DEBUG           # 10
INFO = logzero.INFO             # 20
WARN = logzero.WARN             # 30
ERROR = logzero.ERROR           # 40
CRITICAL = logzero.CRITICAL     # 50

log_format = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s ' \
             '%(funcName)s :: %(message)s'
logzero.setup_default_logger(formatter=logzero.LogFormatter(fmt=log_format))
log = logzero.logger


def pp(*args, **kwargs):
    print(pprint.pformat(*args, **kwargs))


def my_time(func):
    """
    Wrapper to display the function runtime
    :param func: Function to be wrapped
    :return:
    """

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        loglevel = args[0].__dict__.get('_loglevel', None)
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        if loglevel is None:
            print(f"{func.__name__} Elapsed time: {elapsed_time:0.4f} seconds")
        else:
            if loglevel <= 10:
                print(f"{func.__name__} Elapsed time: {elapsed_time:0.4f} seconds")
        return value

    return wrapper_timer


def my_async_time(func):
    """
    Wrapper to display asyncio function runtime
    :param func:
    :return:
    """

    @functools.wraps(func)
    async def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        loglevel = args[0].__dict__.get('_loglevel', None)
        # print("loglevel", loglevel)
        value = await func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        if loglevel is None:
            print(f"{func.__name__} Elapsed time: {elapsed_time:0.4f} seconds")
        else:
            if loglevel <= 10:
                print(f"{func.__name__} X Elapsed time: {elapsed_time:0.4f} seconds")
        return value

    return wrapper_timer


def run_in_loop(f):
    # Run async coroutine in async loop, unless loop already running
    def wrapper(*args, **kwargs):
        api_handler = args[0]
        if api_handler.loop.is_running():
            return f(*args, **kwargs)
        else:
            print(f"Running {f.__name__} in async loop")
            return api_handler.loop.run_until_complete(f(*args, **kwargs))
    return wrapper


class EnvironmentTools:

    @staticmethod
    def get_environ(variable: str = "MERAKI_DASHBOARD_API_KEY") -> str or None:
        """
        Retrieve OS environmental variable.
        :param variable: str, desired variable name
        :return: str, desired variable or None
        """
        try:
            osvar = os.environ[variable]
            log.debug(f"Returning OS variable '{variable}'.")
            return osvar
        except KeyError:
            log.warning(f"Unable to find OS variable '{variable}'.")
        return None

    @staticmethod
    def check_dir(outfolder: str = './_NewFolder', create_folder: bool = False) -> bool:
        """
        CHeck existence of directory
        :param outfolder: path to desired folder
        :param create_folder: bool, create folder if it does not exist
        :return: bool
        """
        exists = os.path.isdir(outfolder)
        if exists:
            log.debug(f"Folder '{outfolder}' already exists.")
            return True
        log.debug(f"Folder '{outfolder}' does not exist.")
        try:
            os.mkdir(outfolder)
            log.debug(f"Folder '{outfolder}' created.")
            return True
        except Exception as e:
            log.warning(f"Unable to create directory '{outfolder}': {e}")
        return False

    @staticmethod
    def check_file(filename: str = 'testfile.txt', create_file=False) -> bool:
        """
        Check if file exists
        :param filename: path to file
        :param create_file: bool, create file if it does not exist
        :return: bool
        """
        exists = os.path.isfile(filename)
        if exists:
            log.debug(f"File '{filename}' already exists.")
            return True
        log.debug(f"File '{filename}' does not exist.")
        if create_file:
            try:
                with open(filename, 'w') as f:
                    log.debug(f"File '{filename}' created.")
                return True
            except Exception as e:
                log.warning(f"Unable to create file '{filename}': {e}")
        return False


class StringTools:
    REGX_IP = r'^((\d|1?\d{2}|2[0-4]\d|25[0-5])\.){3}(\d|1?\d{2}|2[0-4]\d|25[0-5])$'
    REGX_MAC = r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$'
    REGX_MACALT = r'^([0-9a-fA-F]{2}-){5}[0-9a-fA-F]{2}$'
    REGX_JUNOSPORT = r'ge-\d\/\d\/(\d|[1-3]\d|4[0-7]'

    @staticmethod
    def convert_mac(mac: str, upper: bool = False) -> str:
        """
        Convert MAC address to standard 'XX:XX:XX:XX:XX:XX'
        :param mac:
        :return:
        """
        output = ''
        if re.findall(StringTools.REGX_MAC, mac):
            output = mac.replace(':', '-')
        elif re.findall(StringTools.REGX_MACALT, mac):
            output = mac.replace('-', ':')
        elif len(mac) == 12:  # no separation
            mac = [mac[i:i + 2] for i in range(0, len(mac), 2)]
            output = ':'.join(mac)
        else:
            output = ''
        if upper:
            return output.upper()
        return output

    @staticmethod
    def is_ipv4_address(ip: str) -> bool:
        """
        Return bool if IP address
        :param ip:
        :return:
        """
        if re.findall(StringTools.REGX_IP, ip):
            return True
        return False

    @staticmethod
    def sort_ipv4_addresses(ips: list[str], verify: bool = True) -> list[str]:
        """
        Sort a list of IPv4 addresses (strings) from last octet to first.
        :param ips: list of IP strings
        :param verify: Verify that values are valid IPv4 addresses.
        :return: Sorted list of Strings
        """
        if verify:
            ips = [ip for ip in ips if StringTools.is_ipv4_address(ip)]
        for i in range(3, -1, -1):
            ips = sorted(ips, key=lambda x: int(x.split('.')[i]))
        return ips

    @staticmethod
    def xstr(original: str, replacement: str = '') -> str:
        """
        Convert 'None' type value to empty string, or return original as string
        :param original: str, value to check
        :param replacement: str, replacement value
        :return: str
        """
        if original is None:
            return replacement
        return str(original)

    @staticmethod
    def convert_str_to_datetime(datestr: str) -> datetime.datetime:
        """Convert date string to datetime.datetime object"""
        return datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S.%f")


class DataHandler:

    @staticmethod
    def list_of_dict_to_dict_of_dict(original_list: list[dict], key_str: str) -> dict:
        """Turn list of dicts into a dictionary of dicts using key value
        key_value should be a non-repeated value, such as item[id]"""
        new_dict: dict = {}
        try:
            for dictionary in original_list:
                new_dict[dictionary[key_str]] = item

            return new_dict
        except KeyError as e:
            log.error(f"{key_str} not a valid key. {e}")
            return {}

    @staticmethod
    def search_list_of_dicts_for_value_using_next(lst: list, value, key: str) -> dict:
        """Mostly here to keep Next() visible -- Will only find first available match"""
        try:
            item = next((lst[item] for item in lst if value in list[item][key]), {})
        except KeyError as e:
            log.error(f'Keyerror: {key}, {e}')
            item = {}
        return item

    @staticmethod
    def search_list_of_dicts_for_str_using_re(lst: list, value: str, key: str) -> list:
        """
        Find items in dict using keyword/values - can find partial string values
        Value can be reg expression - CASE SENSITIVE
        """
        value = RTB.xstr(value)  # allow user to enter digits, allows search for None type objects
        output = [item for item in lst if re.findall(value, RTB.xstr(item[key], ''))]
        return output

    @staticmethod
    def search_list_of_dicts_for_string_using_in(lst: list, value: str, key: str) -> list:
        """ FInd list items using keyword/values. Can be used to find partial string values."""
        output = []
        for item in lst:
            if value in RTB.xstr(item.get(key, None)):
                output.append(item)
        return output

    @staticmethod
    def search_list_of_dicts_for_value_using_equality(lst: list, value: str or int or float, key: str) -> list:
        """Find list items using keyword/values.  Find EXACT strings/int/float"""
        output = []
        for item in lst:
            if value == item.get(key, None):  # <removed xstr
                output.append(item)
        return output

    @staticmethod
    def choose_from_list(choices: list, prompt: str = "Choose number from list: ", offset: int = 0):
        print(prompt)
        for enum, choice in enumerate(choices):
            print(f'{enum + offset:3}: {choice}')
        selection = input("Selection (or Q): ")
        if selection.upper() == 'Q':
            return None
        try:
            selection = int(selection)
            return choices[selection - offset]
        except ValueError as e:
            print('Incorrect selection ')
        except IndexError as e:
            print('Selection out of range ')
        return RTB.choose_from_list(choices=choices, prompt=prompt, offset=offset)

    @staticmethod
    def choose_from_list_of_dicts(choices: list[dict],
                                  keys: list[str],
                                  offset: int = 0,
                                  prompt: str = "Choose number from list"):
        print(prompt)
        for enum, choice in enumerate(choices):
            line = f'{enum + offset:3}'
            for key in keys:
                line += f"   {key}:{RTB.xstr(choice.get(key, None)):<10}"
            print(line)

        selection = input('Selection (or Q): ')
        if selection.upper() == 'Q':
            return []
        try:
            selection = int(selection)
            return [choices[selection - offset]]
        except ValueError as e:
            print('Incorrect selection ')
        except IndexError as e:
            print("Selection out of range ")
        return RTB.choose_from_list_of_dicts(choices=choices, keys=keys, offset=offset, prompt=prompt)

    @staticmethod
    def print_dict(data: dict = None):
        if dict is None:
            return
        for key, val in data.items():
            print(f"{key}: {val}")


class RTB(EnvironmentTools, StringTools, DataHandler):
    pass


class PSGTools:

    # TODO: move these to their own module, tools for psg.  no need to keep here.

    @staticmethod
    def offset_window(location: tuple[int or None, int or None],
                      offset: tuple[int or None, int or None]) -> tuple:
        """Offset window launch location"""
        location: list[int, int] = list(location)
        if location[0] is not None and offset[0] is not None:
            location[0] += offset[0]
        if location[1] is not None and offset[1] is not None:
            location[1] += offset[1]
        return tuple(location)

    @staticmethod
    def layout_tester(layout: list[list], timeout: int = None):
        pass


if __name__ == '__main__':
    tools = RTB()
    # iplist = ['255.255.255.0',
    #           '172.16.0.3',
    #           '10.10.10.2',
    #           '10.10.10.1',
    #           '192.168.1.255']
