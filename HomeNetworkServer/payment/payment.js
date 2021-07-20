import Web3 from "web3";
import { ChildChain, OmgUtil } from "@omisego/omg-js";
import BigNumber from 'bn.js';
// import { orderBy } from 'lodash';
// import pkg from 'lodash';
// const { orderBy } = pkg;

const web3_provider_url = 'https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6';
const plasmaContractAddress = '0xb43f53394d86deab35bc2d8356d6522ced6429b5';  // CONTRACT_ADDRESS_PLASMA_FRAMEWORK RINKEBY
const watcherUrl = 'https://watcher-info.rinkeby.v1.omg.network';  // WATCHER_INFO_URL
const web3 = new Web3(new Web3.providers.HttpProvider(web3_provider_url));
// const rootChain = new RootChain({ web3, plasmaContractAddress });
const childChain = new ChildChain({ watcherUrl, plasmaContractAddress });

import Router from 'koa-router';

import Koa from "koa";
import bodyParser from "koa-bodyparser";
import cors from "@koa/cors";

const app = new Koa();
const router = new Router();

let todos = {
  0: {'title': 'build an API', 'order': 1, 'completed': false},
  1: {'title': '?????', 'order': 2, 'completed': false},
  2: {'title': 'profit!', 'order': 3, 'completed': false}
};
let nextId = 3;

router.get('/todos/', list)
  .del('/todos/', clear)
  .post('/todos/', add)
  .get('todo', '/todos/:id', show)
  .patch('/todos/:id', update)
  .del('/todos/:id', remove)
  .post('/payment/', payment);



  async function fetchFees() {
    try {
      const allFees = await childChain.getFees();
      return allFees['1'];
    } catch (error) {
      console.log("fees error")
    }
  } 

  async function payment(ctx) {
    // const id = ctx.params.id;
    const body = ctx.request.body;
    const receiverAdd = body['receiverAdd'];
    const amount = body['amount'];
    const metadata = body['metadata'];
    // const receiverAdd = '0x956015029B53403D6F39cf1A37Db555F03FD74dc';
    // const amount = 100;

    const address = '0x5E8138098a133B6424AEC09232674E253909B3Fb';
    // console.log(address)
    const senderPrivateKey = 'fee15b52a7e7824aa088f6e46990cf0527b708ab5ba0b0c36693d8a47ec8dcec';

    // const _utxos = await childChain.getUtxos(address);
    // const utxos = orderBy(_utxos, i => i.amount, 'desc');

    const allFees = await fetchFees();
    const feeInfo = allFees.find(i => i.currency === OmgUtil.transaction.ETH_CURRENCY);
    if (!feeInfo) {
      console.log("fee error")
    }
    // const feeInfo = 1;

    // var amount = 100

    const payments = [ {
      owner: receiverAdd,
      currency: OmgUtil.transaction.ETH_CURRENCY,
      amount: new BigNumber(amount.toString())
    } ];

    const fee = {
      currency: OmgUtil.transaction.ETH_CURRENCY
    };

    // const transactionBody = OmgUtil.transaction.createTransactionBody({
    //   fromAddress: address,
    //   fromUtxos: utxos,
    //   payments,
    //   fee,
    //   metadata: "eth transfer" || OmgUtil.transaction.NULL_METADATA,
    // });

    const transactionBody = await childChain.createTransaction({
      owner: address,
      payments: payments,
      fee: fee,
      metadata: metadata,
    });  

    // const typedData = OmgUtil.transaction.getTypedData(transactionBody, plasmaContractAddress);
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
  }











async function list(ctx) {
  ctx.body = Object.keys(todos).map(k => {
    todos[k].id = k;
    return todos[k];
  });
}

async function clear(ctx) {
  todos = {};
  ctx.status = 204;
}

async function add(ctx) {
  const todo = ctx.request.body;
  if (!todo.title) ctx.throw(400, {'error': '"title" is a required field'});
  const title = todo.title;
  if (!typeof data === 'string' || !title.length) ctx.throw(400, {'error': '"title" must be a string with at least one character'});

  todo['completed'] = todo['completed'] || false;
  todo['url'] = 'http://' + ctx.host + router.url('todo', nextId);
  todos[nextId++] = todo;

  ctx.status = 303;
  ctx.set('Location', todo['url']);
}

async function show(ctx) {
  const id = ctx.params.id;
  const todo = todos[id]
  if (!todo) ctx.throw(404, {'error': 'Todo not found'});
  todo.id = id;
  ctx.body = todo;
}

async function update(ctx) {
  const id = ctx.params.id;
  const todo = todos[id];

  Object.assign(todo, ctx.request.body);

  ctx.body = todo;
}

async function remove(ctx) {
  const id = ctx.params.id;
  if (!todos[id]) ctx.throw(404, {'error': 'Todo not found'});

  delete todos[id];

  ctx.status = 204;
}

app
  .use(bodyParser())
  .use(cors())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(3000);
