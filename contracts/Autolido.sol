// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "./AnyswapV5ERC20.sol";
import "../interfaces/CErc20Interfaces.sol";
import "../interfaces/EIP20Interface.sol";

contract Autolido {
    AnyswapV5ERC20 public collateralToken; // USDC.multi
    CErc20Interface public cToken; // cUSDC
    EIP20Interface public borrowToken; // xcKSM
    mapping(address => uint256) public cTokenBalances; // number of cTokens user owns in autolido

    constructor(address cTokenAddress) {
        cToken = CErc20Interface(cTokenAddress);
        collateralToken = AnyswapV5ERC20(cToken.underlying());
    }
    
    // When approveAndCall() is called on the USDC contract
    // This allows tokens to be approved and deposited in one transcation
    function onTokenApproval(address owner, uint256 value, bytes memory data) external returns(bool){
        cTokenBalances[owner] += (value*10**18)/cToken.exchangeRateCurrent();
        collateralToken.transferFrom(owner, address(this), value);
        collateralToken.approve(address(cToken), value);
        assert(cToken.mint(value)==0);
        return true;
    }

    // redeemTokens: amount of cTokens to redeem from Moonwell
    function withdraw(uint256 redeemTokens) public {
        uint balanceBefore = collateralToken.balanceOf(address(this));
        require(redeemTokens <= cTokenBalances[msg.sender], "Withdrawal amount exceeds balance");

        cTokenBalances[msg.sender] -= redeemTokens;

        require(cToken.redeem(redeemTokens)==0, "Withdrawal error");

        uint balanceAfter = collateralToken.balanceOf(address(this));
        collateralToken.transfer(msg.sender, balanceAfter-balanceBefore);
    }
}