import logging

class Logging():
    def __init__(self, logger_name):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        
        # create formatter
        fmt = "%(asctime)s : %(levelname)s : %(filename)s : %(lineno)d : %(message)s"
        datefmt = "%a %d %b %Y %H:%M:%S"
        self.formatter = logging.Formatter(fmt, datefmt)
        
    def print_name(self):
        print(self.logger_name)
        
    def run(self, log_path=None):
        # set default log_path
        if log_path is None:
            log_path = self.logger_name + '.log'
        else:
            log_path += self.logger_name + '.log'
        
        # create file handler
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        
        # add handler and formatter to logger
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)
        
    def debug_msg(self, debug_msg):
        self.logger.debug(debug_msg)
        
    def info_msg(self, info_msg):
        self.logger.info(info_msg)
        
    def warn_msg(self, warn_msg):
        self.logger.warn(warn_msg)
        
    def error_msg(self, error_msg):
        self.logger.error(error_msg)
    
    def critical_msg(self, critical_msg):
        self.logger.critical(critical_msg)