import time

import requests

from config.config import twocaptcha_apikey


class TwoCaptcha:
    def __init__(self):
        self.twocaptcha_apikey = twocaptcha_apikey

    def get_2captcha_google_token(self):
        if self.twocaptcha_apikey == "":
            raise ValueError("2Captcha API key is null. Check your config.py")
        params = {
            "key": self.twocaptcha_apikey,
            "method": "userrecaptcha",
            "version": "v3",
            "action": "submit",
            "min_score": 0.5,
            "googlekey": "6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH",
            "pageurl": "https://artio.faucet.berachain.com/",
            "json": 1,
        }
        response = requests.get(f"https://2captcha.com/in.php?", params=params).json()
        if response["status"] != 1:
            raise ValueError(response)
        task_id = response["request"]
        for _ in range(60):
            response = requests.get(
                f"https://2captcha.com/res.php?key={self.twocaptcha_apikey}&action=get&id={task_id}&json=1"
            ).json()
            if response["status"] == 1:
                return response["request"]
            else:
                time.sleep(3)
        return False
