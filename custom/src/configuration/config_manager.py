import configparser
import datetime
from typing import List

from core.ball import BallClass


class ConfigManager:
    def __init__(self, config_path) -> None:
        self.__config = configparser.ConfigParser()
        self.__config.read(config_path)
        self.__config_path = config_path

    def get(self, section, key):
        return self.__config[section][key]

    def getint(self, section, key):
        return self.__config.getint(section, key)

    def getfloat(self, section, key):
        return self.__config.getfloat(section, key)

    def getboolean(self, section, key):
        return self.__config.getboolean(section, key)

    def gethours(self, section, key, **kwargs):
        return self.__config._get_conv(
            section,
            key,
            self._convert_to_array_of_hours,
            raw=False,
            vars=None,
            fallback=object(),
            **kwargs
        )

    def _convert_to_array_of_hours(self, value: str):
        try:
            return [
                datetime.datetime.strptime(x.strip(), "%H:%M") for x in value.split(",")
            ]
        except ValueError:
            raise ValueError("Not a valid list of hours: %s" % value)

    def getballclasses(self, section, key, **kwargs) -> List[BallClass]:
        return self.__config._get_conv(
            section,
            key,
            self._convert_to_array_of_ballclasses,
            raw=False,
            vars=None,
            fallback=object(),
            **kwargs
        )

    def _convert_to_array_of_ballclasses(self, value: str):
        try:
            return [
                BallClass(x.strip().split("@")[0], x.strip().split("@")[1:])
                for x in value.split(",")
            ]
        except ValueError:
            raise ValueError("Not a valid list of ball types: %s" % value)

    def getavailablesizes(self, section, key, **kwargs):
        return self.__config._get_conv(
            section,
            key,
            self._convert_to_array_of_availablesizes,
            raw=False,
            vars=None,
            fallback=object(),
            **kwargs
        )

    def _convert_to_array_of_availablesizes(self, value: str):
        try:
            return [x.strip() for x in value.split(",")]
        except ValueError:
            raise ValueError("Not a valid list of available sizes: %s" % value)

    def set(self, section, key, value):
        self.__config[section][key] = value

    def save(self):
        with open(self.__config_path, "w") as configfile:
            self.__config.write(configfile)

    def sections(self):
        return self.__config.sections()

    def options(self, section):
        return self.__config.options(section)

    def items(self, section):
        return self.__config.items(section)

    def has_section(self, section):
        return self.__config.has_section(section)

    def has_option(self, section, option):
        return self.__config.has_option(section, option)

    def add_section(self, section):
        self.__config.add_section(section)

    def remove_section(self, section):
        self.__config.remove_section(section)

    def remove_option(self, section, option):
        self.__config.remove_option(section, option)

    def __str__(self):
        return str(self.__config)
