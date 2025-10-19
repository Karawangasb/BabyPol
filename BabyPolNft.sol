// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
  BabyPolNFT
  - ERC-721 NFT contract compatible with OpenSea metadata conventions
  - Owner (deployer) can mint via safeMint(address to, string uri)
  - Supports setting baseURI and contractURI (for OpenSea collection metadata)
  - Implements EIP-2981 Royalty Standard (default 5%)
  - Uses OpenZeppelin Contracts
  - No burn function to ensure immutability
  - Includes public project website: https://www.babypol.fun/
*/

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";

contract BabyPolNFT is ERC721, Ownable, IERC2981 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    string private _baseTokenURI;
    string private _contractURI;

    // Project info
    string public projectWebsite = "https://www.babypol.fun/";

    // Royalty info
    address private _royaltyReceiver;
    uint96 private _royaltyFeeBasisPoints = 500; // 5% default (500 basis points)

    mapping(uint256 => string) private _tokenURIs;

    event BaseURISet(string baseURI);
    event ContractURISet(string contractURI);
    event RoyaltyInfoSet(address receiver, uint96 feeBasisPoints);
    event ProjectWebsiteSet(string website);
    event Minted(address indexed to, uint256 indexed tokenId, string uri);

    constructor(
        string memory name_,
        string memory symbol_,
        string memory baseURI_,
        string memory contractURI_
    ) ERC721(name_, symbol_) {
        _baseTokenURI = baseURI_;
        _contractURI = contractURI_;
        _tokenIdCounter.increment();
        _royaltyReceiver = msg.sender;
    }

    function safeMint(address to, string calldata uri) external onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _safeMint(to, tokenId);
        if (bytes(uri).length > 0) {
            _tokenURIs[tokenId] = uri;
        }
        emit Minted(to, tokenId, uri);
        return tokenId;
    }

    function safeMintToSelf(string calldata uri) external onlyOwner returns (uint256) {
        return this.safeMint(_msgSender(), uri);
    }

    function tokenURI(uint256 tokenId) public view virtual override returns (string memory) {
        require(_exists(tokenId), "ERC721: URI query for nonexistent token");

        string memory _tokenURI = _tokenURIs[tokenId];
        string memory base = _baseTokenURI;

        if (bytes(_tokenURI).length > 0) {
            return _tokenURI;
        }

        if (bytes(base).length == 0) {
            return "";
        }

        return string(abi.encodePacked(base, _toString(tokenId)));
    }

    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }

    function setBaseURI(string calldata newBaseURI) external onlyOwner {
        _baseTokenURI = newBaseURI;
        emit BaseURISet(newBaseURI);
    }

    function setContractURI(string calldata newContractURI) external onlyOwner {
        _contractURI = newContractURI;
        emit ContractURISet(newContractURI);
    }

    function contractURI() external view returns (string memory) {
        return _contractURI;
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return _baseTokenURI;
    }

    // --- Project Info ---
    function setProjectWebsite(string calldata newWebsite) external onlyOwner {
        projectWebsite = newWebsite;
        emit ProjectWebsiteSet(newWebsite);
    }

    // --- Royalty (EIP-2981) ---
    function royaltyInfo(
        uint256,
        uint256 salePrice
    ) external view override returns (address receiver, uint256 royaltyAmount) {
        receiver = _royaltyReceiver;
        royaltyAmount = (salePrice * _royaltyFeeBasisPoints) / 10000;
    }

    function setRoyaltyInfo(address receiver, uint96 feeBasisPoints) external onlyOwner {
        require(feeBasisPoints <= 1000, "Fee too high (max 10%)");
        _royaltyReceiver = receiver;
        _royaltyFeeBasisPoints = feeBasisPoints;
        emit RoyaltyInfoSet(receiver, feeBasisPoints);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        virtual
        override(ERC721, IERC165)
        returns (bool)
    {
        return interfaceId == type(IERC2981).interfaceId || super.supportsInterface(interfaceId);
    }
}
