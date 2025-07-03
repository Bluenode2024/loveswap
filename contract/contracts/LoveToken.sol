// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.5/contracts/token/ERC1155/ERC1155.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.5/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.5/contracts/access/Ownable.sol";

import "./UserInfo.sol";

contract LoveToken is ERC1155, ERC1155Burnable, Ownable {
    uint256 public currentTokenId = 0;

    mapping(uint256 => UserInfo) private userInfo;

    constructor(string memory uri_) ERC1155(uri_) {
        _mint(msg.sender, 0, 1, "");
           userInfo[0] = UserInfo(
            "vitalik.eth.official",
            "Ethereum Guy",
            0,
            0,
            0,
            0,
            0,
            0,
            0
        );
    }

    function mint(
        address to,
        string memory instagramId,
        string memory major,
        uint8 majorType,
        uint8 mbtiIeType,
        uint8 mbtiNtsfType,
        uint8 mbtiPjType,
        uint8 appearanceType,
        uint8 hobby,
        uint8 debateStance,
        uint8 amount
    ) external onlyOwner returns (uint256) {
        uint256 tokenId = ++currentTokenId;
        _mint(to, tokenId, amount, "");
        userInfo[tokenId] = UserInfo(
            instagramId,
            major,
            majorType,
            mbtiIeType,
            mbtiNtsfType,
            mbtiPjType,
            appearanceType,
            hobby,
            debateStance
        );
        return tokenId;
    }

    function getUserInfo(uint256 tokenId) external view returns (UserInfo memory) {
        return userInfo[tokenId];
    }
}
