import logging
import json
from pathlib import Path
from datetime import datetime
import config_controller

AGE_WRITE_FORMAT = "{0:%Y-%m-%dT%X.%f%z}"
AGE_READ_FORMAT = "%Y-%m-%dT%X.%f"
DAY_AGE_READ_FORMAT = "%Y-%m-%d"


class FileCache():
    """Simple file cache implementation"""
    _age = None

    @staticmethod
    def read(data_path):
        issue_dict = []

        file = Path(data_path)
        if file.exists():
            logging.info("file %s found", data_path)
            with open(data_path) as json_file:
                try:
                    issue_dict = json.load(json_file)
                    json_file.close()
                except FileExistsError:
                    json_file.close()
                    raise
        else:
            logging.error("file %s not found", data_path)
        return issue_dict

    @staticmethod
    def save(data, data_path):
        with open(data_path, "w") as outfile:
            try:
                json.dump(data, outfile)
                outfile.close()
            except FileExistsError:
                outfile.close()
                raise

        info_path = config_controller.ConfigController.get_info_from_data(data_path)
        FileCache.write_info(info_file_name=info_path)

    @staticmethod
    def write_info(info_file_name):
        _age = datetime.now()

        with open(info_file_name, "w") as age_file:
            age_str = AGE_WRITE_FORMAT.format(_age)
            try:
                age_file.write(age_str)
                age_file.close()
            except FileExistsError:
                age_file.close()
                raise
        return _age

    @staticmethod
    def read_info(file_info):

        file = Path(file_info)
        age = None
        if file.exists():
            logging.info("file %s found", file_info)
            with open(file) as info_file:
                try:
                    age_str = info_file.readlines(1)[0]
                    age = datetime.strptime(age_str, AGE_READ_FORMAT)
                    info_file.close()
                except FileExistsError:
                    info_file.close()
                    raise
        else:
            logging.error("file %s not found", file_info)
        return age


def test_file_cache():
    raise NotImplementedError()
    # assert dylib_info('completely/invalid') is None


def test_age():
    file_path = '../../test/'
    age1 = FileCache.write_info(file_path)
    age2 = FileCache.read_info(file_path)
    assert age1 == age2
    print('test on age file is OK')
    # os.removefile_path+)


if __name__ == '__main__':
    test_age()
