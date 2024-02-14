# Berachain software
Created by vvsmmg. My telegram channel - https://t.me/vvsmmg0

[![Telegram channel](https://img.shields.io/endpoint?url=https://runkit.io/damiankrawczyk/telegram-badge/branches/master?url=https://t.me/vvsmmg0)](https://t.me/vvsmmg0)

### Functionality
1. Bera claiming from faucet
2. Swaps
3. Liquidity adding
4. Honey mint, reedem
5. Deposit to bend
6. Borrow from bend
7. Mint honey jar
8. Contract creating (in progress)

### Menu 
1. Claim Bera for all wallets
2. Start base route for all wallets
3. Choose activity for wallets
4. Random activity on the wallets (not implented yet // to do)

### Installation  
+ Install Python v3.10
+ Download this repository
+ Go to project folder in terminal 
+ Run ```pip install requirements.txt```
+ Set up config.py, wallets.txt and proxy.txt
+ Run ```python main.py``` (or ```python3 main.py```)

### Config.py
Put your [2captcha](https://2captcha.com/?from=15327187) api key in thi s line
```twocaptcha_apikey = ""```
### Wallets.txt
Put your private keys in this file. 
Each new line should contain new private key.
### Proxy.txt
Proxy is needed to claim and do swaps. 
Proxy format: https://ip:port@log:pass

