from scripts.helpful_scripts import get_account,get_chainlink_params,fund_link
from brownie import Lottery,network,config
import time

def deploy_lottery():
    account = get_account()
    chainlink_params = get_chainlink_params()
    lottery = Lottery.deploy(
        chainlink_params["eth_usd_price_feed"],
        chainlink_params["vrf_coordinator"],
        chainlink_params["link"],
        chainlink_params["key_hash"],
        chainlink_params["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"]
    )
    print("Lottery deployed!")

def start_lottery():
    lottery = Lottery[-1]
    tx = lottery.startLottery({"from": get_account()})
    tx.wait(1)
    print("Lottery started!")

def enter_lottery():
    lottery = Lottery[-1]
    entrance_fee = lottery.getEntranceFee()
    tx = lottery.enter({"from": get_account(), "value": entrance_fee})
    tx.wait(1)
    print("You entered the lottery!")

def close_lottery():
    lottery = Lottery[-1]
    fund_link(lottery)
    tx = lottery.closeLottery({"from": get_account()})
    tx.wait(1)
    time.sleep(60*5)
    print(f"{lottery.recentWinner()} is the winner!")
    print("Lottery closed.")

def main():
    deploy_lottery()
    # start_lottery()
    # enter_lottery()
    # close_lottery()