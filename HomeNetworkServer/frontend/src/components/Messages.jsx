import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Row, Col } from 'react-bootstrap';
import { ethers } from 'ethers'

import Web3 from "web3";
// import '@metamask/legacy-web3';
import { ChildChain, RootChain, OmgUtil } from "@omisego/omg-js";
import BigNumber from 'bn.js';
// import JSONBigNumber from 'omg-json-bigint';
// import { bufferToHex } from 'ethereumjs-util';
import { orderBy } from 'lodash';
// import { WebWalletError } from 'services/errorService';

const web3_provider_url = 'https://rinkeby.infura.io/v3/4d24fe93ef67480f97be53ccad7e43d6';
const plasmaContractAddress = '0xb43f53394d86deab35bc2d8356d6522ced6429b5';  // CONTRACT_ADDRESS_PLASMA_FRAMEWORK RINKEBY
const watcherUrl = 'https://watcher-info.rinkeby.v1.omg.network';  // WATCHER_INFO_URL
// const watcherUrl = 'https://watcher.rinkeby.v1.omg.network';  // WATCHER_URL
const web3 = new Web3(new Web3.providers.HttpProvider(web3_provider_url));
const rootChain = new RootChain({ web3, plasmaContractAddress });
const childChain = new ChildChain({ watcherUrl, plasmaContractAddress });
// const childChain = new ChildChain({
//   watcherUrl: watcherInfoUrl,
//   watcherProxyUrl: '',
//   plasmaContractAddress: plasmaContractAddress
// });

const erc20ContractAddress = "0xd92e713d051c37ebb2561803a3b5fbabc4962431";
const aliceAddress = "0x8cb0de6206f459812525f2ba043b14155c2230c0";



class Messages extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      messages: [],
      showHide : false,
      add: [],
      total: 0,
      pay: {},
      address: ""
    };

    this.componentDidMount = this.componentDidMount.bind(this);
  }

  handleModalShowHide() {
    this.setState({ showHide: !this.state.showHide })
  }

  closeAndReload(){
    this.setState({ showHide: !this.state.showHide })

    this.componentDidMount()
  }

  deleteClick = value => () => {
    console.log(value);

    const items = this.state.messages.filter(item => item._id !== value);
    this.setState({ messages: items });

    const url = 'http://163.172.130.246:8080/msg/' + value;
    axios.delete(url).then(response => response.data)
    .then((data) => {

     })
    .catch(function (error) {
      console.log(error);
    });

    //this.componentDidMount()
  };

  async payM(){
    const data = this.state.pay;
    console.log(data)
    // iterate on the data key in order to pay each address
    for (const key in data){
      if (key !== "total"){
        console.log(key)
        console.log(data[key])
        // make a payment of n * price
        const priceWei = 100
        const amount = priceWei * data[key]
        const trans = await this.transfer(key, amount);
        if (trans === "success"){
          // send to the server that has payed for this owner and device
          const url = 'http://163.172.130.246:8080/pay/' + this.state.address + '/' + key;
          axios.patch(url, {"payed": true}).then(response => response.data)
          .then((data) => {
            console.log("payed !");
            this.componentDidMount()
          })
          .catch(function (error) {
            console.log(error);
          });

        }

      }
    }
    // this.componentDidMount()
  }


  // componentDidMount() {
  //   const url = 'http://163.172.130.246:8080/msg';
  //   axios.get(url).then(response => response.data)
  //   .then((data) => {
  //     this.setState({ messages: data })
  //     // console.log(this.state.messages)
  //    })
  //   .catch(function (error) {
  //     console.log(error);
  //   });
  // }

  async componentDidMount() {
    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
      await window.ethereum.request({ method: 'eth_requestAccounts' });
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const signer = provider.getSigner();
      const address = await signer.getAddress();
      this.setState({address: address});
      // console.log(address);

      const url = 'http://163.172.130.246:8080/msgs/' + address;
      axios.get(url).then(response => response.data)
      .then((data) => {
        this.setState({ messages: data })
        // console.log(this.state.messages)

        const url = 'http://163.172.130.246:8080/pay/' + address;
        axios.get(url).then(response => response.data)
        .then((data) => {
          // console.log(data)
          this.setState({pay: data});
          const total = data["total"]
          // console.log(total)
          this.setState({total: total});
        })
        .catch(function (error) {
          console.log(error);
        });


      })
      .catch(function (error) {
        console.log(error);
      });

    }
  }


  async retrieveChildChainBalance() {

    await window.ethereum.request({ method: 'eth_requestAccounts' });
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const signer = provider.getSigner();
    const address = await signer.getAddress();


  
    const childchainBalanceArray = await childChain.getBalance(address);
    
    const childchainBalance = childchainBalanceArray.map((i) => {
      return {
        currency:
          i.currency === OmgUtil.transaction.ETH_CURRENCY ? "ETH" : i.currency,
        amount:
          i.currency === OmgUtil.transaction.ETH_CURRENCY ?
            web3.utils.fromWei(String(i.amount), "ether") :
            web3.utils.toBN(i.amount).toString()
      };
    });
    console.log(childchainBalance)
    const amount = childchainBalance[0]['amount']
    console.log(amount)
    const wei = web3.utils.toWei(amount, "ether")
    console.log(wei)
    return childchainBalance;
  }

  async retrieveOMGBalance(address) {
    const childchainBalanceArray = await childChain.getBalance(address);
    
    const childchainBalance = childchainBalanceArray.map((i) => {
      return {
        currency:
          i.currency === OmgUtil.transaction.ETH_CURRENCY ? "ETH" : i.currency,
        amount:
          i.currency === OmgUtil.transaction.ETH_CURRENCY ?
            web3.utils.fromWei(String(i.amount), "ether") :
            web3.utils.toBN(i.amount).toString()
      };
    });
    // console.log(childchainBalance)
    const amount = childchainBalance[0]['amount']
    // console.log(amount)
    const wei = web3.utils.toWei(amount, "ether")
    // console.log(wei)
    return wei;
  }

  async retrieveRootChainErc20Balance() {
  
    const rootchainBalance = await web3.eth.getBalance(aliceAddress);
    const rootchainBalances = [
      {
        currency: "ETH",
        amount: web3.utils.fromWei(String(rootchainBalance), "ether"),
      },
    ];  
    const rootchainERC20Balance = await OmgUtil.getErc20Balance({
      web3,
      address: aliceAddress,
      erc20Address: erc20ContractAddress,
    });
    rootchainBalances.push({
      currency: erc20ContractAddress,
      amount: web3.utils.toBN(rootchainERC20Balance).toString(),
    });
    console.log(rootchainBalances)
  }


  // normalize signing methods across wallet providers
  async signTypedData (typedData, signer) {

    // console.log(typedData)

    // const domain = {
    //   name: 'OMG Network',
    //   version: '1',
    //   verifyingContract: '',
    //   // verifyingContract: plasmaContractAddress,
    //   salt: '0xfad5c7f626d80f9256ef01929f3beb96e058b8b4b0e3fe52d84f054c0e2a7a83'
    // };


    const types = {
      // EIP712Domain: [
      //     { name: 'name', type: 'string' },
      //     { name: 'version', type: 'string' },
      //     { name: 'verifyingContract', type: 'address' },
      //     { name: 'salt', type: 'bytes32' }
      // ],
      Transaction: [
          { name: 'txType', type: 'uint256' },
          { name: 'input0', type: 'Input' },
          { name: 'input1', type: 'Input' },
          { name: 'input2', type: 'Input' },
          { name: 'input3', type: 'Input' },
          { name: 'output0', type: 'Output' },
          { name: 'output1', type: 'Output' },
          { name: 'output2', type: 'Output' },
          { name: 'output3', type: 'Output' },
          { name: 'txData', type: 'uint256' },
          { name: 'metadata', type: 'bytes32' }
      ],
      Input: [
          { name: 'blknum', type: 'uint256' },
          { name: 'txindex', type: 'uint256' },
          { name: 'oindex', type: 'uint256' }
      ],
      Output: [
          { name: 'outputType', type: 'uint256' },
          { name: 'outputGuard', type: 'bytes20' },
          { name: 'currency', type: 'address' },
          { name: 'amount', type: 'uint256' }
      ]
    };

    const signature = await signer._signTypedData(typedData.domain, types, typedData.message);
    // console.log(signature);
    return signature;
  }

  async fetchFees () {
    try {
      const allFees = await childChain.getFees();
      return allFees['1'];
    } catch (error) {
      console.log("fees error")
    }
  }


  async transfer(receiverAdd, value) {
    // const receiverAdd = '0x956015029B53403D6F39cf1A37Db555F03FD74dc';

    await window.ethereum.request({ method: 'eth_requestAccounts' });
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const signer = provider.getSigner();
    const address = await signer.getAddress();
    // console.log(address)

    const _utxos = await childChain.getUtxos(address);
    const utxos = orderBy(_utxos, i => i.amount, 'desc');

    const allFees = await this.fetchFees();
    const feeInfo = allFees.find(i => i.currency === OmgUtil.transaction.ETH_CURRENCY);
    if (!feeInfo) {
      console.log("fee error")
    }
    // const feeInfo = 1;

    // var value = 100

    const payments = [ {
      owner: receiverAdd,
      currency: OmgUtil.transaction.ETH_CURRENCY,
      amount: new BigNumber(value.toString())
    } ];

    const fee = {
      currency: OmgUtil.transaction.ETH_CURRENCY,
      amount: new BigNumber(feeInfo.amount.toString())
    };

    const transactionBody = OmgUtil.transaction.createTransactionBody({
      fromAddress: address,
      fromUtxos: utxos,
      payments,
      fee,
      metadata: "eth transfer" || OmgUtil.transaction.NULL_METADATA,
    });

    const typedData = OmgUtil.transaction.getTypedData(transactionBody, plasmaContractAddress);

    const signature = await this.signTypedData(typedData, signer);
    const signatures = new Array(transactionBody.inputs.length).fill(signature);

    const signedTypedData = childChain.buildSignedTransaction(typedData, signatures);  
    const receipt = await childChain.submitTransaction(signedTypedData);
    console.log('Transaction submitted: ', receipt.txhash)

    // wait for transaction to be recorded by the watcher
    console.log("Waiting for transaction to be recorded by the Watcher...");
    // while amount in receiving account != expected amount
    const receiverBalance = await this.retrieveOMGBalance(receiverAdd);
    // console.log(receiverBalance)
    const expectedAmount = parseInt(receiverBalance) + value;
    // console.log(expectedAmount)

    var intermediateBalance = await this.retrieveOMGBalance(receiverAdd);
    while (parseInt(intermediateBalance) !== expectedAmount){
      await new Promise(r => setTimeout(r, 2000));
      intermediateBalance = await this.retrieveOMGBalance(receiverAdd);
    }

    console.log("received")
    return "success";

  }

  
  render() {
    return (
      <div className="container">
        <div className="col-xs-8">
          <div className="header">
            <h1>Messages</h1>
            <div>
              {(() => {
                if (this.state.total > 1) {
                  return (
                    <div className="d-flex align-items-center">
                    <p className="p_pay">{this.state.total} messages to pay for</p>
                    <Button className="pay_button" variant="success" onClick={() => this.payM()}>Pay</Button>
                    </div>
                  )
                } else if (this.state.total > 0) {
                  return (
                    <div className="d-flex align-items-center">
                    <p className="p_pay">{this.state.total} message to pay for</p>
                    <Button className="pay_button" variant="success" onClick={() => this.payM()}>Pay</Button>
                    </div>
                  )
                } else {
                  return (
                    <p className="p_pay2">{this.state.total} message to pay for</p>
                  )
                }
              })()}
            </div>
            {/* <Button variant="secondary" onClick={() => this.transfer()}>Transfer</Button> */}
            <Button variant="secondary" onClick={async () => {await this.transfer();} }>Transfer</Button>
            <Button variant="secondary" onClick={this.retrieveChildChainBalance}>OMG balance</Button>
            <Button variant="secondary" onClick={this.componentDidMount}>Reload</Button>
          </div>
          {this.state.messages.map((message, i) => (
            <Card key={i} className="card">
              <Card.Header>{message.date}</Card.Header>
              <Row>
              <Col xs={10}>
              <Card.Body>
                <Card.Title>{message.payload}</Card.Title>
                <Card.Text>
                  {message.header.pType}, {message.header.counter}, {message.header.deviceAdd}
                </Card.Text>
              </Card.Body>
              </Col>
              <Col>
              {/* <Button variant="secondary" onClick={this.componentDidMount}>Modify</Button> */}
              <Button className="mybutton" variant="danger" onClick={this.deleteClick(message._id)}>Delete</Button>
              </Col>
              </Row>
            </Card>
          ))}
        </div>
    </div>
   );
  }
}


export default Messages;