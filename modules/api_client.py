import requests
import yaml

class AviMockClient:
    # Accept an optional logger function
    def __init__(self, config_path, logger=print):
        self.logger = logger  # Store the logger
        
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.base_url = self.config['base_url']
        self.token = None
        self.headers = {}

    def register(self):
        url = f"{self.base_url}/register"
        payload = {
            "username": self.config['auth']['username'],
            "password": self.config['auth']['password']
        }
        # Log using the passed logger
        # self.logger(f"[dim]DEBUG: Registering {payload['username']}...[/dim]") 
        response = requests.post(url, json=payload)
        return response.status_code

    def login(self):
        # 1. Clean URL Construction
        # Removes potential double slashes that cause 404 errors
        endpoint = self.config['endpoints']['login'].lstrip('/')
        url = f"{self.base_url.rstrip('/')}/{endpoint}"
        
        # 2. Thread-Safe Logging
        # Uses self.logger instead of print() to ensure output is tagged correctly
        self.logger(f"DEBUG: Attempting login at: {url}")
        
        auth = (self.config['auth']['username'], self.config['auth']['password'])
        try:
            # 3. Request & Validation
            response = requests.post(url, auth=auth)
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.logger(f"DEBUG: Login Successful. Token acquired.")
                return True
            else:
                self.logger(f"Login Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger(f"Connection Failed: {e}")
            return False
        
    def get_resource(self, endpoint):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def update_vs_state(self, uuid, enabled_status):
        url = f"{self.base_url}/api/virtualservice/{uuid}"
        payload = {"enabled": enabled_status}
        response = requests.put(url, json=payload, headers=self.headers)
        
        # Safety check: ensure response is valid JSON before parsing
        try:
            return response.json()
        except:
            return {} # Return empty dict if no content