import { task } from "hardhat/config"
import { HardhatRuntimeEnvironment } from "hardhat/types"
import { Contract } from "ethers"

task("deploy", "Deploys a contract")
    .addPositionalParam("contract", "Name of contract to deploy")
    .addOptionalVariadicPositionalParam("args", "Args to pass into constructor")
    .setAction(async (taskArgs, hre: HardhatRuntimeEnvironment) => {
        if (taskArgs.args == undefined) {
            await deploy(hre, taskArgs.contract)
        } else {
            await deploy(hre, taskArgs.contract, taskArgs.args)
        }
    })

task("vdeploy", "Deploys and verifies a contract")
    .addPositionalParam("contract", "Name of contract to deploy")
    .addOptionalVariadicPositionalParam("args", "Args to pass into constructor")
    .setAction(async (taskArgs, hre: HardhatRuntimeEnvironment) => {
        if (taskArgs.args == undefined) {
            await deployAndVerify(hre, taskArgs.contract)
        } else {
            await deployAndVerify(hre, taskArgs.contract, taskArgs.args)
        }
    })

async function deploy(hre: HardhatRuntimeEnvironment, contractName: string, args?: any[]) {
    const contractFactory = await hre.ethers.getContractFactory(contractName)

    console.log(`Deploying ${contractName}...`)
    let contract: Contract
    if (typeof args === "undefined") {
        contract = await contractFactory.deploy()
    } else {
        contract = await contractFactory.deploy(...args)
    }

    await contract.deployed()
    console.log(`${contractName} deployed at ${contract.address}`)
    return contract
}

async function deployAndVerify(hre: HardhatRuntimeEnvironment, contractName: string, args?: any[]) {
    const contract = await deploy(hre, contractName, args)

    if (
        (hre.network.config.chainId === 4 && process.env.ETHERSCAN_KEY) ||
        (hre.network.config.chainId === 43113 && process.env.SNOWTRACE_KEY)
    ) {
        await contract.deployTransaction.wait(3)
        await verify(hre, contract.address, args)
    }

    return contract
}

async function verify(hre: HardhatRuntimeEnvironment, contractAddress: string, args?: any[]) {
    console.log("Verifying contract... ")
    try {
        if (typeof args === "undefined") {
            await hre.run("verify:verify", {
                address: contractAddress,
                constructorArguments: [],
            })
        } else {
            await hre.run("verify:verify", {
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

module.exports = {}
