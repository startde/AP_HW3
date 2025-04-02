from locust import HttpUser, task, between
from datetime import datetime, timedelta
import time

class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_root(self):
        self.client.get("/docs") 

    @task
    def create_short_link(self):
        unique_id = str(time.time()).replace('.', '') 
        expires_at_datetime = datetime.utcnow() + timedelta(minutes=10)
        expires_at_str = expires_at_datetime.isoformat()
        data = {
            "original_url": f"https://mail.ru/{unique_id}", 
            "custom_alias": f"short_{unique_id}", 
            "expires_at": expires_at_str
        }
        self.client.post(
            "links/shorten",
            json=data,
            headers={"Content-Type": "application/json"}
        )