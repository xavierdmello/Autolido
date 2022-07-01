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


def test_deposit():
    load_accounts()
    AMOUNT = 1 * 10**5  # 0.1 USDC
    musdc = interface.CErc20Interface(
        config["networks"][network.show_active()]["musdc"]
    )
    usdc = Contract.from_abi("USDC", musdc.underlying(), AnyswapV5ERC20.abi)
    if network.show_active() == "moonriver-fork":
        # mint USDC
        tx = usdc.mint(
            accounts[0],
            AMOUNT,
            {"from": config["networks"][network.show_active()]["usdc_minter"]},
        )
        tx.wait(1)

    assert usdc.balanceOf(accounts[0]) >= AMOUNT

    autolido = Autolido.deploy(musdc, {"from": accounts[0]})

    # deposit USDC
    tx = usdc.approveAndCall(autolido, AMOUNT, "", {"from": accounts[0]})
    tx.wait(1)

    # check balance
    assert autolido.balances(accounts[0]) == AMOUNT
    if network.show_active() == "moonriver-fork":
        # mine block to make sure balanceOfUnderlying() calls on the correct block
        chain.mine()
    assert musdc.balanceOfUnderlying.call(autolido, {"from": accounts[0]}) == AMOUNT
    assert usdc.balanceOf(accounts[0]) == 0


# def test_withdraw():
#     load_accounts()
#     AMOUNT = 1 * 10**5  # 0.1 USDC
#     musdc = interface.CErc20Interface(
#         config["networks"][network.show_active()]["musdc"]
#     )
#     usdc = Contract.from_abi("USDC", musdc.underlying(), AnyswapV5ERC20.abi)
#     if network.show_active() == "moonriver-fork":
#         # mint USDC
#         usdc.mint(
#             accounts[0],
#             AMOUNT,
#             {"from": config["networks"][network.show_active()]["usdc_minter"]},
#         )
#     assert usdc.balanceOf(accounts[0]) >= AMOUNT
#     autolido = Autolido.deploy(musdc, {"from": accounts[0]})
#     # deposit USDC
#     usdc.approveAndCall(vault, AMOUNT, "", {"from": accounts[0]})

#     # withdraw USDC
#     autolido.withdraw(AMOUNT, {"from": accounts[0]})

#     # check balance
#     assert vault.balances(accounts[0]) == 0
#     assert vault.balance() == 0
#     assert usdc.balanceOf(vault) == 0
#     assert usdc.balanceOf(accounts[0]) == AMOUNT
