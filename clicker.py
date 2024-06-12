import requests
import time
import random
from database import add_token, get_all_tokens, delete_token


class HamsterKombatClicker:
    def __init__(self,):
        self.url = "https://api.hamsterkombat.io/clicker/tap"
        self.headers_template = {
            "Content-Type": "application/json",
        }
        self.count_interval = (1, 10)
        self.bearer_tokens = self.get_bearer_tokens()
        self.sleep_interval = (300, 600)  # 5-10 minutes
        self.user_agents = self.get_user_agents()

    def get_user_agents(self):
        """Get a list of user agents."""
        with open("user_agents.txt", "r") as f:
            return f.read().splitlines()

    def get_bearer_tokens(self):
        """Get a list of all bearer tokens."""
        return get_all_tokens()

    def add_token(self, token):
        """Add a new bearer token to the list."""
        status = add_token(token)
        if status:
            return True
        else:
            return False

    def remove_token(self, token):
        """Remove a bearer token from the list."""
        if delete_token(token):
            return True
        else:
            return False

    def send_request(self, token, body):
        """Send a POST request with the provided bearer token and body."""
        headers = self.headers_template.copy()
        headers["Authorization"] = f"Bearer {token}"
        headers["User-Agent"] = random.choice(self.user_agents)
        response = requests.post(self.url, json=body, headers=headers)
        return response

    def execute(self):
        """Continuously send requests at intervals."""
        while True:
            timestamp = int(time.time())
            count = random.randint(*self.count_interval)
            print(f"\nTapping count: {count}\n")

            body = {
                "count": count,
                "availableTaps": 5000,
                "timestamp": timestamp
            }
            for token in self.get_bearer_tokens():
                try:
                    response = self.send_request(token, body)
                    if response.status_code == 200:
                        print("Response:", response.json())
                        print("\nRequest successful!\n")
                    elif response.status_code in {401, 403}:
                        print("Response:", response.text)
                        print(f"\nInvalid token detected. Removing token: {token}\n")
                        self.remove_token(token)
                        print(f"Remaining tokens: {self.get_bearer_tokens()}")
                    else:
                        print("Response:", response.text)
                        print("\nRequest failed with status code:", response.status_code)
                        print("Waiting for 5 minutes before retrying...\n")
                        time.sleep(300)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
                    print("Waiting for 10 minutes before retrying...\n")
                    time.sleep(900) # 15 minutes
                except Exception as e:
                    print(f"An error occurred: {e}")
                    print("Waiting for 10 minutes before retrying...\n")
                    time.sleep(900) # 15 minutes
                time.sleep(2) # 2 seconds              
            sleep_duration = random.randint(*self.sleep_interval)
            print(f"\nSleeping for {sleep_duration} seconds\n")
            time.sleep(sleep_duration)