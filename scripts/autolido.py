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


def comptroller():
    # Sanity check
    comptroller1 = interface.ComptrollerInterface(collateralCToken().comptroller())
    comptroller2 = interface.ComptrollerInterface(borrowCToken().comptroller())
    if comptroller1 != comptroller2:
        raise Exception("Comptrollers do not match")
    else:
        return comptroller1


def collateralCToken():
    return interface.CErc20Interface(
        config["networks"][network.show_active()]["collateralCToken"]
    )


def enter_markets(autolido, markets):
    autolido.enterMarkets(markets, {"from": accounts[0]})


def exit_market(autolido, market):
    autolido.exitMarket(market, {"from": accounts[0]})


def borrowCToken():
    return interface.CErc20Interface(
        config["networks"][network.show_active()]["borrowCToken"]
    )


def underlyingCollateral():
    return Contract.from_abi(
        "AnyswapV5ERC20", collateralCToken().underlying(), AnyswapV5ERC20.abi
    )


def underlyingBorrow():
    return interface.EIP20Interface(borrowCToken().underlying())


def deploy_autolido():
    autolido = Autolido.deploy(
        collateralCToken(),
        borrowCToken(),
        {"from": accounts[0]},
    )
    return autolido


def mint_underlying(amount):
    tx = underlyingCollateral().mint(
        accounts[0],
        amount,
        {"from": underlyingCollateral().minters(0)},
    )
    tx.wait(1)


def burn_underlying(amount):
    tx = underlyingCollateral().burn(
        accounts[0],
        amount,
        {"from": underlyingCollateral().minters(0)},
    )
    tx.wait(1)


def deposit(autolido, amount):
    tx = underlyingCollateral().approveAndCall(
        autolido, amount, "", {"from": accounts[0]}
    )
    tx.wait(1)


def withdraw(autolido, cTokenAmount):
    tx = autolido.withdraw(cTokenAmount, {"from": accounts[0]})
    tx.wait(1)
