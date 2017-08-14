import base64
import errno
import json
import os
import sys
import zipfile

import console
import editor

from Helpers import Paths, Config


class XCallbackHandler():
	
	def __init__(self, paths, config_filename):
		self.tmp_directory = paths.wc_install_path
		self.config_filename = config_filename
		self.paths = paths
		
	def copy_repo(self, path, b64_contents):
		tmp_zip_location = self.tmp_directory + 'repo.zip'
		dest = os.path.join(self.paths.docs, path)
		try:
			os.makedirs(dest)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise e
			console.alert('Overwriting existing directory', button1='Continue')
			shutil.rmtree(dest)
			
		zip_file_location = os.path.join(self.paths.docs, tmp_zip_location)
		with open(zip_file_location, 'wb') as out_file:
			out_file.write(base64.b64decode(b64_contents))
				
		with zipfile.ZipFile(zip_file_location) as in_file:
			in_file.extractall(dest)
			
		os.remove(zip_file_location)
		with open(os.path.join(dest, self.config_filename), 'w') as config_file:
			config_file.write(json.dumps({"repo-name": path}))
			
		console.hud_alert(path + ' Downloaded')

	def copy_file(self, path, b64_contents):
		text = base64.b64decode(b64_contents)
		full_file_path = os.path.join(self.paths.docs, path)
		try:
			os.makedirs(full_file_path)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise e
				
		with open(full_file_path, 'wb') as f:
			f.write(text)
			
		editor.open_file(path)
		_, filename = os.path.split(path)
		console.hud_alert(filename + ' Updated')
		

def main(actions, args):
	handler = XCallbackHandler(Paths, Config.filename)
	if url_action == 'copy_repo':
		wc.urlscheme_copy_repo_from_wc(url_args[0], url_args[1])
	elif url_action == 'overwrite_file':
		wc.urlscheme_overwrite_file_with_wc_copy(url_args[0], url_args[1])
				
if __name__ == '__main__':
	url_action, url_args = None, None
	if len(sys.argv) > 1:
		url_action = sys.argv[1]
		url_args = sys.argv[2:]
	main(url_action, url_args)
