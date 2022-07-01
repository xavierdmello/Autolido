from brownie import (
    accounts,
    Autolido,
    chain,
    config,
    network,
    AnyswapV5ERC20,
    Contract,
    interface,
)
from scripts.helpful import load_accounts


def cToken():
    return interface.CErc20Interface(
        config["networks"][network.show_active()]["cToken"]
    )


def underlying():
    return Contract.from_abi(
        "AnyswapV5ERC20", cToken().underlying(), AnyswapV5ERC20.abi
    )


def deploy_autolido():
    autolido = Autolido.deploy(cToken(), {"from": accounts[0]})
    return autolido


def mint_underlying(amount):
    underlying().mint(
        accounts[0],
        amount,
        {"from": underlying().minters(0)},
    )


def burn_underlying(amount):
    underlying().burn(
        accounts[0],
        amount,
        {"from": underlying().minters(0)},
    )


def deposit(autolido, amount):
    underlying().approveAndCall(autolido, amount, "", {"from": accounts[0]})


def withdraw(autolido, cTokenAmount):
    autolido.withdraw(cTokenAmount, {"from": accounts[0]})
