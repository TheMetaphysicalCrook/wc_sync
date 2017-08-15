import webbrowser

try:
	from urllib import urlencode
except:
	from urllib.parse import urlencode


class WorkingCopyApi():
	
	def __init__(self, key):
		self.key = key

	def _send_request(self, action, payload, x_callback_enabled=False):
		x_callback = 'x-callback-url/' if x_callback_enabled else ''
		
		payload['key'] = self.key
		payload = urlencode(payload).replace('+', '%20')
		fmt = 'working-copy://{x_callback}{action}/?{payload}'
		url = fmt.format(x_callback=x_callback, action=action, payload=payload)
		webbrowser.open(url)
		
	def get_repo_list(self, x_success):
		action = 'repos'
		payload = {
			'x-success': x_success
		}
		self._send_request(action, payload, True)
		
	def get_repo(self, repo, x_success):
		action = 'zip'
		payload = {
			'x-success': x_success,
			'repo': repo
		}
		self._send_request(action, payload, True)
		
	def push_file(self, repo, path, contents, x_success):
		action = 'write'
		payload = {
			'repo': repo,
			'path': path,
			'text': contents,
			'x-success': x_success
		}
		self._send_request(action, payload, True)
	
	def get_file(self, repo, path, x_success):
		action = 'read'
		payload = {
			'repo': repo,
			'path': path,
			'base64': '1',
			'x-success': x_success
		}
		self._send_request(action, payload, True)
		
	def open(self, repo):
		action = 'open'
		payload = {
			'repo': repo
		}
		self._send_request(action, payload, False)
		
