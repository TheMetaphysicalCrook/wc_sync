import json
import sys

import editor
import os

class Paths:
	
	docs = os.path.expanduser('~/Documents')
	wc_file = os.path.split(sys.argv[0])[-1]
	wc_install_path = os.path.relpath(os.path.realpath(os.path.abspath(os.path.dirname(__file__))), os.path.expanduser('~/Documents'))


class Config:
	
	filename = '.wcsync'
	
	def __init__(self):
		config = self._load_config()
		self.repo, self.path = None, None
		if config:
			self.repo = config['repo-name']
			# build the path relative to the repo-root
			self.path = editor.get_path()[len(config['repo-root'])+1:]
			
	def _load_config(self, path=None):
		"""Dind the config file for the repo recursively.
		   Don't look beyond the docs directory.
		"""
		config = None
		if not path: 
			path = os.path.dirname(editor.get_path())	
		config_path = os.path.join(path, self.filename)
		if os.path.exists(config_path):
			with open(config_path) as f:
				config = json.loads(f.read())
				config['repo-root'] = path
		elif path != Paths.docs:
			new_path = os.path.abspath(os.path.join(path, '..'))
			config = self._load_config(new_path)
		return config

