pragma solidity 0.8.24;


// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.4.0) (token/ERC20/IERC20.sol)
/**
 * @dev Interface of the ERC-20 standard as defined in the ERC.
 */
interface IERC20 {
    /**
     * @dev Emitted when `value` tokens are moved from one account (`from`) to
     * another (`to`).
     *
     * Note that `value` may be zero.
     */
    event Transfer(address indexed from, address indexed to, uint256 value);

    /**
     * @dev Emitted when the allowance of a `spender` for an `owner` is set by
     * a call to {approve}. `value` is the new allowance.
     */
    event Approval(address indexed owner, address indexed spender, uint256 value);

    /**
     * @dev Returns the value of tokens in existence.
     */
    function totalSupply() external view returns (uint256);

    /**
     * @dev Returns the value of tokens owned by `account`.
     */
    function balanceOf(address account) external view returns (uint256);

    /**
     * @dev Moves a `value` amount of tokens from the caller's account to `to`.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transfer(address to, uint256 value) external returns (bool);

    /**
     * @dev Returns the remaining number of tokens that `spender` will be
     * allowed to spend on behalf of `owner` through {transferFrom}. This is
     * zero by default.
     *
     * This value changes when {approve} or {transferFrom} are called.
     */
    function allowance(address owner, address spender) external view returns (uint256);

    /**
     * @dev Sets a `value` amount of tokens as the allowance of `spender` over the
     * caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * IMPORTANT: Beware that changing an allowance with this method brings the risk
     * that someone may use both the old and the new allowance by unfortunate
     * transaction ordering. One possible solution to mitigate this race
     * condition is to first reduce the spender's allowance to 0 and set the
     * desired value afterwards:
     * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
     *
     * Emits an {Approval} event.
     */
    function approve(address spender, uint256 value) external returns (bool);

    /**
     * @dev Moves a `value` amount of tokens from `from` to `to` using the
     * allowance mechanism. `value` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     */
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

interface IERC165 {
    /**
     * @dev Returns true if this contract implements the interface defined by
     * `interfaceId`. See the corresponding
     * https://eips.ethereum.org/EIPS/eip-165#how-interfaces-are-identified[ERC section]
     * to learn more about how these ids are created.
     *
     * This function call must use less than 30 000 gas.
     */
    function supportsInterface(bytes4 interfaceId) external view returns (bool);
}

interface IERC1363 is IERC20, IERC165 {
    /*
     * Note: the ERC-165 identifier for this interface is 0xb0202a11.
     * 0xb0202a11 ===
     *   bytes4(keccak256('transferAndCall(address,uint256)')) ^
     *   bytes4(keccak256('transferAndCall(address,uint256,bytes)')) ^
     *   bytes4(keccak256('transferFromAndCall(address,address,uint256)')) ^
     *   bytes4(keccak256('transferFromAndCall(address,address,uint256,bytes)')) ^
     *   bytes4(keccak256('approveAndCall(address,uint256)')) ^
     *   bytes4(keccak256('approveAndCall(address,uint256,bytes)'))
     */

    /**
     * @dev Moves a `value` amount of tokens from the caller's account to `to`
     * and then calls {IERC1363Receiver-onTransferReceived} on `to`.
     * @param to The address which you want to transfer to.
     * @param value The amount of tokens to be transferred.
     * @return A boolean value indicating whether the operation succeeded unless throwing.
     */
    function transferAndCall(address to, uint256 value) external returns (bool);

    /**
     * @dev Moves a `value` amount of tokens from the caller's account to `to`
     * and then calls {IERC1363Receiver-onTransferReceived} on `to`.
     * @param to The address which you want to transfer to.
     * @param value The amount of tokens to be transferred.
     * @param data Additional data with no specified format, sent in call to `to`.
     * @return A boolean value indicating whether the operation succeeded unless throwing.
     */
    function transferAndCall(address to, uint256 value, bytes calldata data) external returns (bool);

    /**
     * @dev Moves a `value` amount of tokens from `from` to `to` using the allowance mechanism
     * and then calls {IERC1363Receiver-onTransferReceived} on `to`.
     * @param from The address which you want to send tokens from.
     * @param to The address which you want to transfer to.
     * @param value The amount of tokens to be transferred.
     * @return A boolean value indicating whether the operation succeeded unless throwing.
     */
    function transferFromAndCall(address from, address to, uint256 value) external returns (bool);

    /**
     * @dev Moves a `value` amount of tokens from `from` to `to` using the allowance mechanism
     * and then calls {IERC1363Receiver-onTransferReceived} on `to`.
     * @param from The address which you want to send tokens from.
     * @param to The address which you want to transfer to.
     * @param value The amount of tokens to be transferred.
     * @param data Additional data with no specified format, sent in call to `to`.
     * @return A boolean value indicating whether the operation succeeded unless throwing.
     */
    function transferFromAndCall(address from, address to, uint256 value, bytes calldata data) external returns (bool);

    /**
     * @dev Sets a `value` amount of tokens as the allowance of `spender` over the
     * caller's tokens and then calls {IERC1363Spender-onApprovalReceived} on `spender`.
     * @param spender The address which will spend the funds.
     * @param value The amount of tokens to be spent.
     * @return A boolean value indicating whether the operation succeeded unless throwing.
     */
    function approveAndCall(address spender, uint256 value) external returns (bool);

    /**
     * @dev Sets a `value` amount of tokens as the allowance of `spender` over the
     * caller's tokens and then calls {IERC1363Spender-onApprovalReceived} on `spender`.
     * @param spender The address which will spend the funds.
     * @param value The amount of tokens to be spent.
     * @param data Additional data with no specified format, sent in call to `spender`.
     * @return A boolean value indicating whether the operation succeeded unless throwing.
     */
    function approveAndCall(address spender, uint256 value, bytes calldata data) external returns (bool);
}

// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.3.0) (token/ERC20/utils/SafeERC20.sol)
/**
 * @title SafeERC20
 * @dev Wrappers around ERC-20 operations that throw on failure (when the token
 * contract returns false). Tokens that return no value (and instead revert or
 * throw on failure) are also supported, non-reverting calls are assumed to be
 * successful.
 * To use this library you can add a `using SafeERC20 for IERC20;` statement to your contract,
 * which allows you to call the safe operations as `token.safeTransfer(...)`, etc.
 */
library SafeERC20 {
    /**
     * @dev An operation with an ERC-20 token failed.
     */
    error SafeERC20FailedOperation(address token);

    /**
     * @dev Indicates a failed `decreaseAllowance` request.
     */
    error SafeERC20FailedDecreaseAllowance(address spender, uint256 currentAllowance, uint256 requestedDecrease);

    /**
     * @dev Transfer `value` amount of `token` from the calling contract to `to`. If `token` returns no value,
     * non-reverting calls are assumed to be successful.
     */
    function safeTransfer(IERC20 token, address to, uint256 value) internal {
        _callOptionalReturn(token, abi.encodeCall(token.transfer, (to, value)));
    }

    /**
     * @dev Transfer `value` amount of `token` from `from` to `to`, spending the approval given by `from` to the
     * calling contract. If `token` returns no value, non-reverting calls are assumed to be successful.
     */
    function safeTransferFrom(IERC20 token, address from, address to, uint256 value) internal {
        _callOptionalReturn(token, abi.encodeCall(token.transferFrom, (from, to, value)));
    }

    /**
     * @dev Variant of {safeTransfer} that returns a bool instead of reverting if the operation is not successful.
     */
    function trySafeTransfer(IERC20 token, address to, uint256 value) internal returns (bool) {
        return _callOptionalReturnBool(token, abi.encodeCall(token.transfer, (to, value)));
    }

    /**
     * @dev Variant of {safeTransferFrom} that returns a bool instead of reverting if the operation is not successful.
     */
    function trySafeTransferFrom(IERC20 token, address from, address to, uint256 value) internal returns (bool) {
        return _callOptionalReturnBool(token, abi.encodeCall(token.transferFrom, (from, to, value)));
    }

    /**
     * @dev Increase the calling contract's allowance toward `spender` by `value`. If `token` returns no value,
     * non-reverting calls are assumed to be successful.
     *
     * IMPORTANT: If the token implements ERC-7674 (ERC-20 with temporary allowance), and if the "client"
     * smart contract uses ERC-7674 to set temporary allowances, then the "client" smart contract should avoid using
     * this function. Performing a {safeIncreaseAllowance} or {safeDecreaseAllowance} operation on a token contract
     * that has a non-zero temporary allowance (for that particular owner-spender) will result in unexpected behavior.
     */
    function safeIncreaseAllowance(IERC20 token, address spender, uint256 value) internal {
        uint256 oldAllowance = token.allowance(address(this), spender);
        forceApprove(token, spender, oldAllowance + value);
    }

    /**
     * @dev Decrease the calling contract's allowance toward `spender` by `requestedDecrease`. If `token` returns no
     * value, non-reverting calls are assumed to be successful.
     *
     * IMPORTANT: If the token implements ERC-7674 (ERC-20 with temporary allowance), and if the "client"
     * smart contract uses ERC-7674 to set temporary allowances, then the "client" smart contract should avoid using
     * this function. Performing a {safeIncreaseAllowance} or {safeDecreaseAllowance} operation on a token contract
     * that has a non-zero temporary allowance (for that particular owner-spender) will result in unexpected behavior.
     */
    function safeDecreaseAllowance(IERC20 token, address spender, uint256 requestedDecrease) internal {
        unchecked {
            uint256 currentAllowance = token.allowance(address(this), spender);
            if (currentAllowance < requestedDecrease) {
                revert SafeERC20FailedDecreaseAllowance(spender, currentAllowance, requestedDecrease);
            }
            forceApprove(token, spender, currentAllowance - requestedDecrease);
        }
    }

    /**
     * @dev Set the calling contract's allowance toward `spender` to `value`. If `token` returns no value,
     * non-reverting calls are assumed to be successful. Meant to be used with tokens that require the approval
     * to be set to zero before setting it to a non-zero value, such as USDT.
     *
     * NOTE: If the token implements ERC-7674, this function will not modify any temporary allowance. This function
     * only sets the "standard" allowance. Any temporary allowance will remain active, in addition to the value being
     * set here.
     */
    function forceApprove(IERC20 token, address spender, uint256 value) internal {
        bytes memory approvalCall = abi.encodeCall(token.approve, (spender, value));

        if (!_callOptionalReturnBool(token, approvalCall)) {
            _callOptionalReturn(token, abi.encodeCall(token.approve, (spender, 0)));
            _callOptionalReturn(token, approvalCall);
        }
    }

    /**
     * @dev Performs an {ERC1363} transferAndCall, with a fallback to the simple {ERC20} transfer if the target has no
     * code. This can be used to implement an {ERC721}-like safe transfer that rely on {ERC1363} checks when
     * targeting contracts.
     *
     * Reverts if the returned value is other than `true`.
     */
    function transferAndCallRelaxed(IERC1363 token, address to, uint256 value, bytes memory data) internal {
        if (to.code.length == 0) {
            safeTransfer(token, to, value);
        } else if (!token.transferAndCall(to, value, data)) {
            revert SafeERC20FailedOperation(address(token));
        }
    }

    /**
     * @dev Performs an {ERC1363} transferFromAndCall, with a fallback to the simple {ERC20} transferFrom if the target
     * has no code. This can be used to implement an {ERC721}-like safe transfer that rely on {ERC1363} checks when
     * targeting contracts.
     *
     * Reverts if the returned value is other than `true`.
     */
    function transferFromAndCallRelaxed(
        IERC1363 token,
        address from,
        address to,
        uint256 value,
        bytes memory data
    ) internal {
        if (to.code.length == 0) {
            safeTransferFrom(token, from, to, value);
        } else if (!token.transferFromAndCall(from, to, value, data)) {
            revert SafeERC20FailedOperation(address(token));
        }
    }

    /**
     * @dev Performs an {ERC1363} approveAndCall, with a fallback to the simple {ERC20} approve if the target has no
     * code. This can be used to implement an {ERC721}-like safe transfer that rely on {ERC1363} checks when
     * targeting contracts.
     *
     * NOTE: When the recipient address (`to`) has no code (i.e. is an EOA), this function behaves as {forceApprove}.
     * Opposedly, when the recipient address (`to`) has code, this function only attempts to call {ERC1363-approveAndCall}
     * once without retrying, and relies on the returned value to be true.
     *
     * Reverts if the returned value is other than `true`.
     */
    function approveAndCallRelaxed(IERC1363 token, address to, uint256 value, bytes memory data) internal {
        if (to.code.length == 0) {
            forceApprove(token, to, value);
        } else if (!token.approveAndCall(to, value, data)) {
            revert SafeERC20FailedOperation(address(token));
        }
    }

    /**
     * @dev Imitates a Solidity high-level call (i.e. a regular function call to a contract), relaxing the requirement
     * on the return value: the return value is optional (but if data is returned, it must not be false).
     * @param token The token targeted by the call.
     * @param data The call data (encoded using abi.encode or one of its variants).
     *
     * This is a variant of {_callOptionalReturnBool} that reverts if call fails to meet the requirements.
     */
    function _callOptionalReturn(IERC20 token, bytes memory data) private {
        uint256 returnSize;
        uint256 returnValue;
        assembly ("memory-safe") {
            let success := call(gas(), token, 0, add(data, 0x20), mload(data), 0, 0x20)
            // bubble errors
            if iszero(success) {
                let ptr := mload(0x40)
                returndatacopy(ptr, 0, returndatasize())
                revert(ptr, returndatasize())
            }
            returnSize := returndatasize()
            returnValue := mload(0)
        }

        if (returnSize == 0 ? address(token).code.length == 0 : returnValue != 1) {
            revert SafeERC20FailedOperation(address(token));
        }
    }

    /**
     * @dev Imitates a Solidity high-level call (i.e. a regular function call to a contract), relaxing the requirement
     * on the return value: the return value is optional (but if data is returned, it must not be false).
     * @param token The token targeted by the call.
     * @param data The call data (encoded using abi.encode or one of its variants).
     *
     * This is a variant of {_callOptionalReturn} that silently catches all reverts and returns a bool instead.
     */
    function _callOptionalReturnBool(IERC20 token, bytes memory data) private returns (bool) {
        bool success;
        uint256 returnSize;
        uint256 returnValue;
        assembly ("memory-safe") {
            success := call(gas(), token, 0, add(data, 0x20), mload(data), 0, 0x20)
            returnSize := returndatasize()
            returnValue := mload(0)
        }
        return success && (returnSize == 0 ? address(token).code.length > 0 : returnValue == 1);
    }
}

abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }

    function _msgData() internal view virtual returns (bytes calldata) {
        return msg.data;
    }

    function _contextSuffixLength() internal view virtual returns (uint256) {
        return 0;
    }
}

// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.0.0) (access/Ownable.sol)
/**
 * @dev Contract module which provides a basic access control mechanism, where
 * there is an account (an owner) that can be granted exclusive access to
 * specific functions.
 *
 * The initial owner is set to the address provided by the deployer. This can
 * later be changed with {transferOwnership}.
 *
 * This module is used through inheritance. It will make available the modifier
 * `onlyOwner`, which can be applied to your functions to restrict their use to
 * the owner.
 */
abstract contract Ownable is Context {
    address private _owner;

    /**
     * @dev The caller account is not authorized to perform an operation.
     */
    error OwnableUnauthorizedAccount(address account);

    /**
     * @dev The owner is not a valid owner account. (eg. `address(0)`)
     */
    error OwnableInvalidOwner(address owner);

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev Initializes the contract setting the address provided by the deployer as the initial owner.
     */
    constructor(address initialOwner) {
        if (initialOwner == address(0)) {
            revert OwnableInvalidOwner(address(0));
        }
        _transferOwnership(initialOwner);
    }

    /**
     * @dev Throws if called by any account other than the owner.
     */
    modifier onlyOwner() {
        _checkOwner();
        _;
    }

    /**
     * @dev Returns the address of the current owner.
     */
    function owner() public view virtual returns (address) {
        return _owner;
    }

    /**
     * @dev Throws if the sender is not the owner.
     */
    function _checkOwner() internal view virtual {
        if (owner() != _msgSender()) {
            revert OwnableUnauthorizedAccount(_msgSender());
        }
    }

    /**
     * @dev Leaves the contract without owner. It will not be possible to call
     * `onlyOwner` functions. Can only be called by the current owner.
     *
     * NOTE: Renouncing ownership will leave the contract without an owner,
     * thereby disabling any functionality that is only available to the owner.
     */
    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Can only be called by the current owner.
     */
    function transferOwnership(address newOwner) public virtual onlyOwner {
        if (newOwner == address(0)) {
            revert OwnableInvalidOwner(address(0));
        }
        _transferOwnership(newOwner);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Internal function without access restriction.
     */
    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}

// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.1.0) (utils/ReentrancyGuard.sol)
/**
 * @dev Contract module that helps prevent reentrant calls to a function.
 *
 * Inheriting from `ReentrancyGuard` will make the {nonReentrant} modifier
 * available, which can be applied to functions to make sure there are no nested
 * (reentrant) calls to them.
 *
 * Note that because there is a single `nonReentrant` guard, functions marked as
 * `nonReentrant` may not call one another. This can be worked around by making
 * those functions `private`, and then adding `external` `nonReentrant` entry
 * points to them.
 *
 * TIP: If EIP-1153 (transient storage) is available on the chain you're deploying at,
 * consider using {ReentrancyGuardTransient} instead.
 *
 * TIP: If you would like to learn more about reentrancy and alternative ways
 * to protect against it, check out our blog post
 * https://blog.openzeppelin.com/reentrancy-after-istanbul/[Reentrancy After Istanbul].
 */
abstract contract ReentrancyGuard {
    // Booleans are more expensive than uint256 or any type that takes up a full
    // word because each write operation emits an extra SLOAD to first read the
    // slot's contents, replace the bits taken up by the boolean, and then write
    // back. This is the compiler's defense against contract upgrades and
    // pointer aliasing, and it cannot be disabled.

    // The values being non-zero value makes deployment a bit more expensive,
    // but in exchange the refund on every call to nonReentrant will be lower in
    // amount. Since refunds are capped to a percentage of the total
    // transaction's gas, it is best to keep them low in cases like this one, to
    // increase the likelihood of the full refund coming into effect.
    uint256 private constant NOT_ENTERED = 1;
    uint256 private constant ENTERED = 2;

    uint256 private _status;

    /**
     * @dev Unauthorized reentrant call.
     */
    error ReentrancyGuardReentrantCall();

    constructor() {
        _status = NOT_ENTERED;
    }

    /**
     * @dev Prevents a contract from calling itself, directly or indirectly.
     * Calling a `nonReentrant` function from another `nonReentrant`
     * function is not supported. It is possible to prevent this from happening
     * by making the `nonReentrant` function external, and making it call a
     * `private` function that does the actual work.
     */
    modifier nonReentrant() {
        _nonReentrantBefore();
        _;
        _nonReentrantAfter();
    }

    function _nonReentrantBefore() private {
        // On the first call to nonReentrant, _status will be NOT_ENTERED
        if (_status == ENTERED) {
            revert ReentrancyGuardReentrantCall();
        }

        // Any calls to nonReentrant after this point will fail
        _status = ENTERED;
    }

    function _nonReentrantAfter() private {
        // By storing the original value once again, a refund is triggered (see
        // https://eips.ethereum.org/EIPS/eip-2200)
        _status = NOT_ENTERED;
    }

    /**
     * @dev Returns true if the reentrancy guard is currently set to "entered", which indicates there is a
     * `nonReentrant` function in the call stack.
     */
    function _reentrancyGuardEntered() internal view returns (bool) {
        return _status == ENTERED;
    }
}

// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.3.0) (utils/Pausable.sol)
/**
 * @dev Contract module which allows children to implement an emergency stop
 * mechanism that can be triggered by an authorized account.
 *
 * This module is used through inheritance. It will make available the
 * modifiers `whenNotPaused` and `whenPaused`, which can be applied to
 * the functions of your contract. Note that they will not be pausable by
 * simply including this module, only once the modifiers are put in place.
 */
abstract contract Pausable is Context {
    bool private _paused;

    /**
     * @dev Emitted when the pause is triggered by `account`.
     */
    event Paused(address account);

    /**
     * @dev Emitted when the pause is lifted by `account`.
     */
    event Unpaused(address account);

    /**
     * @dev The operation failed because the contract is paused.
     */
    error EnforcedPause();

    /**
     * @dev The operation failed because the contract is not paused.
     */
    error ExpectedPause();

    /**
     * @dev Modifier to make a function callable only when the contract is not paused.
     *
     * Requirements:
     *
     * - The contract must not be paused.
     */
    modifier whenNotPaused() {
        _requireNotPaused();
        _;
    }

    /**
     * @dev Modifier to make a function callable only when the contract is paused.
     *
     * Requirements:
     *
     * - The contract must be paused.
     */
    modifier whenPaused() {
        _requirePaused();
        _;
    }

    /**
     * @dev Returns true if the contract is paused, and false otherwise.
     */
    function paused() public view virtual returns (bool) {
        return _paused;
    }

    /**
     * @dev Throws if the contract is paused.
     */
    function _requireNotPaused() internal view virtual {
        if (paused()) {
            revert EnforcedPause();
        }
    }

    /**
     * @dev Throws if the contract is not paused.
     */
    function _requirePaused() internal view virtual {
        if (!paused()) {
            revert ExpectedPause();
        }
    }

    /**
     * @dev Triggers stopped state.
     *
     * Requirements:
     *
     * - The contract must not be paused.
     */
    function _pause() internal virtual whenNotPaused {
        _paused = true;
        emit Paused(_msgSender());
    }

    /**
     * @dev Returns to normal state.
     *
     * Requirements:
     *
     * - The contract must be paused.
     */
    function _unpause() internal virtual whenPaused {
        _paused = false;
        emit Unpaused(_msgSender());
    }
}

// SPDX-License-Identifier: MIT
// ═══════════════════════════════════════════════════════════════════════════════
//
//   KairosMetaRouter — Smart Order Router with On-Chain Fee Capture
//   Owner: Kairos 777 Inc. — Mario Isaac
//   "In God We Trust"
//
//   Architecture:
//   - Sits between any user/external exchange and ALL target DEXes
//   - Captures a platform fee on EVERY swap regardless of which DEX executes it
//   - Supports any Uniswap V2-compatible router (PancakeSwap, SushiSwap, etc.)
//   - External exchanges (tradingprohup.com) route orders here → fee captured →
//     best DEX executes the swap
//
//   Fee tiers (configurable):
//   - Default:     30 bps (0.30%) — external integrators
//   - Partner:     20 bps (0.20%) — verified partner exchanges
//   - Internal:    15 bps (0.15%) — Kairos DeFi app users
//   - API Premium: 10 bps (0.10%) — high-volume API keys
//
//   Flow:
//   1. User approves tokenIn to MetaRouter
//   2. MetaRouter pulls tokenIn from user
//   3. Takes fee → sends to feeRecipient
//   4. Approves remaining to target DEX router
//   5. Calls target router swap function
//   6. Output tokens go directly to user
//
// ═══════════════════════════════════════════════════════════════════════════════
interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint256 amountIn, uint256 amountOutMin,
        address[] calldata path, address to, uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapExactTokensForTokensSupportingFeeOnTransferTokens(
        uint256 amountIn, uint256 amountOutMin,
        address[] calldata path, address to, uint256 deadline
    ) external;

    function swapExactETHForTokens(
        uint256 amountOutMin, address[] calldata path,
        address to, uint256 deadline
    ) external payable returns (uint256[] memory amounts);

    function swapExactETHForTokensSupportingFeeOnTransferTokens(
        uint256 amountOutMin, address[] calldata path,
        address to, uint256 deadline
    ) external payable;

    function swapExactTokensForETH(
        uint256 amountIn, uint256 amountOutMin,
        address[] calldata path, address to, uint256 deadline
    ) external returns (uint256[] memory amounts);

    function swapExactTokensForETHSupportingFeeOnTransferTokens(
        uint256 amountIn, uint256 amountOutMin,
        address[] calldata path, address to, uint256 deadline
    ) external;

    function getAmountsOut(uint256 amountIn, address[] calldata path)
        external view returns (uint256[] memory amounts);

    function WETH() external view returns (address);
}

contract KairosMetaRouter is Ownable, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // ── State ────────────────────────────────────────────────────────────────
    address public feeRecipient;
    uint256 public defaultFeeBps;          // Default fee in basis points (1 bp = 0.01%)
    uint256 public constant MAX_FEE_BPS = 100; // Max 1% fee (safety cap)
    uint256 public constant BPS_DENOMINATOR = 10000;

    // Whitelisted DEX routers (PancakeSwap, Uniswap, SushiSwap, KairosSwap, etc.)
    mapping(address => bool) public whitelistedRouters;

    // Partner fee tiers: partner address → custom fee bps (0 = use default)
    mapping(address => uint256) public partnerFeeBps;
    mapping(address => bool) public isPartner;

    // Statistics
    uint256 public totalSwaps;
    uint256 public totalFeesCollectedETH; // Running count of ETH/BNB fees
    mapping(address => uint256) public totalFeesCollectedToken; // Per-token fees

    // ── Events ───────────────────────────────────────────────────────────────
    event SwapExecuted(
        address indexed user,
        address indexed router,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 fee,
        uint256 amountOut,
        address indexed partner
    );
    event RouterWhitelisted(address indexed router, bool status);
    event PartnerRegistered(address indexed partner, uint256 feeBps);
    event FeeRecipientUpdated(address indexed newRecipient);
    event DefaultFeeUpdated(uint256 newFeeBps);
    event EmergencyWithdraw(address token, uint256 amount);

    // ── Constructor ──────────────────────────────────────────────────────────
    // NOTE: _initialOwner is explicit (not msg.sender) to support CREATE2
    //       deployment via Nick's Factory for universal same-address deploys.
    constructor(
        address _initialOwner,
        address _feeRecipient,
        uint256 _defaultFeeBps,
        address[] memory _initialRouters
    ) Ownable(_initialOwner) {
        require(_initialOwner != address(0), "KMR: zero owner");
        require(_feeRecipient != address(0), "KMR: zero fee recipient");
        require(_defaultFeeBps <= MAX_FEE_BPS, "KMR: fee too high");

        feeRecipient = _feeRecipient;
        defaultFeeBps = _defaultFeeBps;

        for (uint256 i = 0; i < _initialRouters.length; i++) {
            whitelistedRouters[_initialRouters[i]] = true;
            emit RouterWhitelisted(_initialRouters[i], true);
        }
    }

    receive() external payable {}

    // ═══════════════════════════════════════════════════════════════════════════
    //  SWAP — Token → Token (with fee capture)
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * @notice Swap tokens through any whitelisted DEX router with fee capture.
     * @param router       Target DEX router address (must be whitelisted)
     * @param amountIn     Amount of tokenIn to swap (including fee)
     * @param amountOutMin Minimum acceptable output after slippage
     * @param path         Swap path [tokenIn, ..., tokenOut]
     * @param deadline     Unix timestamp deadline
     * @param partner      Partner/referrer address (address(0) for default fee)
     */
    function swapExactTokensForTokens(
        address router,
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline,
        address partner
    ) external nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(whitelistedRouters[router], "KMR: router not whitelisted");
        require(path.length >= 2, "KMR: invalid path");
        require(amountIn > 0, "KMR: zero amount");

        address tokenIn = path[0];
        address tokenOut = path[path.length - 1];

        // 1. Pull tokens from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);

        // 2. Calculate and take fee
        uint256 fee = _calculateFee(amountIn, partner);
        uint256 swapAmount = amountIn - fee;

        if (fee > 0) {
            IERC20(tokenIn).safeTransfer(feeRecipient, fee);
            totalFeesCollectedToken[tokenIn] += fee;
        }

        // 3. Approve target router
        IERC20(tokenIn).forceApprove(router, swapAmount);

        // 4. Execute swap on target DEX — output goes directly to user
        uint256 balBefore = IERC20(tokenOut).balanceOf(msg.sender);

        IUniswapV2Router(router).swapExactTokensForTokensSupportingFeeOnTransferTokens(
            swapAmount, amountOutMin, path, msg.sender, deadline
        );

        amountOut = IERC20(tokenOut).balanceOf(msg.sender) - balBefore;

        // 5. Track
        totalSwaps++;
        emit SwapExecuted(msg.sender, router, tokenIn, tokenOut, amountIn, fee, amountOut, partner);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  SWAP — Native (BNB/ETH) → Token (with fee capture)
    // ═══════════════════════════════════════════════════════════════════════════

    function swapExactETHForTokens(
        address router,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline,
        address partner
    ) external payable nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(whitelistedRouters[router], "KMR: router not whitelisted");
        require(path.length >= 2, "KMR: invalid path");
        require(msg.value > 0, "KMR: zero value");

        address tokenOut = path[path.length - 1];

        // 1. Calculate and take fee in native currency
        uint256 fee = _calculateFee(msg.value, partner);
        uint256 swapAmount = msg.value - fee;

        if (fee > 0) {
            (bool sent, ) = feeRecipient.call{value: fee}("");
            require(sent, "KMR: fee transfer failed");
            totalFeesCollectedETH += fee;
        }

        // 2. Execute swap — output goes to user
        uint256 balBefore = IERC20(tokenOut).balanceOf(msg.sender);

        IUniswapV2Router(router).swapExactETHForTokensSupportingFeeOnTransferTokens{value: swapAmount}(
            amountOutMin, path, msg.sender, deadline
        );

        amountOut = IERC20(tokenOut).balanceOf(msg.sender) - balBefore;

        totalSwaps++;
        emit SwapExecuted(msg.sender, router, address(0), tokenOut, msg.value, fee, amountOut, partner);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  SWAP — Token → Native (BNB/ETH) (with fee capture)
    // ═══════════════════════════════════════════════════════════════════════════

    function swapExactTokensForETH(
        address router,
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        uint256 deadline,
        address partner
    ) external nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(whitelistedRouters[router], "KMR: router not whitelisted");
        require(path.length >= 2, "KMR: invalid path");
        require(amountIn > 0, "KMR: zero amount");

        address tokenIn = path[0];

        // 1. Pull tokens from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);

        // 2. Calculate and take fee on input token
        uint256 fee = _calculateFee(amountIn, partner);
        uint256 swapAmount = amountIn - fee;

        if (fee > 0) {
            IERC20(tokenIn).safeTransfer(feeRecipient, fee);
            totalFeesCollectedToken[tokenIn] += fee;
        }

        // 3. Approve target router
        IERC20(tokenIn).forceApprove(router, swapAmount);

        // 4. Execute swap — ETH output goes to THIS contract first
        uint256 ethBefore = address(this).balance;

        IUniswapV2Router(router).swapExactTokensForETHSupportingFeeOnTransferTokens(
            swapAmount, amountOutMin, path, address(this), deadline
        );

        amountOut = address(this).balance - ethBefore;

        // 5. Forward ETH to user
        (bool sent, ) = msg.sender.call{value: amountOut}("");
        require(sent, "KMR: ETH transfer failed");

        totalSwaps++;
        emit SwapExecuted(msg.sender, router, tokenIn, address(0), amountIn, fee, amountOut, address(0));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  MULTI-HOP: Best Route Swap (for aggregator)
    //  Allows swapping through multiple routers in sequence
    // ═══════════════════════════════════════════════════════════════════════════

    struct SwapStep {
        address router;       // Which DEX router to use for this step
        address[] path;       // Token path for this step [tokenA, tokenB]
        uint256 amountOutMin; // Min output for this step
    }

    /**
     * @notice Execute a multi-step swap route (e.g., Token1 → KairosSwap → WBNB → PancakeSwap → Token2)
     *         Fee is captured on the initial input only.
     */
    function swapMultiRoute(
        SwapStep[] calldata steps,
        uint256 amountIn,
        uint256 deadline,
        address partner
    ) external nonReentrant whenNotPaused returns (uint256 finalAmountOut) {
        require(steps.length > 0 && steps.length <= 5, "KMR: invalid steps");

        address tokenIn = steps[0].path[0];
        address tokenOut = steps[steps.length - 1].path[steps[steps.length - 1].path.length - 1];

        // 1. Pull initial tokens from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);

        // 2. Take fee on initial input
        uint256 fee = _calculateFee(amountIn, partner);
        uint256 currentAmount = amountIn - fee;

        if (fee > 0) {
            IERC20(tokenIn).safeTransfer(feeRecipient, fee);
            totalFeesCollectedToken[tokenIn] += fee;
        }

        // 3. Execute each step
        for (uint256 i = 0; i < steps.length; i++) {
            SwapStep calldata step = steps[i];
            require(whitelistedRouters[step.router], "KMR: router not whitelisted");

            address stepTokenIn = step.path[0];
            address stepTokenOut = step.path[step.path.length - 1];

            // Approve step router
            IERC20(stepTokenIn).forceApprove(step.router, currentAmount);

            // Execute step — output to this contract (except last step → user)
            address recipient = (i == steps.length - 1) ? msg.sender : address(this);
            uint256 balBefore = IERC20(stepTokenOut).balanceOf(recipient);

            IUniswapV2Router(step.router).swapExactTokensForTokensSupportingFeeOnTransferTokens(
                currentAmount, step.amountOutMin, step.path, recipient, deadline
            );

            currentAmount = IERC20(stepTokenOut).balanceOf(recipient) - balBefore;
        }

        finalAmountOut = currentAmount;
        totalSwaps++;
        emit SwapExecuted(msg.sender, steps[0].router, tokenIn, tokenOut, amountIn, fee, finalAmountOut, partner);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  VIEW: Quote with fee
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * @notice Get a quote that includes the Kairos platform fee deduction.
     * @return netAmountIn  Amount that actually goes to the DEX (after fee)
     * @return fee          Platform fee deducted
     * @return amountOut    Expected output from the DEX
     */
    function getQuoteWithFee(
        address router,
        uint256 amountIn,
        address[] calldata path,
        address partner
    ) external view returns (uint256 netAmountIn, uint256 fee, uint256 amountOut) {
        fee = _calculateFee(amountIn, partner);
        netAmountIn = amountIn - fee;

        uint256[] memory amounts = IUniswapV2Router(router).getAmountsOut(netAmountIn, path);
        amountOut = amounts[amounts.length - 1];
    }

    /**
     * @notice Compare quotes across multiple routers to find best execution.
     */
    function getBestQuote(
        address[] calldata routers,
        uint256 amountIn,
        address[] calldata path,
        address partner
    ) external view returns (
        address bestRouter,
        uint256 bestAmountOut,
        uint256 fee
    ) {
        fee = _calculateFee(amountIn, partner);
        uint256 netAmount = amountIn - fee;

        for (uint256 i = 0; i < routers.length; i++) {
            if (!whitelistedRouters[routers[i]]) continue;
            try IUniswapV2Router(routers[i]).getAmountsOut(netAmount, path) returns (uint256[] memory amounts) {
                uint256 out = amounts[amounts.length - 1];
                if (out > bestAmountOut) {
                    bestAmountOut = out;
                    bestRouter = routers[i];
                }
            } catch {
                // Router doesn't have liquidity for this pair — skip
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  ADMIN
    // ═══════════════════════════════════════════════════════════════════════════

    function setFeeRecipient(address _feeRecipient) external onlyOwner {
        require(_feeRecipient != address(0), "KMR: zero address");
        feeRecipient = _feeRecipient;
        emit FeeRecipientUpdated(_feeRecipient);
    }

    function setDefaultFee(uint256 _feeBps) external onlyOwner {
        require(_feeBps <= MAX_FEE_BPS, "KMR: fee too high");
        defaultFeeBps = _feeBps;
        emit DefaultFeeUpdated(_feeBps);
    }

    function setRouterWhitelist(address router, bool status) external onlyOwner {
        whitelistedRouters[router] = status;
        emit RouterWhitelisted(router, status);
    }

    function batchWhitelistRouters(address[] calldata routers, bool status) external onlyOwner {
        for (uint256 i = 0; i < routers.length; i++) {
            whitelistedRouters[routers[i]] = status;
            emit RouterWhitelisted(routers[i], status);
        }
    }

    function registerPartner(address partner, uint256 feeBps) external onlyOwner {
        require(feeBps <= MAX_FEE_BPS, "KMR: fee too high");
        isPartner[partner] = true;
        partnerFeeBps[partner] = feeBps;
        emit PartnerRegistered(partner, feeBps);
    }

    function removePartner(address partner) external onlyOwner {
        isPartner[partner] = false;
        partnerFeeBps[partner] = 0;
    }

    function pause() external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }

    /// @notice Emergency withdraw stuck tokens (safety)
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        if (token == address(0)) {
            (bool sent, ) = owner().call{value: amount}("");
            require(sent, "KMR: ETH withdraw failed");
        } else {
            IERC20(token).safeTransfer(owner(), amount);
        }
        emit EmergencyWithdraw(token, amount);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  INTERNAL
    // ═══════════════════════════════════════════════════════════════════════════

    function _calculateFee(uint256 amount, address partner) internal view returns (uint256) {
        uint256 feeBps = defaultFeeBps;

        // Partner-specific fee tier (can be lower than default)
        if (partner != address(0) && isPartner[partner]) {
            feeBps = partnerFeeBps[partner];
        }

        return (amount * feeBps) / BPS_DENOMINATOR;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  INFO
    // ═══════════════════════════════════════════════════════════════════════════

    function getStats() external view returns (
        uint256 swaps,
        uint256 ethFees,
        uint256 feeBps,
        address recipient
    ) {
        return (totalSwaps, totalFeesCollectedETH, defaultFeeBps, feeRecipient);
    }

    function getFeeBps(address partner) external view returns (uint256) {
        if (partner != address(0) && isPartner[partner]) {
            return partnerFeeBps[partner];
        }
        return defaultFeeBps;
    }
}