from warnings import warn
import pkg_resources
import logging

class Logger:
    # Singleton pattern, for global access once instantiated by a main method
    _instance = None
    _logger_filename = 'data/app.log'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False       

        return cls._instance

    def __init__(self):
        if self._initialized:
            warn('Accessing existing instance of Config', UserWarning)
            return
    
        logger_filename = pkg_resources.resource_filename('config', Logger._logger_filename)

        logging.basicConfig(
            filename=logger_filename,
            encoding='utf-8',
            filemode='a',
            format='{asctime} - {levelname} - {message}',
            style='{',
            datefmt='%Y-%m-%d %H:%M',
            level=logging.INFO
        )
        
        self._initialized = True

    def log(self, message):
        # logging.warning(message)
        logging.info(message)
