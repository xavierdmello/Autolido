// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "./AnyswapV5ERC20.sol";

// Contract for testing USDC.multi's approveAndCall() functionality
// Will be used to approve and deposit USDC in a single transaction
contract Vault {
    AnyswapV5ERC20 public USDC;
    mapping(address => uint256) public balances;

    constructor(address usdc_address) {
        USDC = AnyswapV5ERC20(usdc_address);
    }
    
    function balance() public view returns(uint) {
        return USDC.balanceOf(address(this));
    }

    // When approveAndCall() is called on the USDC contract
    // This allows tokens to be approved and deposited in one transcation
    function onTokenApproval(address owner, uint256 value, bytes memory data) external returns(bool){
        balances[owner] += value;
        USDC.transferFrom(owner, address(this), value);
        return true;
    }

    function withdraw(uint256 amount) public {
        require(amount <= balances[msg.sender]);
        balances[msg.sender] -= amount;
        USDC.transfer(msg.sender, amount);
    }
}