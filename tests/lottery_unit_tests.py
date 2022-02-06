from scripts.deploy_lottery import deploy_lottery,start_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS,get_account,fund_link
from brownie import Lottery, VRFCoordinatorMock, network, exceptions
import pytest

def test_can_start_lottery():
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    # act
    start_lottery()
    # assert
    assert lottery.lotteryState() == 0

def test_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip() 
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    # act
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = 50 / 2000 * 10 ** 18
    # assert
    assert entrance_fee == expected_entrance_fee

def test_can_enter_lottery():
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    start_lottery()
    account = get_account()
    # act/assert
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # assert
    assert lottery.players(0) == account

def test_cant_enter_lottery_with_different_fee():
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    start_lottery()
    # act/assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee() - 10000})

def test_can_close_lottery():
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    start_lottery()
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    # act
    fund_link(lottery)
    lottery.closeLottery({"from": get_account()})
    # assert
    assert lottery.lotteryState() == 2

def test_can_select_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip() 
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    start_lottery()
    account = get_account()
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(2), "value": lottery.getEntranceFee()})
    account_starting_balance = get_account(1).balance()
    lottery_balance = lottery.balance()
    fund_link(lottery)
    tx = lottery.closeLottery({"from": account})
    # act
    request_id = tx.events["requestedRandomness"]["requestId"]
    randomness = 124
    VRFCoordinatorMock[-1].callBackWithRandomness(request_id,randomness,lottery.address, {"from": account})
    # assert
    assert lottery.recentWinner() == get_account(1) # 124 % 3 = 1
    assert get_account(1).balance() == account_starting_balance + lottery_balance
    assert lottery_balance != 0