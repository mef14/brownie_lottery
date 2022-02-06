from brownie import Lottery,network
from scripts.deploy_lottery import deploy_lottery,start_lottery,enter_lottery,close_lottery
from scripts.helpful_scripts import get_account,LOCAL_BLOCKCHAIN_ENVIRONMENTS
import pytest


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    deploy_lottery()
    lottery = Lottery[-1]
    account = get_account()
    # act
    start_lottery()
    enter_lottery()
    enter_lottery()
    close_lottery()
    # assert
    assert lottery.balance() == 0
    assert lottery.recentWinner() == account

