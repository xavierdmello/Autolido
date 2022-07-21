import { assert, expect } from "chai"
import { Contract } from "ethers"
import { deploy } from "../scripts/deploy"
import { mintAnyswap, randint } from "../scripts/helpful"
import { ethers } from "hardhat"
import { SignerWithAddress } from "@nomiclabs/hardhat-ethers/signers"

describe("Autolido", function () {
    let autolido: Contract

    let collateralCToken: Contract
    let borrowCToken: Contract
    let underlyingCollateral: Contract
    let underlyingBorrow: Contract

    let account: SignerWithAddress
    beforeEach(async function () {
        collateralCToken = await ethers.getContractAt(
            "CErc20Interface",
            "0xd0670AEe3698F66e2D4dAf071EB9c690d978BFA8"
        ) // mUSDC
        borrowCToken = await ethers.getContractAt(
            "CErc20Interface",
            "0xa0D116513Bd0B8f3F14e6Ea41556c6Ec34688e0f"
        ) // mxcKSM
        underlyingCollateral = await ethers.getContractAt(
            "AnyswapV5ERC20",
            await collateralCToken.underlying()
        ) // USDC.multi
        underlyingBorrow = await ethers.getContractAt(
            "EIP20Interface",
            await borrowCToken.underlying()
        ) // xcKSM
        autolido = await deploy("Autolido", [collateralCToken.address, borrowCToken.address])
        account = (await ethers.getSigners())[0]
    })

    it("Should have correct underlying tokens", async function () {
        assert.equal(underlyingCollateral.address, await autolido.collateralToken())
        assert.equal(underlyingBorrow.address, await autolido.borrowToken())
    })

    it("Should be able to have tokens deposited through approveAndCall()", async function () {
        const amount = "100"

        // Mint collateral
        await mintAnyswap(account.address, amount, underlyingCollateral.address)
        // Deposit collateral in autolido
        await underlyingCollateral.approveAndCall(autolido.address, amount, [])

        // Assert that autolido has a borrow balance
        assert.equal(
            (await collateralCToken.callStatic.balanceOfUnderlying(autolido.address)).toString(),
            (BigInt(amount)-BigInt(1)).toString()
        )
    })
})
