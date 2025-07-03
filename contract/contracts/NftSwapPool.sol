// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.5/contracts/token/ERC1155/IERC1155.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.5/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.5/contracts/access/Ownable.sol";
import "./UserInfo.sol";

interface IMyERC1155Burnable {
    function burn(address account, uint256 id, uint256 value) external;
    function getUserInfo(uint256 tokenId) external view returns (UserInfo memory);
}

contract NftSwapPool is ERC1155Holder, Ownable {
    IERC1155 public nftToken;
    IMyERC1155Burnable public burnableToken;

    uint256[] public aPoolTokenIds;
    uint256[] public bPoolTokenIds;
    mapping(uint256 => bool) public isInAPool;
    mapping(uint256 => bool) public isInBPool;

    event Deposited(address indexed user, uint256 tokenId, uint8 poolType);
    event Swapped(address indexed user, uint256 myTokenId, uint256 targetTokenId, uint8 poolType);
    event WithDraw(address indexed user, uint256 targetTokenId, uint8 poolType);

    constructor(address _nftToken) {
        nftToken = IERC1155(_nftToken);
        burnableToken = IMyERC1155Burnable(_nftToken);
    }

    function swap(uint8 poolType, uint256 myTokenId, uint256 targetTokenId) external returns (UserInfo memory) {
        require(poolType == 0 || poolType == 1, "Invalid pool type");

        deposit(poolType, myTokenId);

        if (targetTokenId != 0) {
            withdrawal(poolType, targetTokenId);
        }

        emit Swapped(msg.sender, myTokenId, targetTokenId, poolType);
        return burnableToken.getUserInfo(targetTokenId);
    }

    function getAPoolTokenIds() external view returns (uint256[] memory) {
        return aPoolTokenIds;
    }

    function getBPoolTokenIds() external view returns (uint256[] memory) {
        return bPoolTokenIds;
    }

    function deposit(uint8 poolType, uint256 tokenId) internal {
        uint256 userBalance = nftToken.balanceOf(msg.sender, tokenId);
        nftToken.safeTransferFrom(msg.sender, address(this), tokenId, userBalance, "");

        if (poolType == 0) {
            aPoolTokenIds.push(tokenId);
            isInAPool[tokenId] = true;
        } else {
            bPoolTokenIds.push(tokenId);
            isInBPool[tokenId] = true;
        }

        emit Deposited(msg.sender, tokenId, poolType);
    }

    function withdrawal(uint8 poolType, uint256 targetTokenId) internal {
        if (poolType == 0) {
            require(isInBPool[targetTokenId], "Target B token not in pool");
        } else {
            require(isInAPool[targetTokenId], "Target A token not in pool");
        }

        burnableToken.burn(address(this), targetTokenId, 1);
        uint256 userBalance = nftToken.balanceOf(address(this), targetTokenId);

        if (userBalance == 0) {
            if (poolType == 0) {
                isInBPool[targetTokenId] = false;
                _removeFromArray(bPoolTokenIds, targetTokenId);
            } else {
                isInAPool[targetTokenId] = false;
                _removeFromArray(aPoolTokenIds, targetTokenId);
            }
        }

        emit WithDraw(msg.sender, targetTokenId, poolType);
    }

    function _removeFromArray(uint256[] storage array, uint256 tokenId) internal {
        uint256 len = array.length;
        for (uint256 i = 0; i < len; i++) {
            if (array[i] == tokenId) {
                array[i] = array[len - 1];
                array.pop();
                break;
            }
        }
    }
}
