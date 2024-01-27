import configparser
import os

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            open(config_file, 'a').close()
        self.config.read(config_file)

    def save_config(self, section, key, value):
        if isinstance(value, list):
            value = ','.join(value)  # 리스트를 쉼표로 구분된 문자열로 변환
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def load_config(self, section, key):
        return self.config.get(section, key) if self.config.has_section(section) and self.config.has_option(section, key) else ''
