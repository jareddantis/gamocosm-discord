import json
import requests


response_defaults = {
    'server': False,
    'status': 'none',
    'domain': '-',
    'ip': '-',
    'minecraft': False,
}


def _parse(response):
    """Parses JSON response from endpoint"""
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


class Server:
    """API Wrapper Object that connects to one server"""

    def __init__(self, server_id, api_key):
        self.server_id = server_id
        self.api_key = api_key
        self.api_url = f"https://gamocosm.com/servers/{server_id}/api/{api_key}/"
        self.headers = {}
        self.last_state = False

    def _get(self, endpoint):
        """Sends a GET request to the specified endpoint"""
        response = requests.get(self.api_url + endpoint, headers=self.headers)
        return _parse(response)

    def _post(self, endpoint, data):
        """Sends a POST request to the specified endpoint"""
        response = requests.post(self.api_url + endpoint, data, headers=self.headers)
        return _parse(response)

    def _status(self):
        """Sends GET request to get raw status of server"""
        return self._get("status")

    def _status_safe(self, attribute):
        """Retrieves the specified attribute from the Gamocosm API,
        and returns a specified default value in case of an error."""
        status = self._status()
        return status[attribute] if attribute in status else response_defaults[attribute]

    def status(self):
        """Gets server status, with default values in case of errors."""
        raw_status = self._status()
        for key in response_defaults.keys():
            if key not in raw_status:
                raw_status[key] = response_defaults[key]
        return raw_status

    def start(self):
        """Sends POST request to start the DO server"""
        return self._post("start", "")['error']

    def stop(self):
        """Sends POST request to stop the DO server"""
        return self._post("stop", "")['error']

    def reboot(self):
        """Sends POST request to reboot the DO server"""
        return self._post("reboot", "")['error']

    def pause(self):
        """Sends POST request to stop the Minecraft server"""
        return self._post("pause", "")['error']

    def resume(self):
        """Sends POST request to start the Minecraft server"""
        return self._post("resume", "")['error']

    def backup(self):
        """Sends POST request to remotely backup the world of the server"""
        return self._post("backup", "")['error']

    def online(self):
        """Is the DO server online?"""
        status = self._status_safe('server')
        return 'online' if status else 'offline'

    def pending(self):
        """Are there any pending operations?"""
        return self._status_safe('status')

    def minecraft(self):
        """Is the Minecraft server running?"""
        status = self._status_safe('minecraft')
        return 'online' if status else 'offline'

    def domain(self):
        """Whats the hostname of the server"""
        return self._status_safe('domain')

    def ip(self):
        """Has an ip been assigned?"""
        return self._status_safe('ip')

    def download(self):
        """Grabs a download link for the world"""
        return self._status_safe('download')
