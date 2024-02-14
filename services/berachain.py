import json
import random
import time

import requests
from loguru import logger
from web3 import Web3

from config.config import rpc_url
from config.abi import (
    erc_20_abi,
    honey_abi,
    bex_abi,
    bend_abi,
    bend_borrows_abi,
    ooga_booga_abi,
)
from config.contracts_addresses import (
    bex_swap_address,
    usdc_address,
    honey_address,
    honey_swap_address,
    bex_approve_liquidity_address,
    weth_address,
    bend_address,
    bend_borrows_address,
    wbear_address,
    zero_address,
    ooga_booga_address,
)


class BeraChain:
    def __init__(self):
        self.rpc_url = rpc_url
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self.bex_contract = self.w3.eth.contract(
                address=bex_swap_address, abi=bex_abi
            )
            self.honey_swap_contract = self.w3.eth.contract(
                address=honey_swap_address, abi=honey_abi
            )
            self.usdc_contract = self.w3.eth.contract(
                address=usdc_address, abi=erc_20_abi
            )
            self.weth_contract = self.w3.eth.contract(
                address=weth_address, abi=erc_20_abi
            )
            self.honey_contract = self.w3.eth.contract(
                address=honey_address, abi=erc_20_abi
            )
            self.bend_contract = self.w3.eth.contract(
                address=bend_address, abi=bend_abi
            )
            self.bend_borrows_contract = self.w3.eth.contract(
                address=bend_borrows_address, abi=bend_borrows_abi
            )
            self.ooga_booga_contract = self.w3.eth.contract(
                address=ooga_booga_address, abi=ooga_booga_abi
            )
        except:
            raise ValueError(
                "Wrong RPC. Recommended RPC: https://artio.rpc.berachain.com/"
            )

    def get_nonce(self, address):
        return self.w3.eth.get_transaction_count(address)

    def claim_bera_from_faucet(self, address, twocaptcha, fake, proxies=None):
        google_token = twocaptcha.get_2captcha_google_token()
        if not google_token:
            raise ValueError("Cannot get Google token. Check your 2captcha API key.")
        user_agent = fake.chrome()
        headers = {
            "authority": "artio-80085-ts-faucet-api-2.berachain.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": f"Bearer {google_token}",
            "cache-control": "no-cache",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://artio.faucet.berachain.com",
            "pragma": "no-cache",
            "referer": "https://artio.faucet.berachain.com/",
            "user-agent": user_agent,
        }
        params = {"address": address}
        response = requests.post(
            "https://artio-80085-faucet-api-recaptcha.berachain.com/api/claim",
            params=params,
            headers=headers,
            data=json.dumps(params),
            proxies=proxies,
        )
        return response

    def approve_token(
        self, address, private_key, spender, amount: int, approve_token_address
    ):
        approve_contract = self.w3.eth.contract(
            address=approve_token_address, abi=erc_20_abi
        )

        allowance_balance = approve_contract.functions.allowance(
            address, spender
        ).call()
        if allowance_balance < amount:
            txn = approve_contract.functions.approve(spender, amount).buildTransaction(
                {
                    "gas": 500000 + random.randint(1, 10000),
                    "gasPrice": int(self.w3.eth.gas_price * 1.15),
                    "nonce": self.get_nonce(address),
                }
            )
            signed_txn = self.w3.eth.account.signTransaction(
                txn, private_key=private_key.strip()
            )
            order_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            return order_hash.hex()
        return True

    def bex_swap(
        self,
        spender,
        private_key,
        asset_in_address,
        asset_out_address,
        amount_in,
        fake,
        session,
    ):
        if asset_in_address == wbear_address:
            balance = self.w3.eth.get_balance(spender)
            if balance == 0:
                return "ERR: Bera balance is 0. Try again."
        else:
            asset_in_token_contract = self.w3.eth.contract(
                asset_in_address, abi=erc_20_abi
            )
            balance = asset_in_token_contract.functions.balanceOf(spender).call()
            if balance == 0:
                return "ERR: Bera balance is 0. Try again."
            allowance_balance = asset_in_token_contract.functions.allowance(
                spender, bex_swap_address
            ).call()
            if allowance_balance < amount_in:
                try:
                    approve_result = self.approve_token(
                        spender,
                        private_key,
                        bex_swap_address,
                        int("0x" + "f" * 64, 16),
                        bex_swap_address,
                    )
                    logger.debug(approve_result)
                except:
                    return "ERR: Something went wrong with allowance. Try again."

        headers = {
            "authority": "artio-80085-dex-router.berachain.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "origin": "https://artio.bex.berachain.com",
            "pragma": "no-cache",
            "referer": "https://artio.bex.berachain.com/",
            "user-agent": fake.chrome(),
        }

        params = {
            "quoteAsset": asset_out_address,
            "baseAsset": asset_in_address,
            "amount": amount_in,
            "swap_type": "given_in",
        }

        response = session.get(
            "https://artio-80085-dex-router.berachain.com/dex/route",
            params=params,
            headers=headers,
        )
        time.sleep(1)
        assert response.status_code == 200
        swaps_list = response.json()["steps"]
        swaps = list()
        for index, info in enumerate(swaps_list):
            swaps.append(
                dict(
                    poolId=self.w3.toChecksumAddress(info["pool"]),
                    assetIn=self.w3.toChecksumAddress(info["assetIn"]),
                    amountIn=int(info["amountIn"]),
                    assetOut=self.w3.toChecksumAddress(info["assetOut"]),
                    amountOut=0
                    if index + 1 != len(swaps_list)
                    else int(int(info["amountOut"]) * 0.5),
                    userData=b"",
                )
            )
        if asset_in_address.lower() == wbear_address.lower():
            swaps[0]["assetIn"] = zero_address

        txn = self.bex_contract.functions.batchSwap(
            kind=0, swaps=swaps, deadline=99999999
        ).buildTransaction(
            {
                "gas": 500000 + random.randint(1, 10000),
                "value": amount_in if asset_in_address == wbear_address else 0,
                "gasPrice": int(self.w3.eth.gas_price * 1.2),
                "nonce": self.get_nonce(spender),
            }
        )
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key.strip())
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()

    def bex_add_liquidity(
        self, spender, private_key, amount_to_spend: int, pool_address, asset_in_address
    ) -> str:
        asset_in_token_contract = self.w3.eth.contract(asset_in_address, abi=erc_20_abi)
        token_balance = asset_in_token_contract.functions.balanceOf(spender).call()
        assert token_balance != 0
        assert token_balance >= amount_to_spend
        allowance_balance = asset_in_token_contract.functions.allowance(
            spender, bex_approve_liquidity_address
        ).call()
        if allowance_balance < amount_to_spend:
            approve_result = self.approve_token(
                spender,
                private_key,
                bex_approve_liquidity_address,
                int("0x" + "f" * 64, 16),
                asset_in_address,
            )
            logger.debug(approve_result)

        txn = self.bex_contract.functions.addLiquidity(
            pool_address,
            receiver=spender,
            assetsIn=[asset_in_address],
            amountsIn=[amount_to_spend],
        ).buildTransaction(
            {
                "gas": 500000 + random.randint(1, 10000),
                "gasPrice": int(self.w3.eth.gas_price * 1.15),
                "nonce": self.get_nonce(spender),
            }
        )
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key.strip())
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()

    def honey_mint(self, spender, private_key, amount_usdc: int) -> str:
        usdc_balance = self.usdc_contract.functions.balanceOf(spender).call()
        assert usdc_balance != 0
        assert usdc_balance >= amount_usdc
        allowance_balance = self.usdc_contract.functions.allowance(
            spender, honey_swap_address
        ).call()
        if allowance_balance < amount_usdc:
            approve_result = self.approve_token(
                spender,
                private_key,
                honey_swap_address,
                int("0x" + "f" * 64, 16),
                usdc_address,
            )

        txn = self.honey_swap_contract.functions.mint(
            spender,
            usdc_address,
            amount=amount_usdc,
        ).buildTransaction(
            {
                "gas": 500000 + random.randint(1, 10000),
                "gasPrice": int(self.w3.eth.gas_price * 1.15),
                "nonce": self.get_nonce(spender),
            }
        )
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key.strip())
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()

    def honey_redeem(self, address, private_key, amount_honey_in: int) -> str:
        honey_balance = self.honey_contract.functions.balanceOf(address).call()
        assert honey_balance != 0
        assert honey_balance >= amount_honey_in
        allowance_balance = self.honey_contract.functions.allowance(
            address, honey_swap_address
        ).call()
        if allowance_balance < amount_honey_in:
            try:
                approve_result = self.approve_token(
                    address,
                    private_key,
                    honey_swap_address,
                    int("0x" + "f" * 64, 16),
                    honey_address,
                )

            except:
                return "ERR: Something went wrong with allowance. Try again."
        txn = self.honey_swap_contract.functions.redeem(
            to=address, amount=amount_honey_in, collateral=usdc_address
        ).buildTransaction(
            {
                "gas": 500000 + random.randint(1, 10000),
                "gasPrice": int(self.w3.eth.gas_price * 1.15),
                "nonce": self.get_nonce(address),
            }
        )
        signed_txn = self.w3.eth.account.sign_transaction(
            txn, private_key=private_key.strip()
        )
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()

    def bend_deposit(
        self, address, private_key, amount_in_token_address, amount_in: int
    ) -> str:
        amount_in_token_contract = self.w3.eth.contract(
            address=amount_in_token_address, abi=erc_20_abi
        )
        token_balance = amount_in_token_contract.functions.balanceOf(address).call()
        assert token_balance != 0
        assert token_balance >= amount_in
        allowance_balance = amount_in_token_contract.functions.allowance(
            address, bend_address
        ).call()
        if allowance_balance < amount_in:
            try:
                approve_result = self.approve_token(
                    address,
                    private_key,
                    bend_address,
                    int("0x" + "f" * 64, 16),
                    weth_address,
                )
            except:
                return "ERR: Something went wrong with allowance. Try again."
        txn = self.bend_contract.functions.supply(
            asset=amount_in_token_address,
            amount=amount_in,
            onBehalfOf=address,
            referralCode=0,
        ).buildTransaction(
            {
                "gas": 500000 + random.randint(1, 10000),
                "gasPrice": int(self.w3.eth.gas_price * 1.15),
                "nonce": self.get_nonce(address),
            }
        )
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key.strip())
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()

    def bend_borrow(
        self, address, private_key, amount_out: int, asset_token_address
    ) -> str:
        tx_data = self.bend_contract.functions.borrow(
            asset=asset_token_address,
            amount=int(amount_out),
            interestRateMode=2,
            referralCode=0,
            onBehalfOf=address,
        ).buildTransaction(
            {
                "gas": 500000 + random.randint(1, 10000),
                "gasPrice": int(self.w3.eth.gas_price * 1.15),
                "nonce": self.get_nonce(address),
            }
        )
        signed_txn = self.w3.eth.account.sign_transaction(
            tx_data, private_key=private_key.strip()
        )
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()

    def honey_jar_mint(self, address, private_key):
        allowance_balance = self.honey_contract.functions.allowance(
            address, ooga_booga_address
        ).call()
        if allowance_balance / 1e18 < 4.2:
            try:
                approve_result = self.approve_token(
                    address,
                    private_key,
                    ooga_booga_address,
                    int("0x" + "f" * 64, 16),
                    honey_address,
                )
            except:
                return "ERR: Something went wrong with allowance. Try again."
        has_mint = self.ooga_booga_contract.functions.hasMinted(address).call()
        if has_mint:
            return True
        signed_txn = self.w3.eth.account.sign_transaction(
            dict(
                chainId=80085,
                nonce=self.get_nonce(address),
                gasPrice=int(self.w3.eth.gas_price * 1.15),
                gas=134500 + random.randint(1, 10000),
                to=self.w3.toChecksumAddress(ooga_booga_address),
                data="0xa6f2ae3a",
            ),
            private_key.strip(),
        )
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return order_hash.hex()
