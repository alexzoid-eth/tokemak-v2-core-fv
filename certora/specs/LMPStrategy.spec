using BalancerAuraDestinationVault as BalancerDestVault;
using CurveConvexDestinationVault as CurveDestVault;
using SystemRegistry as systemRegistry;

/////////////////// METHODS ///////////////////////

methods {
    
    // LMPStrategyHarness
    function getDestinationSummaryStatsExternal(address, uint256, LMPStrategy.RebalanceDirection, uint256) 
        external returns (IStrategy.SummaryStats);
    function getSwapCostOffsetTightenThresholdInViolations() external returns (uint16) envfree;
    // Immutable
    function lmpVault() external returns (address) envfree;
    function pauseRebalancePeriodInDays() external returns (uint16) envfree;
    function maxPremium() external returns (int256) envfree;
    function maxDiscount() external returns (int256) envfree;
    function staleDataToleranceInSeconds() external returns (uint40) envfree;
    function swapCostOffsetInitInDays() external returns (uint16) envfree;
    function swapCostOffsetTightenThresholdInViolations() external returns (uint16) envfree;
    function swapCostOffsetTightenStepInDays() external returns (uint16) envfree;
    function swapCostOffsetRelaxThresholdInDays() external returns (uint16) envfree;
    function swapCostOffsetRelaxStepInDays() external returns (uint16) envfree;
    function swapCostOffsetMaxInDays() external returns (uint16) envfree;
    function swapCostOffsetMinInDays() external returns (uint16) envfree;
    function navLookback1InDays() external returns (uint8) envfree;
    function navLookback2InDays() external returns (uint8) envfree;
    function navLookback3InDays() external returns (uint8) envfree;
    function maxNormalOperationSlippage() external returns (uint256) envfree;
    function maxTrimOperationSlippage() external returns (uint256) envfree;
    function maxEmergencyOperationSlippage() external returns (uint256) envfree;
    function maxShutdownOperationSlippage() external returns (uint256) envfree;
    function maxAllowedDiscount() external returns (int256) envfree;
    function weightBase() external returns (uint256) envfree;
    function weightFee() external returns (uint256) envfree;
    function weightIncentive() external returns (uint256) envfree;
    function weightSlashing() external returns (uint256) envfree;
    function weightPriceDiscountExit() external returns (int256) envfree;
    function weightPriceDiscountEnter() external returns (int256) envfree;
    function weightPricePremium() external returns (int256) envfree;
    function lstPriceGapTolerance() external returns (uint256) envfree;
    // State Variables
    function lastPausedTimestamp() external returns (uint40) envfree;
    function lastAddTimestampByDestination(address destination) external returns (uint40) envfree;
    function violationTrackingState() external returns (uint8, uint8, uint16) envfree;
    //function navTrackingState() external returns (uint8, uint8, uint40, uint256[]) envfree;
    function lastRebalanceTimestamp() external returns (uint40) envfree;
    // Functions 
    function verifyRebalance(IStrategy.RebalanceParams params, IStrategy.SummaryStats outSummary) 
        external returns (bool, string);
    function getRebalanceOutSummaryStats(IStrategy.RebalanceParams rebalanceParams) 
        external returns (IStrategy.SummaryStats);
    function navUpdate(uint256 navPerShare) external;
    function rebalanceSuccessfullyExecuted(IStrategy.RebalanceParams params) external;
    function swapCostOffsetPeriodInDays() external returns (uint16);
    function paused() external returns (bool);
    
    // Can help reduce complexity, think carefully about implications before using.
    // May need to think of a more clever way to summarize this.
    // function LMPStrategy.getRebalanceValueStats(IStrategy.RebalanceParams memory input) internal returns (LMPStrategy.RebalanceValueStats memory) 
    //    => getRebalanceValueStatsCVL(input);

    // ILMPVault
    // Summarized instead of linked to help with runtime. 
    // The two state changing functions don't change any relevant state and aren't implemented.
    // The rest of the functions are getters so ghost summary has the same effect as linking.
    function _.addToWithdrawalQueueHead(address) external => NONDET;
    function _.addToWithdrawalQueueTail(address) external => NONDET;
    function _.totalIdle() external => totalIdleCVL expect uint256;
    function _.asset() external => assetCVL expect uint256;
    function _.totalAssets() external => totalAssetsCVL expect uint256;
    function _.isDestinationRegistered(address dest) external => isDestinationRegisteredCVL[dest] expect bool;
    function _.isDestinationQueuedForRemoval(address dest) external => isDestinationQueuedForRemovalCVL[dest] expect bool;
    function _.getDestinationInfo(address dest) external => getDestinationInfoCVL(dest) expect LMPDebt.DestinationInfo;

    // IRootPriceOracle
    function _.getPriceInEth(address token) external with (env e) 
        => getPriceInEthCVL[token][e.block.timestamp] expect (uint256);
    function _.getSpotPriceInEth(address, address) external => DISPATCHER(true);

    // IDestinationVault
    function _.getStats() external => DISPATCHER(true);
    function _.getValidatedSpotPrice() external => DISPATCHER(true);
    function _.isShutdown() external => DISPATCHER(true);
    function _.getPool() external => DISPATCHER(true);
    function _.underlying() external => DISPATCHER(true);
    function _.underlyingTokens() external => DISPATCHER(true);
    function _.debtValue(uint256) external => DISPATCHER(true);

    // IDexLSTStats
    function _.current() external => NONDET; // can be dispatched if returned values are important

    // IBalancerComposableStablePool
    function _.getBptIndex() external => getBptIndexCVL expect (uint256);

    // ISystemRegistry
    function _.accessController() external => DISPATCHER(true); // needed in constructor, rest is handled by linking

    // IIncentivesPricingStats
    function _.getPriceOrZero(address, uint40) external => DISPATCHER(true);

    // ERC20
    function _.name() external => DISPATCHER(true);
    function _.symbol() external => DISPATCHER(true);
    function _.totalSupply() external => DISPATCHER(true);
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.allowance(address,address) external => DISPATCHER(true);
    function _.approve(address,uint256) external => DISPATCHER(true);
    function _.transfer(address,uint256) external => DISPATCHER(true);
    function _.transferFrom(address,address,uint256) external => DISPATCHER(true);
    // ERC20's `decimals` summarized as 6, 8 or 18 (validDecimal), can be changed to ALWAYS(18) for better runtime.
    // This helps with runtime because arbitrary decimal value creates many nonlinear operations.
    function _.decimals() external => ALWAYS(18); // validDecimal expect uint256; // validDecimal is 6, 8 or 18 for a better summary
}

///////////////// DEFINITIONS /////////////////////

definition MAX_NAV_TRACKING() returns uint8 = require_uint8(91);

////////////////// FUNCTIONS //////////////////////

//
// LMPStrategy
//

function getRebalanceValueStatsCVL(IStrategy.RebalanceParams input) returns LMPStrategy.RebalanceValueStats {
    LMPStrategy.RebalanceValueStats tmp;
    return tmp;
}

//  LMPStrategyInt.getDefaultConfig()
function defaultConfig() {
    require(swapCostOffsetInitInDays() == require_uint16(28));
    require(swapCostOffsetTightenThresholdInViolations() == require_uint16(5));
    require(swapCostOffsetTightenStepInDays() == require_uint16(3));
    require(swapCostOffsetRelaxThresholdInDays() == require_uint16(20));
    require(swapCostOffsetRelaxStepInDays() == require_uint16(3));
    require(swapCostOffsetMaxInDays() == require_uint16(60));
    require(swapCostOffsetMinInDays() == require_uint16(10));
    require(navLookback1InDays() == require_uint8(30));
    require(navLookback2InDays() == require_uint8(60));
    require(navLookback3InDays() == require_uint8(90));
    require(maxNormalOperationSlippage() == require_uint256(10 ^ 16)); // 1%
    require(maxTrimOperationSlippage() == require_uint256(2 * 10 ^ 16)); // 2%
    require(maxEmergencyOperationSlippage() == require_uint256(25 * 10 ^ 15)); // 2.5%
    require(maxShutdownOperationSlippage() == require_uint256(15 * 10 ^ 15)); // 1.5%
    require(weightBase() == require_uint256(10 ^ 6));
    require(weightFee() == require_uint256(10 ^ 6));
    require(weightIncentive() == require_uint256(9 * 10 ^ 5));
    require(weightSlashing() == require_uint256(10 ^ 6));
    require(weightPriceDiscountExit() == require_int256(75 * 10 ^ 4));
    require(weightPriceDiscountEnter() == require_int256(0));
    require(weightPricePremium() == require_int256(10 ^ 6));
    require(pauseRebalancePeriodInDays() == require_uint16(90));
    require(maxPremium() == require_int256(10 ^ 16)); // 1%
    require(maxDiscount() == require_int256(2 * 10 ^ 16)); // 2%
    require(staleDataToleranceInSeconds() == require_uint40(2 * 60 * 60 * 24)); // 2 days
    require(maxAllowedDiscount() == require_int256(5 * 10 ^ 16));
    require(lstPriceGapTolerance() == require_uint256(10 * 60 * 60 * 24)); // 10 days
}

// LMPStrategyConfig.validate()
function configValidate() {
    
    require(swapCostOffsetInitInDays() >= swapCostOffsetMinInDays());
    require(swapCostOffsetInitInDays() <= swapCostOffsetMaxInDays());
    
    require(swapCostOffsetMaxInDays() > swapCostOffsetMinInDays());

    require(navLookback1InDays() < MAX_NAV_TRACKING());
    require(navLookback2InDays() < MAX_NAV_TRACKING());
    require(navLookback3InDays() < MAX_NAV_TRACKING());

    require(navLookback1InDays() < navLookback2InDays());
    require(navLookback2InDays() < navLookback3InDays());

    require(maxPremium() >= 0 && maxPremium() <= require_int256(10 ^ 18));

    require(maxDiscount() >= 0 && maxDiscount() <= require_int256(10 ^ 18));

    require(maxShutdownOperationSlippage() != 0);
    require(maxEmergencyOperationSlippage() != 0);
    require(maxTrimOperationSlippage() != 0);
    require(maxNormalOperationSlippage() != 0);
    require(navLookback1InDays() != 0);
}

function initConstructor(env e) {

    require(lmpVault() != 0);

    // defaultConfig();
    configValidate();

    require(e.block.timestamp > 0 && e.block.timestamp < max_uint40);
    require(lastRebalanceTimestamp() >= require_uint40(e.block.timestamp));
}

//
// ILMPVault
//

function getDestinationInfoCVL(address dest) returns LMPDebt.DestinationInfo {
    LMPDebt.DestinationInfo info;
    return info;
}

function currentCVL() returns IDexLSTStats.DexLSTStatsData {
    IDexLSTStats.DexLSTStatsData data;
    return data;
}

///////////////// GHOSTS & HOOKS //////////////////

//
// LMPStrategy
//

ghost uint256 getBptIndexCVL;
ghost uint256 validDecimal {
    axiom validDecimal == 6 || validDecimal == 8 || validDecimal == 18;
}

//
// ILMPVault
//

ghost uint256 totalIdleCVL;
ghost uint256 assetCVL;
ghost uint256 totalAssetsCVL;
ghost mapping(address => bool) isDestinationRegisteredCVL;
ghost mapping(address => bool) isDestinationQueuedForRemovalCVL;

//
// IRootPriceOracle summaries
//

ghost mapping(address => mapping(uint256 => uint256)) getPriceInEthCVL;

//
// Ghost copy of `_swapCostOffsetPeriod`
//

ghost uint16 _swapCostOffsetPeriodGhost;

hook Sload uint16 defaultValue _swapCostOffsetPeriod STORAGE {
    require(_swapCostOffsetPeriodGhost == defaultValue);
}

hook Sstore _swapCostOffsetPeriod uint16 defaultValue STORAGE {
    _swapCostOffsetPeriodGhost = defaultValue;
}

///////////////// PROPERTIES //////////////////////

use builtin rule sanity;

// Offset period must be between swapCostOffsetMaxInDays and swapCostOffsetMinInDays.
invariant offsetIsInBetween()
    _swapCostOffsetPeriodGhost <= swapCostOffsetMaxInDays() && _swapCostOffsetPeriodGhost >= swapCostOffsetMinInDays() {
    preserved with(env e) {
        initConstructor(e);
    }
}

// `violationTrackingState.violationCount` must not be increased by more than 1
rule cantJumpTwoViolationsAtOnce(env e, method f) {

    initConstructor(e);

    uint16 numOfViolationsBefore;
    numOfViolationsBefore,_,_ = violationTrackingState();

    calldataarg args;
    f(e, args);

    uint16 numOfViolationsAfter;
    numOfViolationsAfter,_,_ = violationTrackingState();

    assert numOfViolationsAfter - numOfViolationsBefore <= 1;
}



