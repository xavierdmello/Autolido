// imports
import { ethers, run, network } from "hardhat"
import "@nomiclabs/hardhat-etherscan"
import { Contract } from "ethers"

export async function deploy(contractName: string, args?: any[]) {
    const contractFactory = await ethers.getContractFactory(contractName)

    let contract: Contract
    if (typeof args === "undefined") {
        contract = await contractFactory.deploy()
    } else {
        contract = await contractFactory.deploy(...args)
    }

    await contract.deployed()
    return contract
}

export async function deployAndVerify(contractName: string, args?: any[]) {
    const contract = await deploy(contractName, args)

    if (
        (network.config.chainId === 4 && process.env.ETHERSCAN_KEY) ||
        (network.config.chainId === 43113 && process.env.SNOWTRACE_KEY)
    ) {
        await contract.deployTransaction.wait(3)
        await verify(contract.address, args)
    }

    return contract
}

export async function verify(contractAddress: string, args?: any[]) {
    console.log("Verifying contract... ")
    try {
        if (typeof args === "undefined") {
            await run("verify:verify", {
                address: contractAddress,
                constructorArguments: [],
            })
        } else {
            await run("verify:verify", {
                address: contractAddress,
                constructorArguments: args,
            })
        }
    } catch (e) {
        if (e instanceof Error) {
            if (e.message.toLowerCase().includes("already verified")) {
                console.log("Already verified!")
            } else {
                console.log(e)
            }
        } else {
            console.log("Unexpected error", e)
        }
    }
}
