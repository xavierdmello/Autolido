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
from scripts.autolido import (
    burn_underlying,
    cToken,
    deploy_autolido,
    deposit,
    mint_underlying,
    underlying,
    withdraw,
)
from scripts.helpful import load_accounts


def test_deposit():
    # Arrange
    load_accounts()
    AMOUNT = 1 * 10 ** (underlying().decimals() - 1)  # 0.1 of underlying token
    if network.show_active() == "moonriver-fork":
        mint_underlying(AMOUNT)
    # Make sure user has enough of underlying assset in account to mint
    assert underlying().balanceOf(accounts[0]) >= AMOUNT
    autolido = deploy_autolido()

    # Act
    # Deposit underlying asset
    deposit(autolido, AMOUNT)

    # Assert
    if network.show_active() == "moonriver-fork":
        # mine block to make sure balanceOfUnderlying() calls on the correct block
        chain.mine()
    assert cToken().balanceOfUnderlying.call(autolido, {"from": accounts[0]}) == AMOUNT
    assert underlying().balanceOf(accounts[0]) == 0
    assert autolido.cTokenBalances(accounts[0]) == cToken().balanceOf(autolido)

    # Cleanup (withdraw & burn underlying so balances are correct if underlying asset is being used again in same VM instance)
    withdraw(autolido, autolido.cTokenBalances(accounts[0]))
    if network.show_active() == "moonriver-fork":
        burn_underlying(AMOUNT)


def test_withdraw():
    # Arrange
    load_accounts()
    AMOUNT = 1 * 10 ** (underlying().decimals() - 1)  # 0.1 of underlying token
    if network.show_active() == "moonriver-fork":
        mint_underlying(AMOUNT)
    # Make sure user has enough of underlying assset in account to mint
    assert underlying().balanceOf(accounts[0]) >= AMOUNT
    autolido = deploy_autolido()
    deposit(autolido, AMOUNT)

    # Act
    # Withdraw underlying asset
    withdraw(autolido, autolido.cTokenBalances(accounts[0]))

    # Assert
    assert autolido.cTokenBalances(accounts[0]) == 0
    assert underlying().balanceOf(accounts[0]) == AMOUNT
    assert cToken().balanceOf(autolido) == 0

    # Cleanup (burn underlying so balances are correct if underlying asset is being used again in same VM instance)
    if network.show_active() == "moonriver-fork":
        burn_underlying(AMOUNT)
