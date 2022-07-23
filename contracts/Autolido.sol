// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "./AnyswapV5ERC20.sol";
import "./CErc20Interfaces.sol";
import "./EIP20Interface.sol";
import "./PriceOracle.sol";
import "./ComptrollerInterface.sol";

contract Autolido {
    uint256 public safteyMargin; // 80% of LTV by default
    uint256 public ltvDeviationThreshold = 5; // 5%
    mapping(address => uint256) public balances; // number of collateralCTokens user owns in autolido
    address public owner;

    CErc20Interface public collateralCToken; // cERC20 mUSDC
    CErc20Interface public borrowCToken; // cERC20 mxcKSM

    AnyswapV5ERC20 public collateralToken; // Anyswapv5ERC20 USDC.multi
    EIP20Interface public borrowToken; // XC20 xcKSM

    constructor(address collateralCTokenAddress, address borrowCTokenAddress) {
        collateralCToken = CErc20Interface(collateralCTokenAddress);
        borrowCToken = CErc20Interface(borrowCTokenAddress);

        collateralToken = AnyswapV5ERC20(collateralCToken.underlying());
        borrowToken = EIP20Interface(borrowCToken.underlying());

        owner = msg.sender;

        safteyMargin = 8 * 10**(collateralToken.decimals() - 1); // 80% of LTV

        // Automatically enter market
        enterMarket();
    }

    // Automatic way to deposit tokens. Will be called When approveAndCall() is called on the USDC contract.
    // This allows tokens to be approved and deposited in one transcation
    function onTokenApproval(
        address owner,
        uint256 value,
        bytes memory data
    ) external returns (bool) {
        _deposit(owner, value);
        return true;
    }

    // Manual way to deposit tokens. Must approve tokens first if calling this function.
    function deposit(uint256 value) public {
        _deposit(msg.sender, value);
    }

    // Internal deposit function
    function _deposit(address owner, uint256 value) private {
        // Deposit tokens into market
        balances[owner] += (value * 10**18) / collateralCToken.exchangeRateCurrent();
        collateralToken.transferFrom(owner, address(this), value);
        collateralToken.approve(address(collateralCToken), value);
        require(collateralCToken.mint(value) == 0, "Minting error");

        // Borrow borrowToken
        // TODO: Make sure borrow won't push autolido into liquidation range before a borrow (it shouldn't, but hey, who knows?)
        // This will fail on a local testnet, because xcKSM is a XC-20 token which depends special on rust code in the moonriver node
        require(borrowCToken.borrow(amountToBorrow(value)) == 0, "Borrow error");
    }

    // Calculates safe amount to borrow in borrow token, given amount of collateral token
    // TODO: Compare gas price of calculating borrow amount using this function vs. using getAccountLiquidity() twice
    function amountToBorrow(uint256 depositAmount) public view returns (uint256) {
        (, uint256 collateralFactorMantissa, ) = collateralCToken.comptroller().markets(
            address(collateralCToken)
        );

        // TODO: Compare gas cost of hardcoding borrowCToken.comptroller() and borrowCToken.comptroller().oracle() and calling those instead of reading them from the CToken contract.
        // This may reduce gas cost, but means that the comptroller will have to be manually updated if it changes. The comptroller *should* never change, but it *can*.
        uint256 depositTokenPrice = collateralCToken.comptroller().oracle().getUnderlyingPrice(
            address(collateralCToken)
        ); // Denominated in 36-(Decimals of Underlying) decimals
        uint256 depositUSDvalue = (depositAmount * depositTokenPrice) / 10**(36 - collateralToken.decimals()); // Same decimals as underlying

        uint256 maxBorrowUSD = (depositUSDvalue * collateralFactorMantissa) / 10**18;
        uint256 safeBorrowUSD = (maxBorrowUSD * safteyMargin) / 10**collateralToken.decimals(); // 80% of max borrow by default

        // This will fail on a local testnet, because xcKSM is a XC-20 token which depends special on rust code in the moonriver node
        uint256 borrowTokenPrice = borrowCToken.comptroller().oracle().getUnderlyingPrice(
            address(borrowCToken)
        ); // Denominated in 36-(Decimals of Underlying) decimals
        uint256 amountToBorrow = (safeBorrowUSD *
            10**(2 * borrowToken.decimals() - collateralToken.decimals())) / borrowTokenPrice; // Denominated in decimals of borrow token
        return amountToBorrow;
    }

    modifier onlyOwner() {
        assert(owner == msg.sender);
        _;
    }

    // !! DEV FUNCTION - MAY BE REMOVED LATER !!
    function enterMarket() public onlyOwner returns (uint256[] memory) {
        address[] memory market = new address[](1);
        market[0] = address(collateralCToken);
        require(collateralCToken.comptroller().enterMarkets(market)[0] == 0, "Enter Market Failed");
    }

    // !! DEV FUNCTION - MAY BE REMOVED LATER !!
    function exitMarket() public onlyOwner returns (uint256) {
        require(
            collateralCToken.comptroller().exitMarket(address(collateralCToken)) == 0,
            "Exit Market Failed"
        );
    }

    // !! DEV FUNCTION - MAY BE REMOVED LATER !!
    // redeemTokens: amount of collateralCTokens to redeem from Moonwell
    function withdraw(uint256 redeemTokens) public onlyOwner {
        uint256 balanceBefore = collateralToken.balanceOf(address(this));
        require(redeemTokens <= balances[msg.sender], "Withdrawal amount exceeds balance");

        balances[msg.sender] -= redeemTokens;

        require(collateralCToken.redeem(redeemTokens) == 0, "Withdrawal error");

        uint256 balanceAfter = collateralToken.balanceOf(address(this));
        collateralToken.transfer(msg.sender, balanceAfter - balanceBefore);
    }
}
