// SPDX-License-Identifier: BSD-3-Clause
pragma solidity ^0.8.9;

interface PriceOracle {
    /**
      * @notice Get the underlying price of a cToken asset
      * @param cToken The cToken to get the underlying price of
      * @return The price of the asset in USD as an unsigned integer scaled up by 10 ^ (36 - underlying asset decimals). E.g. WBTC has 8 decimal places, so the return value is scaled up by 1e28.
      */
    function getUnderlyingPrice(address cToken) virtual external view returns (uint);
}