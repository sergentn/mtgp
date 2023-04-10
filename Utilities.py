import configparser

class IniLoader:

    def __init__(self, config_filepath):

        self.config = configparser.ConfigParser()
        try:
            with open(config_filepath, encoding="utf-8") as f:
                self.config.read(config_filepath)
        except IOError:
            print(f'No existing configuration file: {config_filepath}')

    def getParam(self, section, param, default_value=None):
        try:
            return self.config[section][param]
        except:
            if (default_value is None):
                print(f'No parameter {param} in section {section}, no default parameter provided.')
                return ''
            else:
                print(f'No parameter {param} in section {section}, loading default: {default_value}')
                return default_value
