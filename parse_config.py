import os
import logging

from pathlib import Path
from functools import reduce, partial
from operator import getitem
from datetime import datetime
from logger import setup_logging
from utils import read_conf, write_conf
from datetime import datetime


class ConfigParser(object):
    def __init__(self, config, save_dir='saved'):
        """
        description:
            class to parse configuration json/yaml file.
        
        params:
            config: Dict containing configurations
        """
        self._config = config
        
        
        # set log_dir
        # and set experience_name and run_id
        save_dir = Path(save_dir)
        
        self._exper_name = config['name']
        self._run_id = datetime.now().strftime(r'%y%m%d')
        self._cfg_dir = save_dir / 'config' / self.exper_name / self.run_id
        self._log_dir = save_dir / 'log' / self.exper_name / self.run_id
        self._result_dir = save_dir / 'result' / self.exper_name / self.run_id
        
        # make directory for saving log.
        self.cfg_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        
        # save current config file.
        write_conf(self.config, self.cfg_dir / 'config.yaml')
        
        # configure logging module
        setup_logging(self.log_dir)
        self.log_levels = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG
        }
        
    @classmethod
    def from_args(cls, args):
        if not isinstance(args, tuple):
            args, _ = args.parse_known_args()
        
        message = "Configuration file need to be specified. Add '-c config.json', for example."
        assert args.config is not None, message
        
        cfg_path = args.config
        config = read_conf(cfg_path)
        config.update(vars(args))    
        return cls(config)
    
    def get_logger(self, name, verbosity=2):
        msg_verbosity = 'verbosity option {} is invalid. Valid options are {}.'.format(verbosity, self.log_levels.keys())
        assert verbosity in self.log_levels, msg_verbosity
        logger = logging.getLogger(name)
        logger.setLevel(self.log_levels[verbosity])
        return logger

    def init_obj(self, name, module, *args, **kwargs):
        module_name = self[name]['type']
        module_args = dict(self[name]['args'])
        assert all([k not in module_args for k in kwargs]), 'Overwriting kwargs given in config file is not allowed'
        
        module_args.update(kwargs)
        return getattr(module, module_name)(*args, **module_args)
    
    def __getitem__(self, name):
        return self.config[name]
    
    @property
    def config(self):
        return self._config    
    
    @property
    def exper_name(self):
        return self._exper_name
    
    @property
    def run_id(self):
        return self._run_id
    
    @property
    def cfg_dir(self):
        return self._cfg_dir
    
    @property
    def log_dir(self):
        return self._log_dir
    
    @property
    def result_dir(self):
        return self._result_dir