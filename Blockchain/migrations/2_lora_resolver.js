const LoraResolver = artifacts.require("LoraResolver");

module.exports = function(deployer) {
  deployer.deploy(LoraResolver);
};