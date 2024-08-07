import pkg_resources
import csv
from warnings import warn

class Config:
    # Singleton pattern, for global access once instantiated by a main method
    _instance = None
    _specifications_filename = 'data/specifications.csv'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False       

        return cls._instance

    def __init__(self):
        if self._initialized:
            warn('Accessing existing instance of Config', UserWarning)
            return
    
        specifications_filename = pkg_resources.resource_filename('config', Config._specifications_filename)
        self.constants = Config.load_constants(specifications_filename)
        self._initialized = True

    @staticmethod
    def load_constants(specifications_filename):
        constants = {}
        with open(specifications_filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                data_type_function = Config.get_data_type_function_from_str(row['data_type'].strip())
                value = data_type_function(row['value'])
                constants[name] = value
        return constants
       
    @staticmethod
    def get_data_type_function_from_str(data_type_str):
        default = str
        if data_type_str == 'float':
            return float
        elif data_type_str == 'str':
            return str
        elif data_type_str == 'int':
            return int
        elif data_type_str == '':
            warn('data_type field is empty. Defaulting to str() function.', UserWarning)
            return default
        else:
            warn('Could not match data_type. Defaulting to str() function.', UserWarning)
            return default
        
    def set_max_length(self, max_length=None):
        if max_length is not None:
            assert isinstance(max_length, int)
            assert max_length > 0
            assert max_length <= 20
            self['MAX_LENGTH'] = max_length
        else:
            self['MAX_LENGTH'] = self['DEFAULT_MAX_LENGTH']

        self.set_probability_of_extending_route()
        
    def set_probability_of_extending_route(self):
        assert 'MAX_LENGTH' in self.constants
        assert 'MAX_LENGTH_PROBABILITY' in self.constants
        
        max_length = self['MAX_LENGTH']
        max_length_probability = self['MAX_LENGTH_PROBABILITY']
        incremental_length_probability = max_length_probability ** (1.0 / max_length)

        self['PROBABILITY_OF_EXTENDING_ROUTE'] = incremental_length_probability
        
    def get(self, name, provided=None):
        return provided or self[name]

    def __getitem__(self, name):
        return self.constants.get(name)
    
    def __setitem__(self, name, value):
        self.constants[name] = value