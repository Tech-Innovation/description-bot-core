import configparser


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
