import datetime
import json
import yaml
import os.path
from abc import ABC, abstractmethod

from toolbox import RTB, log, pp


def check_required_files(filelist: dict):
    for key, file in filelist.items():
        if not os.path.exists(file):
            if file.endswith('.json'):
                FileHandlerJSON.save_data_to_file([], filename=file)
            if file.endswith('.yml'):
                FileHandlerYAML.save_data_to_file([], filename=file)


class FileHandler(ABC):
    extension = ''

    def check_filename(self, filename):
        return filename if filename.endswith(self.extension) else filename + self.extension

    def date_filename(self, filename: str, month: int = None, day: int = None, year: int = None) -> str:
        """ return dated filename"""
        today = datetime.datetime.today()
        month = month if month is not None else today.month
        mont = str(month).rjust(2, '0')
        day = day if day is not None else today.day
        day = str(day).rjust(2, '0')
        year = year if year is not None else today.year
        year = str(year)[-2:]
        filename = f'{filename}_{year}_{month}_{day}'
        return self.check_filename(filename)

    @abstractmethod
    def save_data_to_file(self, data: list or dict, filename: str, comment: str = None) -> bool:
        """Save data list or dict to file"""

    @abstractmethod
    def load_dict_from_file(self, filename: str = None, data_only: bool = True) -> dict:
        """load dict object from file"""

    @abstractmethod
    def load_list_from_file(self, filename: str = None, data_only: bool = True) -> dict:
        """Load list object from file"""


class FileHandlerJSON(FileHandler):
    """ File handling for .json type files"""
    extension = '.json'

    def save_data_to_file(self, data: list or dict, filename: str, comment: str = None) -> bool:
        comment = RTB.xstr(comment, '')
        filename = filename if filename.endswith(self.extension) else filename + self.extension
        data = {'fname': filename, 'comment': comment, 'date': str(datetime.datetime.today()), 'data': data}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True

    @staticmethod
    def _load_any_from_json_file(filename, data_only: bool = True) -> dict or list:
        if not RTB.check_file(filename):
            return None
        with open(filename, 'r') as file:
            data = json.load(file)
            pp(data)
            if data.get('data', None):
                data['date'] = RTB.convert_str_to_datetime(data['date'])
            log.debug(f'Loaded file{filename}, dated: {data.get("date", None)}')
            if data_only:
                return data.get('data', None)
        return data

    def load_dict_from_file(self, filename: str = None, data_only: bool = True) -> dict:
        """load dict object from .json file"""
        filename = filename if filename.endswith(self.extension) else filename + self.extension
        data = self._load_any_from_json_file(filename=filename, data_only=data_only)
        print(type(data))
        pp(data)
        if type(data) is dict:
            return data
        print('did not return data')
        return {}

    def load_list_from_file(self, filename: str = None, data_only: bool = True) -> list:
        """load list object from .json file"""
        filename = filename if filename.endswith(self.extension) else filename + self.extension
        data = self._load_any_from_json_file(filename=filename, data_only=data_only)
        if type(data) is list:
            #Todo: check if data_only, may cause confusion, failure
            return data
        return []


class FileHandlerYAML(FileHandler):
    """File handling for .yml file type"""
    extension = '.yml'

    def save_data_to_file(self, data: list or dict, filename: str, comment: str = None) -> bool:
        comment = RTB.xstr(comment, '')
        filename = self.check_filename(filename)
        data = {'fname': filename, 'comment': comment, 'date': str(datetime.datetime.today()), 'data': data}
        with open(filename, 'w') as f:
            yaml.safe_dump(data, f)
        return True

    @staticmethod
    def _load_any_from_yml_file(filename: str = None, data_only: bool = True) -> dict:
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
        if data_only:
            return data.get('data', None)
        return data

    def load_dict_from_file(self, filename: str = None, data_only: bool = True) -> dict:
        filename = self.check_filename(filename)
        data = self._load_any_from_yml_file(filename=filename, data_only=data_only)
        if type(data) is dict:
            return data
        return {}

    def load_list_from_file(self, filename: str = None, data_only: bool = True) -> dict:
        filename = self.check_filename(filename)
        data = self._load_any_from_yml_file(filename=filename, data_only=data_only)
        if type(data) is list:
            return data
        return []


class Tester:

    def __init__(self, fh: FileHandler = None, filename: str = 'test123'):
        self.filehandler = fh
        self.datadict = {'hello': 'there'}
        self.datalist = ['hi', 'how', 'are', 'ya']
        self.filename = filename

    def ret_filename(self):
        filename = self.filename if self.filename.endswith(self.filehandler.extension) \
            else self.filename + self.filehandler.extension
        return filename

    def check_test_exists(self, filename):
        print(f'exists: {os.path.exists(filename)}')

    def del_test(self):
        filename = self.ret_filename()
        if os.path.exists(filename):
            self.check_test_exists(filename)
            os.remove(filename)
            print(f"Deleted")
            self.check_test_exists(filename)
        else:
            print(f'\n Unable to del {filename}, does not exist')

    def save_dict_test(self):
        filename = self.ret_filename()
        print('\nTestSaveDict')
        self.check_test_exists(filename)
        print('Dict save')
        self.filehandler.save_data_to_file(self.datadict, self.filename)
        self.check_test_exists(filename)

    def load_dict_test(self):
        filename = self.ret_filename()
        print('\nTestLoadDict')
        self.check_test_exists(filename)
        if os.path.exists(filename):
            data = self.filehandler.load_dict_from_file(self.filename)
            print(type(data))
            pp(data)
        else:
            print(f'Unable to open file {filename} - does not exist')

    def save_list_test(self):
        filename = self.ret_filename()
        print('\nTestSaveList')
        self.check_test_exists(filename)
        print('List save')
        self.filehandler.save_data_to_file(self.datalist, self.filename)
        self.check_test_exists(filename)

    def load_list_test(self):
        filename = self.ret_filename()
        print('\nTestLoadList')
        self.check_test_exists(filename)
        if os.path.exists(filename):
            data = self.filehandler.load_list_from_file(self.filename)
            print(type(data))
            pp(data)
        else:
            print(f'unable to open file {filename} - does not exist')

    def tests(self):

        self.save_dict_test()
        self.load_dict_test()
        self.del_test()
        print('  $$$$  ')
        self.save_list_test()
        self.load_list_test()
        self.del_test()


def testing():
    tests = [FileHandlerJSON, FileHandlerYAML]
    for test in tests:
        print('######################')
        print(test.__name__)
        test = Tester(test())
        test.tests()


if __name__ == '__main__':
    testing()
