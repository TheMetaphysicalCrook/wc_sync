import webbrowser
import functools

try:
	from urllib import urlencode
except:
	from urllib.parse import urlencode


class WorkingCopyApi():
	
	def __init__(self, key):
		self.key = key

	def __getattr__(self, attr):
		return functools.partial(self._send_request, action=attr)
		
	def __getattribute__(self, attr):
		result = object.__getattribute__(self, attr)
		if result:
			return result
		raise AttributeError()

	def _send_request(self, action, **kwargs):
		payload = kwargs
		if 'x_success' in payload:
			payload['x-success'] = payload.pop('x_success')
		
		x_callback = 'x-callback-url/' if 'x-success' in payload else ''
		
		payload['key'] = self.key
		if action == 'read':
			payload['base64'] = 1
		
		payload = urlencode(payload).replace('+', '%20')
		
		fmt = 'working-copy://{x_callback}{action}/?{payload}'
		url = fmt.format(x_callback=x_callback, action=action, payload=payload)
		webbrowser.open(url)
		
		
