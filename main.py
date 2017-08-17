import console
import dialogs
import editor
import keychain
import json
import os
import shutil
import sys
from collections import OrderedDict

from api import WorkingCopyApi
	

class WorkingCopySync():

	def __init__(self, paths, config):
		self.key = self._get_key()
		
		self.paths = paths
		self.config = config
		self.repo = self.config.repo
		self.path = self.config.path
			
		self.wcApi = WorkingCopyApi(self.key)
	
	@property
	def repo_path(self):
		return os.path.join(self.repo, self.path)		
		
	def _get_key(self):
		"""Retrieve the working copy key or prompt for a new one."""
		key = keychain.get_password('wcSync', 'xcallback')
		if not key:
			key = console.password_alert('Working Copy Key')
			keychain.set_password('wcSync', 'xcallback', key)
		return key

	def _get_repo_list(self):
		x_success = 'pythonista3://{install_path}/{wc_file}?action=run&argv=repo_list&argv='	
		x_success = x_success.format(install_path=self.paths.wc_install_path, wc_file=self.paths.wc_file)
		self.wcApi.repos(x_success=x_success)

	def copy_repo_from_wc(self, repo_list=None):
		''' copy a repo to the local filesystem
		'''
		if not repo_list:
			self._get_repo_list()
		else:
			repo_name = dialogs.list_dialog(title='Select repo', items=repo_list)
			if repo_name:
				x_success = 'pythonista3://{install_path}/{wc_file}?action=run&argv=copy_repo&argv={repo_name}&argv='
				x_success = x_success.format(install_path=self.paths.wc_install_path, repo_name=repo_name, wc_file=self.paths.wc_file)
				self.wcApi.zip(repo=repo_name, x_success=x_success)

	def _push_file_to_wc(self, path, contents):
		x_success = 'pythonista3://{repo}/{path}?'.format(repo=self.repo, path=path)
		self.wcApi.write(repo=self.repo, path=path, text=contents, x_success=x_success)

	def push_current_file_to_wc(self):
		self._push_file_to_wc(self.path, editor.get_text())

	def push_pyui_to_wc(self):
		pyui_path, pyui_contents = self._get_pyui_contents_for_file()
		if not pyui_contents:
			console.alert("No PYUI file associated. Now say you're sorry.",
				button1="I'm sorry.", hide_cancel_button=True)
		else:
			self._push_file_to_wc(pyui_path, pyui_contents)

	def _get_pyui_contents_for_file(self):
		rel_pyui_path = self.path + 'ui'
		full_pyui_path = os.path.join(self.paths.docs, self.repo, rel_pyui_path)
		try:
			with open(full_pyui_path) as f:
				return rel_pyui_path, f.read()
		except IOError:
			return None, None

	def overwrite_with_wc_copy(self):
		x_success = 'pythonista3://{install_path}/{wc_file}?action=run&argv=overwrite_file&argv={path}&argv='
		x_success = x_success.format(install_path=self.paths.wc_install_path, path=editor.get_path(), wc_file=self.paths.wc_file)
		self.wcApi.read(repo=self.repo, path=self.path, x_success=x_success)

	def open_repo_in_wc(self):
		self.wcApi.open(repo=self.repo)
		
	def present(self):
		actions = OrderedDict()
		actions['CLONE 	- Copy repo from Working Copy'] = self.copy_repo_from_wc
		if self.repo: 
			actions['FETCH 	- Overwrite file with WC version'] = self.overwrite_with_wc_copy
			actions['PUSH 		- Send file to WC'] = self.push_current_file_to_wc
			actions['PUSH UI 	- Send associated PYUI to WC'] = self.push_pyui_to_wc
			actions['OPEN 		- Open repo in WC'] = self.open_repo_in_wc
		action = dialogs.list_dialog(title='Choose action', items=[key for key in actions])
		if action:
			actions[action]()
			

def main(url_action=None, url_args=None):
	from helpers import Paths, Config
	import xcallback
	
	config = Config()
	
	wc = WorkingCopySync(Paths, config)
	xc = xcallback.Handler(Paths, Config.filename)
	
	if not url_action or url_action == editor.get_path():
		wc.present()
	elif url_action == 'copy_repo':
		xc.copy_repo(url_args[0], url_args[1])
	elif url_action == 'overwrite_file':
		xc.copy_file(url_args[0], url_args[1])
	elif url_action == 'repo_list':
		wc.copy_repo_from_wc(repo_list=[repo['name'] for repo in json.loads(url_args[0])])
	else:
		msg = "Not a valid URL scheme action. Now say you're sorry."
		console.alert(msg, button1="I'm sorry.", hide_cancel_button=True)

if __name__ == "__main__":
	url_action, url_args = None, None
	if len(sys.argv) > 1:
		url_action = sys.argv[1]
		url_args = sys.argv[2:]
	main(url_action, url_args)
