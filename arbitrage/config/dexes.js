// config/dexes.js
import { ethers } from "../ethers.min.js"; // TAPI: karena ethers dari CDN, kita pakai global

// Gunakan global `ethers` (karena load via CDN)
const ABI = ["function getAmountsOut(uint amountIn, address[] path) view returns (uint[] amounts)"];
const provider = new ethers.providers.JsonRpcProvider("https://polygon-rpc.com");

export const DEXES = {
  QuickSwap: new ethers.Contract("0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff", ABI, provider),
  SushiSwap: new ethers.Contract("0x1b02da8cb0d097eb8d57a175b88c7d8b47997506", ABI, provider),
  MeshSwap:  new ethers.Contract("0x10f4A785F458Bc144e3706575924889954946639", ABI, provider),
  DFYN:      new ethers.Contract("0xA10207D102261e3Cf151C40124C79C929C2a0181", ABI, provider)
};
