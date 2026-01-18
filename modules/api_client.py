import requests
import yaml

class AviMockClient:
    def __init__(self, config_path):
        # Dynamically parse YAML configurations 
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.base_url = self.config['base_url']
        self.token = None
        self.headers = {}

    def register(self):
        """Step 1: Register a new user [cite: 54, 133]"""
        url = f"{self.base_url}/register"
        payload = {
            "username": self.config['auth']['username'],
            "password": self.config['auth']['password']
        }
        response = requests.post(url, json=payload)
        return response.status_code

    def login(self):
        url = f"{self.base_url}/login1"
        # The doc requires Basic Auth for the login step 
        auth = (self.config['auth']['username'], self.config['auth']['password'])
        try:
            response = requests.post(url, auth=auth)
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.headers = {"Authorization": f"Bearer {self.token}"} # [cite: 72, 151]
                return True
            else:
                print(f"Login Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Connection Failed: {e}")
            return False

    def get_resource(self, endpoint):
        """Generic GET method for fetching tenants, VSs, or SEs [cite: 34, 118]"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def update_vs_state(self, uuid, enabled_status):
        """Step 3: Convert VS endpoint to a PUT request to update state [cite: 43, 123]"""
        url = f"{self.base_url}/api/virtualservice/{uuid}"
        payload = {"enabled": enabled_status}
        response = requests.put(url, json=payload, headers=self.headers)
        return response.json()