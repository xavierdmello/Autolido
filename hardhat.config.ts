import { HardhatUserConfig } from "hardhat/config"
import "@nomicfoundation/hardhat-toolbox"
import "@nomiclabs/hardhat-etherscan"
import "./tasks/deploy"
import "dotenv/config"

const PRIVATE_KEY = process.env.PRIVATE_KEY
const MOONRIVER_RPC = process.env.MOONRIVER_RPC
const MOONSCAN_KEY = process.env.MOONSCAN_KEY

const config: HardhatUserConfig = {
    solidity: {
        version: "0.8.9",
        settings: {
            optimizer: {
                enabled: true,
                runs: 500,
            },
        },
    },
    defaultNetwork: "hardhat",
    networks: {
        hardhat: {
            forking: {
                enabled: true,
                url: MOONRIVER_RPC!,
                blockNumber: 2000000,
            },
        },
        moonriver: { url: MOONRIVER_RPC!, accounts: [PRIVATE_KEY!], chainId: 1285 },
        localhost: { url: "http://127.0.0.1:8545/", chainId: 31337 },
    },
    etherscan: {
        apiKey: {
            moonriver: MOONSCAN_KEY!,
        },
    },
    gasReporter: { enabled: false },
}

export default config
