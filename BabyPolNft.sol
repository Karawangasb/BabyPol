// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";

contract BabyPolNFT is ERC721URIStorage, Ownable, IERC2981 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    string private _contractURI;
    string public projectWebsite = "https://www.babypol.fun/";

    // Royalty info
    address private _royaltyReceiver;
    uint96 private _royaltyFeeBasisPoints = 500; // 5%

    event ContractURISet(string contractURI);
    event RoyaltyInfoSet(address receiver, uint96 feeBasisPoints);
    event ProjectWebsiteSet(string website);
    event Minted(address indexed to, uint256 indexed tokenId, string uri);

    constructor(
        string memory name_,
        string memory symbol_,
        string memory contractURI_
    ) ERC721(name_, symbol_) {
        _contractURI = contractURI_;
        _tokenIdCounter.increment();
        _royaltyReceiver = msg.sender;
    }

    function safeMint(address to, string calldata uri) external onlyOwner returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        emit Minted(to, tokenId, uri);
        return tokenId;
    }

    function safeMintToSelf(string calldata uri) external onlyOwner returns (uint256) {
        return this.safeMint(msg.sender, uri);
    }

    function contractURI() external view returns (string memory) {
        return _contractURI;
    }

    function setContractURI(string calldata newContractURI) external onlyOwner {
        _contractURI = newContractURI;
        emit ContractURISet(newContractURI);
    }

    function setProjectWebsite(string calldata newWebsite) external onlyOwner {
        projectWebsite = newWebsite;
        emit ProjectWebsiteSet(newWebsite);
    }

    // Royalty (EIP-2981)
    function royaltyInfo(uint256, uint256 salePrice) external view override returns (address receiver, uint256 royaltyAmount) {
        receiver = _royaltyReceiver;
        royaltyAmount = (salePrice * _royaltyFeeBasisPoints) / 10000;
    }

    function setRoyaltyInfo(address receiver, uint96 feeBasisPoints) external onlyOwner {
        require(feeBasisPoints <= 1000, "Fee too high (max 10%)");
        _royaltyReceiver = receiver;
        _royaltyFeeBasisPoints = feeBasisPoints;
        emit RoyaltyInfoSet(receiver, feeBasisPoints);
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, IERC165) returns (bool) {
        return interfaceId == type(IERC2981).interfaceId || super.supportsInterface(interfaceId);
    }
}
