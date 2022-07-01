// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "./AnyswapV5ERC20.sol";
import "../interfaces/CErc20Interfaces.sol";
contract Autolido {
    AnyswapV5ERC20 public USDC;
    CErc20Interface public mUSDC;
    mapping(address => uint256) public balances;

    constructor(address musdc_address) {
        mUSDC = CErc20Interface(musdc_address);
        USDC = AnyswapV5ERC20(mUSDC.underlying());
    }
    
    function balance() public view returns(uint) {
        return mUSDC.balanceOf(address(this));
    }

    // When approveAndCall() is called on the USDC contract
    // This allows tokens to be approved and deposited in one transcation
    function onTokenApproval(address owner, uint256 value, bytes memory data) external returns(bool){
        balances[owner] += value;
        USDC.transferFrom(owner, address(this), value);
        USDC.approve(address(mUSDC), value);
        assert(mUSDC.mint(value)==0);
        return true;
    }

    function withdraw(uint256 amount) public {
        require(amount <= balances[msg.sender]);
        balances[msg.sender] -= amount;
        USDC.transfer(msg.sender, amount);
    }
}