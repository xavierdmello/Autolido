import { burnAnyswap, mintAnyswap } from "../scripts/helpful"
import { ethers } from "hardhat"
import { Contract } from "ethers"
import { assert } from "chai"

describe("Mint", function () {
    let collateralCToken: Contract
    let underlying: Contract

    beforeEach(async function () {
        collateralCToken = await ethers.getContractAt(
            "CErc20Interface",
            "0xd0670AEe3698F66e2D4dAf071EB9c690d978BFA8"
        ) // mUSDC
        underlying = await ethers.getContractAt(
            "AnyswapV5ERC20",
            await collateralCToken.underlying()
        )
    })

    it("Should mint tokens", async function () {
        const amount = "100"
        const account = (await ethers.getSigners())[0]
        await mintAnyswap(account.address, amount, underlying.address)

        assert.equal(amount, (await underlying.balanceOf(account.address)).toString())

        // Destroy minted tokens
        await burnAnyswap(account.address, amount, underlying.address)
    })
})
