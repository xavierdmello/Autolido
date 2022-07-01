from brownie import (
    accounts,
    Vault,
    config,
    network,
    AnyswapV5ERC20,
    Contract,
    interface,
)
from scripts.helpful import load_accounts


def test_deposit_withdraw():
    load_accounts()
    AMOUNT = 1 * 10**5  # 0.1 USDC
    musdc = interface.CErc20Interface(
        config["networks"][network.show_active()]["musdc"]
    )
    usdc = Contract.from_abi("USDC", musdc.underlying(), AnyswapV5ERC20.abi)
    if network.show_active() == "moonriver-fork":
        # mint USDC
        usdc.mint(
            accounts[0],
            AMOUNT,
            {"from": config["networks"][network.show_active()]["usdc_minter"]},
        )
    assert usdc.balanceOf(accounts[0]) >= AMOUNT
    vault = Vault.deploy(musdc.underlying(), {"from": accounts[0]})

    # deposit USDC
    usdc.approveAndCall(vault, AMOUNT, "", {"from": accounts[0]})

    # check balance
    assert vault.balances(accounts[0]) == AMOUNT
    assert vault.balance() == AMOUNT
    assert usdc.balanceOf(vault) == AMOUNT
    assert usdc.balanceOf(accounts[0]) == 0

    # withdraw USDC
    vault.withdraw(AMOUNT, {"from": accounts[0]})

    # check balance
    assert vault.balances(accounts[0]) == 0
    assert vault.balance() == 0
    assert usdc.balanceOf(vault) == 0
    assert usdc.balanceOf(accounts[0]) == AMOUNT

    if network.show_active() == "moonriver-fork":
        # burn USDC so balances are correct if USDC contracts are being used again in same VM instance
        usdc.burn(
            accounts[0],
            AMOUNT,
            {"from": config["networks"][network.show_active()]["usdc_minter"]},
        )
