import Web3 from "web3";
import { ChildChain, OmgUtil } from "@omisego/omg-js";
import BigNumber from 'bn.js';

const web3_provider_url = 'https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6';
const plasmaContractAddress = '0xb43f53394d86deab35bc2d8356d6522ced6429b5';  // CONTRACT_ADDRESS_PLASMA_FRAMEWORK RINKEBY
const watcherUrl = 'https://watcher-info.rinkeby.v1.omg.network';  // WATCHER_INFO_URL
const web3 = new Web3(new Web3.providers.HttpProvider(web3_provider_url));
const childChain = new ChildChain({ watcherUrl, plasmaContractAddress });

import Router from 'koa-router';

import Koa from "koa";
import bodyParser from "koa-bodyparser";
import cors from "@koa/cors";

import abi from "ethereumjs-abi";
import util from 'ethereumjs-util'
import EthereumTx from "ethereumjs-tx"

const app = new Koa();
const router = new Router();

const address = '0x5E8138098a133B6424AEC09232674E253909B3Fb';
const senderPrivateKey = 'fee15b52a7e7824aa088f6e46990cf0527b708ab5ba0b0c36693d8a47ec8dcec';

const account = await web3.eth.accounts.privateKeyToAccount(senderPrivateKey);
await web3.eth.accounts.wallet.add(account);

const contract_abi = '[{"inputs":[{"internalType":"address payable","name":"_recipient","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"constant":false,"inputs":[],"name":"claimTimeout","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"close","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"expiration","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"newExpiration","type":"uint256"}],"name":"extend","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"isValidSignature","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"recipient","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"sender","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'
const bytecode = "0x60806040526040516108213803806108218339818101604052604081101561002657600080fd5b810190808051906020019092919080519060200190929190505050336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555081600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055508042016002819055505050610745806100dc6000396000f3fe608060405234801561001057600080fd5b506004361061007d5760003560e01c806366d003ac1161005b57806366d003ac1461016f57806367e404ce146101b95780639714378c14610203578063b2af9362146102315761007d565b80630e1da6c314610082578063415ffba71461008c5780634665096d14610151575b600080fd5b61008a61030e565b005b61014f600480360360408110156100a257600080fd5b8101908080359060200190929190803590602001906401000000008111156100c957600080fd5b8201836020820111156100db57600080fd5b803590602001918460018302840111640100000000831117156100fd57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610357565b005b610159610467565b6040518082815260200191505060405180910390f35b61017761046d565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6101c1610493565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61022f6004803603602081101561021957600080fd5b81019080803590602001909291905050506104b8565b005b6102f46004803603604081101561024757600080fd5b81019080803590602001909291908035906020019064010000000081111561026e57600080fd5b82018360208201111561028057600080fd5b803590602001918460018302840111640100000000831117156102a257600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610529565b604051808215151515815260200191505060405180910390f35b60025442101561031d57600080fd5b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16146103b157600080fd5b6103bb8282610529565b6103c457600080fd5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc839081150290604051600060405180830381858888f1935050505015801561042c573d6000803e3d6000fd5b506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b60025481565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461051157600080fd5b600254811161051f57600080fd5b8060028190555050565b6000806105923085604051602001808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660601b815260140182815260200192505050604051602081830303815290604052805190602001206105f6565b90506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166105d6828561064e565b73ffffffffffffffffffffffffffffffffffffffff161491505092915050565b60008160405160200180807f19457468657265756d205369676e6564204d6573736167653a0a333200000000815250601c01828152602001915050604051602081830303815290604052805190602001209050919050565b60008060008061065d856106d5565b92509250925060018684848460405160008152602001604052604051808581526020018460ff1660ff1681526020018381526020018281526020019450505050506020604051602081039080840390855afa1580156106c0573d6000803e3d6000fd5b50505060206040510351935050505092915050565b600080600060418451146106e857600080fd5b6020840151915060408401519050606084015160001a9250828282925092509250919390925056fea265627a7a72315820b76f0f1cee859ce5547cf4dc1552adf93171ccfe07e152a85efabc97ed5c0f6064736f6c63430005110032"

router
  .post('/payment/', payment)
  .post('/signPayment/', signPayment)
  .get('/isValidSignature/', isValidSignature)
  .post('/deploy/', deploy);


async function fetchFees() {
  try {
    const allFees = await childChain.getFees();
    return allFees['1'];
  } catch (error) {
    console.log("fees error")
  }
} 

async function payment(ctx) {
  const body = ctx.request.body;
  const receiverAdd = body['receiverAdd'];
  const amount = body['amount'];
  const metadata = body['metadata'];

  try {

    const allFees = await fetchFees();
    const feeInfo = allFees.find(i => i.currency === OmgUtil.transaction.ETH_CURRENCY);
    if (!feeInfo) {
      console.log("fee error")
    }

    const payments = [ {
      owner: receiverAdd,
      currency: OmgUtil.transaction.ETH_CURRENCY,
      amount: new BigNumber(amount.toString())
    } ];

    const fee = {
      currency: OmgUtil.transaction.ETH_CURRENCY
    };

    const transactionBody = await childChain.createTransaction({
      owner: address,
      payments: payments,
      fee: fee,
      metadata: metadata,
    });  

    const typedData = OmgUtil.transaction.getTypedData(
      transactionBody.transactions[0], plasmaContractAddress);

    const privateKeys = new Array(
      transactionBody.transactions[0].inputs.length
    ).fill(senderPrivateKey); 

    const signatures = childChain.signTransaction(typedData, privateKeys);  

    const signedTypedData = childChain.buildSignedTransaction(typedData, signatures);  
    const receipt = await childChain.submitTransaction(signedTypedData);
    console.log('Transaction submitted: ', receipt.txhash)

    
    ctx.body = receipt.txhash;

  } catch (error) {
    ctx.body = "error4 : too early for another payment";
  }

}


async function constructPaymentMessage(contractAddress, amount) {
  return abi.soliditySHA3(
      ["address", "uint256"],
      [contractAddress, amount]
  );
}

async function signMessage(message){
  const data = await web3.eth.sign(
    "0x" + message.toString("hex"),
    address
  );
  // console.log('data :', data);
  var publicKey = web3.eth.accounts.recover("0x" + message.toString("hex"), data);
  // console.log('publicKey :', publicKey);
  return data
}


// curl -X POST -d '{"contractAddress":"contractAddress", "amount":"amount"}' http://163.172.130.246:3000/signPayment/
// contractAddress is used to prevent cross-contract replay attacks.
// amount, in wei, specifies how much Ether should be sent.
async function signPayment(ctx) {
  const body = ctx.request.body;
  const contractAddress = body['contractAddress'];
  const amount = body['amount'];
  var message = await constructPaymentMessage(contractAddress, amount);
  var signature = await signMessage(message);
  // console.log('signature :', signature);
  ctx.body = signature;
}




// this mimics the prefixing behavior of the eth_sign JSON-RPC method.
async function prefixed(hash) {
  return abi.soliditySHA3(
      ["string", "bytes32"],
      ["\x19Ethereum Signed Message:\n32", hash]
  );
}

async function recoverSigner(message, signature) {
  var add_of_signature = web3.eth.accounts.recover("0x" + message.toString("hex"), signature);
  console.log('add_of_signature :', add_of_signature);
  return add_of_signature;
}

async function isValidSignature(ctx) {
  const contractAddress = '0xFFC869826E724845a65F710D3Ffa8691f274b3Ba';
  const amount = 100;
  var signature = '0xf0ea2702ea910b3ddf9c94300e484816c48993b7adb78e9003e27eb1dd8febcb3c7175af47a3397e80a626c67d3f44aceeeececa704e117def93972863cbcda91c';
  const expectedSigner = address;
  var message = await constructPaymentMessage(contractAddress, amount);
  var signer = await recoverSigner(message, signature);
  console.log(signer.toLowerCase() == expectedSigner.toLowerCase());
}


async function deploy(ctx) {
  const body = ctx.request.body;
  const receiverAdd = body['receiverAdd'];
  const amount = body['amount'];
  const duration = body['duration'];
  
  let gasPrice = web3.eth.gasPrice;

  const contractAbi = new web3.eth.Contract(JSON.parse(contract_abi));
  
  const transaction = contractAbi.deploy({
    data: bytecode,
    arguments: [receiverAdd, duration],
  });

  const createTransaction = await web3.eth.accounts.signTransaction(
    {
       from: address,
       data: transaction.encodeABI(),
       gas: 6000000,
       gasPrice: gasPrice,
       value: amount
    },
    senderPrivateKey
  );

  const createReceipt = await web3.eth.sendSignedTransaction(
    createTransaction.rawTransaction
  );
  console.log('Contract deployed at address :', createReceipt.contractAddress);

  ctx.body = createReceipt.contractAddress;
}


app
  .use(bodyParser())
  .use(cors())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(3000);
