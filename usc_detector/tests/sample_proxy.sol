// SPDX-License-Identifier: MIT
// Minimal EIP-1967 style proxy for testing USC detector

pragma solidity ^0.8.0;

contract ERC1967Proxy {
    bytes32 internal constant _IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    function _delegate(address implementation) internal virtual {
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), implementation, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }

    function _implementation() internal view virtual returns (address) {
        return _getImplementation();
    }

    function _getImplementation() internal view returns (address) {
        address impl;
        assembly {
            impl := sload(_IMPLEMENTATION_SLOT)
        }
        return impl;
    }

    fallback() external payable virtual {
        _delegate(_implementation());
    }

    receive() external payable virtual {
        _delegate(_implementation());
    }
}
