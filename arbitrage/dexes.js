// dexes.js
const DEXES = {
  QuickSwap: "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
  SushiSwap: "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",
  MeshSwap:  "0x10f4A785F458Bc144e3706575924889954946639",
  DFYN:      "0xA10207D102261e3Cf151C40124C79C929C2a0181"
};

const ABI = ["function getAmountsOut(uint amountIn, address[] path) view returns (uint[] amounts)"];
const provider = new ethers.providers.JsonRpcProvider("https://polygon-rpc.com");

const dexContracts = {};
for (const [name, addr] of Object.entries(DEXES)) {
  dexContracts[name] = new ethers.Contract(addr, ABI, provider);
}

export { dexContracts, provider };