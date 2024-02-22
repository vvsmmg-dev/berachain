import random
import sys

import requests
from eth_account import Account
from loguru import logger
from faker import Faker
import time

from services.berachain import BeraChain
from services.twocaptcha import TwoCaptcha
from services.files import read_file_lines

from config.contracts_addresses import (
    usdc_address,
    wbear_address,
    weth_address,
    bex_approve_liquidity_address,
    usdc_pool_liquidity_address,
    weth_pool_liquidity_address,
)

logger.remove()
logger.add(
    sys.stderr,
    format="<white>{time:HH:mm:ss}</white>"
    " | <level>{level: <8}</level>"
    " | <cyan>{line}</cyan>"
    " - <white>{message}</white>",
)

bera = BeraChain()
captcha_solver = TwoCaptcha()
faker = Faker()
session = requests.Session()

wallets = read_file_lines("data/wallets.txt")
proxies = read_file_lines("data/proxy.txt")


def claim_bera(wallets, proxies):
    for wallet_key, proxy in zip(wallets, proxies):
        account = Account.from_key(wallet_key.strip())
        logger.info(f"Claiming BERA for {account.address} using proxy {proxy}...")
        try:
            response = bera.claim_bera_from_faucet(
                account.address, captcha_solver, faker, proxy
            )
            if response.ok:
                logger.success(f"Successfully claimed BERA for {account.address}.")
            else:
                logger.error(
                    f"Failed to claim BERA for {account.address}: {response.text}"
                )
        except Exception as e:
            logger.error(
                f"Exception occurred while claiming BERA for {account.address}: {str(e)}"
            )
        time.sleep(2)


def bex_swap(wallet_key, asset_in_address, asset_out_address, amount_in):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Starting token swap for {account.address}...")
    try:
        result = bera.bex_swap(
            account.address,
            wallet_key,
            asset_in_address,
            asset_out_address,
            amount_in,
            faker,
            session,
        )
        if "ERR" not in result:
            logger.success(f"Swap success. TxID: {result}")
        else:
            logger.error(f"Swap failed for {account.address}: {result}")
    except Exception as e:
        logger.error(f"Exception during swap for {account.address}: {str(e)}")
    finally:
        time.sleep(2)


def add_liquidity_usdc(wallet_key, amount: int):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Adding liquidity in USDC for {account.address}...")
    try:
        result = bera.bex_add_liquidity(
            account.address,
            wallet_key,
            amount,
            usdc_pool_liquidity_address,
            usdc_address,
        )
        if "ERR" not in result:
            logger.success(f"Liquidity addition success. TxID: {result}")
        else:
            logger.error(f"Failed to add liquidity for {account.address}: {result}")
    except Exception as e:
        logger.error(f"Exception adding USDC liquidity for {account.address}: {str(e)}")
    finally:
        time.sleep(2)


def add_liquidity_weth(wallet_key, amount: int):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Adding liquidity in WETH for {account.address}...")
    try:
        result = bera.bex_add_liquidity(
            account.address,
            wallet_key,
            amount,
            weth_pool_liquidity_address,
            weth_address,
        )
        if "ERR" not in result:
            logger.success(f"Liquidity addition success. TxID: {result}")
        else:
            logger.error(f"Failed to add liquidity for {account.address}: {result}")
    except Exception as e:
        logger.error(f"Exception adding WETH liquidity for {account.address}: {str(e)}")
    finally:
        time.sleep(2)


def mint_honey(wallet_key, amount_usdc):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Minting Honey for {account.address}...")
    try:
        result = bera.honey_mint(account.address, wallet_key, amount_usdc)
        if "ERR" not in result:
            logger.success(f"Honey minting success. TxID: {result}")
        else:
            logger.error(f"Failed to mint Honey for {account.address}: {result}")
    except Exception as e:
        logger.error(f"Exception during Honey minting for {account.address}: {str(e)}")
    finally:
        time.sleep(2)


def redeem_honey(wallet_key, amount_honey):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Redeeming Honey for USDC for {account.address}...")
    try:
        result = bera.honey_redeem(account.address, wallet_key, amount_honey)
        if "ERR" not in result:
            logger.success(f"Honey redemption success. TxID: {result}")
        else:
            logger.error(f"Failed to redeem Honey for {account.address}: {result}")
    except Exception as e:
        logger.error(
            f"Exception during Honey redemption for {account.address}: {str(e)}"
        )
    finally:
        time.sleep(2)


def deposit_bend(wallet_key, token_address, amount):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Depositing to Bend for {account.address}...")
    try:
        result = bera.bend_deposit(account.address, wallet_key, token_address, amount)
        if "ERR" not in result:
            logger.success(f"Bend deposit success. TxID: {result}")
        else:
            logger.error(f"Failed to deposit in Bend for {account.address}: {result}")
    except Exception as e:
        logger.error(f"Exception during Bend deposit for {account.address}: {str(e)}")
    finally:
        time.sleep(2)


def borrow_bend(wallet_key, asset_token_address, amount):
    account = Account.from_key(wallet_key.strip())
    logger.info(f"Borrowing from Bend for {account.address}...")
    try:
        result = bera.bend_borrow(
            account.address, wallet_key, amount, asset_token_address
        )
        if "ERR" not in result:
            logger.success(f"Bend borrow success. TxID: {result}")
        else:
            logger.error(f"Failed to borrow from Bend for {account.address}: {result}")
    except Exception as e:
        logger.error(f"Exception during Bend borrowing for {account.address}: {str(e)}")
    finally:
        time.sleep(2)


def honey_jar_mint(wallet_key):
    account = Account.from_key(wallet_key.strip())
    address = account.address.strip()
    logger.info(f"Minting Honey Jar for {address}...")
    try:
        result = bera.honey_jar_mint(address, wallet_key)
        if "ERR" not in result:
            logger.success(f"Honey Jar minting success. TxID: {result}")
        else:
            logger.error(f"Failed to mint Honey Jar for {address}: {result}")
    except Exception as e:
        logger.error(f"Exception during Honey Jar minting for {address}: {str(e)}")
    finally:
        time.sleep(2)

def deploy_contract(wallet_key):
    account = Account.from_key(wallet_key.strip())
    address = account.address.strip()
    logger.info(f"Deploying contract for {address}...")
    try:
        result = bera.deploy_contract(address, wallet_key)
        if "ERR" not in result:
            logger.success(f"Deploy success. TxID: {result}")
        else:
            logger.error(f"Failed to deploy contract for {address}: {result}")
    except Exception as e:
        logger.error(f"Exception during contract deploying for {address}: {str(e)}")
    finally:
        time.sleep(2)

def bera_name(wallet_key):
    account = Account.from_key(wallet_key.strip())
    address = account.address.strip()
    logger.info(f"Creating bera name for {address}...")
    try:
        result = bera.create_bera_name(address, wallet_key)
        if "ERR" not in result:
            logger.success(f"Create success. TxID: {result}")
        else:
            logger.error(f"Failed to create bera name for {address}: {result}")
    except Exception as e:
        logger.error(f"Exception during bera name for {address}: {str(e)}")
    finally:
        time.sleep(2)


def main_menu():
    print("BeraChain Software || Created by t.me/vvsmmg0")
    print("1. Claim Bera for all wallets")
    print("2. Start base route for all wallets")
    print("3. Choose activity for wallets")
    print("4. Random activity on the wallets")
    print("5. Exit")


def choose_activity_menu():
    print("Choose activity for wallets:")
    print("1. Bex Swap")
    print("2. Add Liquidity")
    print("3. Mint Honey")
    print("4. Redeem Honey")
    print("5. Deposit to Bend")
    print("6. Borrow from Bend")
    print("7. Mint Honey Jar")
    print("8. Deploy contract")
    print("9. Bera name create")
    print("10. Back to main menu")


def perform_random_activity():
    for wallet_key in wallets:
        account = Account.from_key(wallet_key.strip())
        activities = [
            lambda: bex_swap(wallet_key, wbear_address, usdc_address,
                             int(random.randrange(1, 3, 1) / 10 * bera.w3.eth.get_balance(account.address))),
            lambda: bex_swap(wallet_key, wbear_address, weth_address,
                             int(random.randrange(1, 3, 1) / 10 * bera.usdc_contract.functions.balanceOf(
                                 account.address).call())),

            lambda: add_liquidity_usdc(wallet_key, int(random.randrange(1, 3,
                                                                        1) / 10 * bera.usdc_contract.functions.balanceOf(
                account.address).call())),
            lambda: add_liquidity_weth(wallet_key, int(random.randrange(1, 3,
                                                                        1) / 10 * bera.weth_contract.functions.balanceOf(
                account.address).call())),
            lambda: mint_honey(wallet_key,
                               int(random.randrange(1, 3, 1) / 10 * bera.usdc_contract.functions.balanceOf(
                                   account.address).call())),
            lambda: redeem_honey(wallet_key,
                                 int(random.randrange(1, 3, 1) / 10 * bera.honey_contract.functions.balanceOf(
                                     account.address).call())),
            lambda: deposit_bend(wallet_key, usdc_address,
                                 int(random.randrange(1, 3, 1) / 10 * bera.usdc_contract.functions.balanceOf(
                                     account.address).call())),
            lambda: borrow_bend(wallet_key, weth_address, 0.01 * 10 ** 18),
            lambda: honey_jar_mint(wallet_key),
            lambda: deploy_contract(wallet_key),
            lambda: bera_name(wallet_key)
        ]

        random.shuffle(activities)

        for activity in activities:
            activity()
            time.sleep(random.randint(5, 30))


def main():
    while True:
        main_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            claim_bera(wallets, proxies)
        elif choice == "2":
            for wallet_key in wallets:
                account = Account.from_key(wallet_key.strip())
                bera_balance = bera.w3.eth.get_balance(account.address)
                amount_in_bera_to_usdc = int(
                    random.randrange(1, 3, 1) / 10 * bera_balance
                )
                amount_in_bera_to_weth = int(
                    random.randrange(1, 3, 1) / 10 * bera_balance
                )

                bex_swap(
                    wallet_key, wbear_address, usdc_address, amount_in_bera_to_usdc
                )
                time.sleep(5)
                bex_swap(
                    wallet_key, wbear_address, weth_address, amount_in_bera_to_weth
                )

                usdc_balance = int(
                    random.randrange(1, 3, 1)
                    / 10
                    * bera.usdc_contract.functions.balanceOf(account.address).call()
                )
                weth_balance = int(
                    random.randrange(1, 3, 1)
                    / 10
                    * bera.weth_contract.functions.balanceOf(account.address).call()
                )

                add_liquidity_usdc(wallet_key, usdc_balance)
                time.sleep(5)
                add_liquidity_weth(wallet_key, weth_balance)

                usdc_balance = int(
                    random.randrange(1, 3, 1)
                    / 10
                    * bera.usdc_contract.functions.balanceOf(account.address).call()
                )

                mint_honey(wallet_key, usdc_balance)
                time.sleep(5)

                amount_honey = int(
                    random.randrange(1, 3, 1)
                    / 10
                    * bera.honey_contract.functions.balanceOf(account.address).call()
                )
                redeem_honey(wallet_key, amount_honey)

                time.sleep(5)
                deposit_amount_usdc = int(
                    random.randrange(1, 3, 1)
                    / 10
                    * bera.usdc_contract.functions.balanceOf(account.address).call()
                )
                deposit_bend(wallet_key, usdc_address, deposit_amount_usdc)

                time.sleep(5)
                borrow_amount_weth = 0.01 * 10 ** 18
                borrow_bend(wallet_key, weth_address, borrow_amount_weth)

                time.sleep(5)
                honey_jar_mint(wallet_key)

                time.sleep(5)
                deploy_contract(wallet_key)

                time.sleep(5)
                bera_name(wallet_key)

        elif choice == "3":
            while True:
                choose_activity_menu()
                activity_choice = input("Enter activity choice for wallets: ")
                if activity_choice == "1":
                    for wallet_key in wallets:
                        account = Account.from_key(wallet_key.strip())
                        bera_balance = bera.w3.eth.get_balance(account.address)
                        amount_in_bera_to_usdc = int(
                            random.randrange(1, 5, 1) / 10 * bera_balance
                        )
                        amount_in_bera_to_weth = int(
                            random.randrange(1, 5, 1) / 10 * bera_balance
                        )
                        bex_swap(
                            wallet_key,
                            wbear_address,
                            usdc_address,
                            amount_in_bera_to_usdc,
                        )
                        time.sleep(3)
                        bex_swap(
                            wallet_key,
                            wbear_address,
                            weth_address,
                            amount_in_bera_to_weth,
                        )

                elif activity_choice == "2":
                    for wallet_key in wallets:
                        account = Account.from_key(wallet_key.strip())
                        usdc_balance = int(
                            random.randrange(1, 5, 1)
                            / 10
                            * bera.usdc_contract.functions.balanceOf(
                                account.address
                            ).call()
                        )
                        add_liquidity_usdc(wallet_key, usdc_balance)

                        time.sleep(3)
                        weth_balance = int(
                            random.randrange(1, 5, 1)
                            / 10
                            * bera.weth_contract.functions.balanceOf(
                                account.address
                            ).call()
                        )
                        add_liquidity_weth(wallet_key, weth_balance)

                elif activity_choice == "3":
                    for wallet_key in wallets:
                        account = Account.from_key(wallet_key.strip())
                        usdc_balance = int(
                            random.randrange(1, 5, 1)
                            / 10
                            * bera.usdc_contract.functions.balanceOf(
                                account.address
                            ).call()
                        )
                        mint_honey(wallet_key, usdc_balance)

                elif activity_choice == "4":
                    for wallet_key in wallets:
                        account = Account.from_key(wallet_key.strip())
                        amount_honey = int(
                            random.randrange(1, 5, 1)
                            / 10
                            * bera.honey_contract.functions.balanceOf(
                                account.address
                            ).call()
                        )
                        redeem_honey(wallet_key, amount_honey)

                elif activity_choice == "5":
                    for wallet_key in wallets:
                        account = Account.from_key(wallet_key.strip())
                        deposit_amount_usdc = int(
                            random.randrange(1, 5, 1)
                            / 10
                            * bera.usdc_contract.functions.balanceOf(
                                account.address
                            ).call()
                        )
                        deposit_bend(wallet_key, usdc_address, deposit_amount_usdc)

                elif activity_choice == "6":
                    for wallet_key in wallets:
                        account = Account.from_key(wallet_key.strip())
                        borrow_amount_weth = 0.01 * 10**18
                        borrow_bend(wallet_key, weth_address, borrow_amount_weth)

                elif activity_choice == "7":
                    for wallet_key in wallets:
                        honey_jar_mint(wallet_key)

                elif activity_choice == "8":
                    for wallet_key in wallets:
                        deploy_contract(wallet_key)

                elif activity_choice == "9":
                    for wallet_key in wallets:
                        bera_name(wallet_key)

                elif activity_choice == "10":
                    break

        elif choice == "4":
            perform_random_activity()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please enter a valid option.")


if __name__ == "__main__":
    main()
