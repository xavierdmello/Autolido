import { network, ethers } from "hardhat"

export function randint(min: number, max: number) {
    return Math.floor(Math.random() * (max - min + 1)) + min
}

export async function mintAnyswap(to: string, amount: string, tokenAddress: string) {
    let token = await ethers.getContractAt("AnyswapV5ERC20", tokenAddress)
    const minterAddress = await token.minters(0)

    // Unlock minter account
    await network.provider.request({
        method: "hardhat_impersonateAccount",
        params: [minterAddress],
    })
    const minter = await ethers.getSigner(minterAddress)

    // Mint tokens
    token = token.connect(minter)
    await token.mint(to, amount)

    // Relock minter account
    await network.provider.request({
        method: "hardhat_stopImpersonatingAccount",
        params: [minterAddress],
    })
}

export async function burnAnyswap(from: string, amount: string, tokenAddress: string) {
    let token = await ethers.getContractAt("AnyswapV5ERC20", tokenAddress)
    const minterAddress = await token.minters(0)

    // Unlock minter account
    await network.provider.request({
        method: "hardhat_impersonateAccount",
        params: [minterAddress],
    })
    const minter = await ethers.getSigner(minterAddress)

    // Burn tokens
    token = token.connect(minter)
    await token.burn(from, amount)

    // Relock minter account
    await network.provider.request({
        method: "hardhat_stopImpersonatingAccount",
        params: [minterAddress],
    })
}
