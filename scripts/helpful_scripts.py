from itertools import chain
from brownie import network,accounts,config,MockV3Aggregator,LinkToken,VRFCoordinatorMock,Contract
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork","mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development","ganache-desktop"]

def get_account(index=0):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[index]
    else:
        return accounts.add(config["wallets"]["from_key"])

# get chainlink paramters to generate price feeds and random numbers
# deploy mocks if on development networks
def get_chainlink_params():

    chainlink_params = {}

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        chainlink_params["eth_usd_price_feed"] = config["networks"][network.show_active()]["eth_usd_price_feed"]
        chainlink_params["vrf_coordinator"] = config["networks"][network.show_active()]["vrf_coordinator"]
        chainlink_params["link"] = config["networks"][network.show_active()]["link"]
        chainlink_params["key_hash"] = config["networks"][network.show_active()]["key_hash"]
        chainlink_params["fee"] = config["networks"][network.show_active()]["fee"]
    else:
        if len(MockV3Aggregator) > 0 and len(LinkToken) > 0 and len(VRFCoordinatorMock) > 0:
            mock_v3_aggregator = MockV3Aggregator[-1]
            mock_link_token = LinkToken[-1]
            mock_vrf_coordinator = VRFCoordinatorMock[-1]
        else:
            mock_v3_aggregator = MockV3Aggregator.deploy(8,2000 * 10 ** 8,{"from": get_account()})
            mock_link_token = LinkToken.deploy({"from": get_account()})
            mock_vrf_coordinator = VRFCoordinatorMock.deploy(mock_link_token.address,{"from": get_account()})

        chainlink_params["eth_usd_price_feed"] = mock_v3_aggregator.address
        chainlink_params["vrf_coordinator"] = mock_vrf_coordinator.address
        chainlink_params["link"] = mock_link_token.address
        chainlink_params["key_hash"] = config["networks"][network.show_active()]["key_hash"]
        chainlink_params["fee"] = config["networks"][network.show_active()]["fee"]
        
    return chainlink_params

# get LINK token
def fund_link(to_account,from_account=None,amount=100000000000000000):
    from_account = from_account if from_account else get_account()
    link_token = Contract.from_abi(LinkToken._name,get_chainlink_params()["link"],LinkToken.abi)
    tx = link_token.transfer(to_account,amount, {"from": from_account})
    tx.wait(1)