import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Modal, Row, Col, Form, Spinner } from 'react-bootstrap';
// import Web3 from 'web3';
import { ethers } from 'ethers'
import { loraResolverAbi } from './abis';
// import BigNumber from 'bn.js';
import bigInt from 'big-integer';

// const web3 = new Web3(Web3.givenProvider);
// const contractAddr = '0xc3C5B3159dE1d2f348Ff952a7175648E77Af23c7';
// ropsten
// const contractAddr = '0xCd862ceF6D5EDd348854e4a280b62d51F7F62a65';    
// rinkeby
const contractAddr = '0x4a9fF7c806231fF7d4763c1e83E8B131467adE61';
// const SimpleContract = new web3.eth.Contract(simpleStorageAbi, contractAddr);

// const serverAdd = 2745991926
// const x_pub_server = "c29769136166eec1299e1b5d56c48de1787a3f72f0e8ee5c14357ef5b78fc6ea"
// const y_pub_server = "7666b00c308248cf824c8e224dd8ffcc4ccd1362c822f2ea82f5b01f79e1b49a"


class Devices extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      devices: [],
      showHide : false,
      modal : false,
      modal_resp : false,
      name : "test",
      deviceAdd: "test",
      pubkey: "test",
      val: "",
      val2: "",
      down: "",
      add: [],
      server: [],
      willShowLoader: false,
      error: false,
    };

    this.componentDidMount = this.componentDidMount.bind(this);
  }

  handleModalShowHide() {
    this.setState({ showHide: !this.state.showHide })
    this.setState({ val2: "" })

    const url = 'http://163.172.130.246:8080/devices/' + this.state.add.deviceAdd;
    axios.delete(url).then(response => response.data)
    .then((data) => {

     })
    .catch(function (error) {
      console.log(error);
    });
  }

  handleModal2ShowHide() {
    this.setState({ modal: !this.state.modal })
    this.setState({ val: "" })
    this.setState({ name: "" })
    this.setState({ deviceAdd: "" })
    this.setState({ pubkey: "" })
  }

  handleModal3ShowHide() {
    this.setState({ modal_resp: !this.state.modal_resp })
    this.setState({ name: "" })
    this.setState({ deviceAdd: "" })
    this.setState({ down: "" })
  }

  submit() {
    this.setState({ modal: !this.state.modal })

    //console.log(this.state.val);
    if(this.state.val !== ""){
      // update server
      const url = 'http://163.172.130.246:8080/devices/' + this.state.deviceAdd;
      axios.patch(url, {"deviceAdd":this.state.deviceAdd, "name":this.state.val}).then(response => response.data)
      .then((data) => {
        this.componentDidMount()
      })
      .catch(function (error) {
        console.log(error);
      });

      this.setState({ val: "" })
      this.setState({ name: "" })
      this.setState({ deviceAdd: "" })
      this.setState({ pubkey: "" })
    }
  }

  send() {
    this.setState({ modal_resp: !this.state.modal_resp })

    //console.log(this.state.val);
    if(this.state.down !== ""){
      // update server
      const url = 'http://163.172.130.246:8080/down';
      axios.post(url, {"deviceAdd":this.state.deviceAdd, "payload":this.state.down}).then(response => response.data)
      .then((data) => {
        // this.componentDidMount()
        // console.log("send")
      })
      .catch(function (error) {
        console.log(error);
      });

      this.setState({ name: "" })
      this.setState({ deviceAdd: "" })
      this.setState({ down: "" })
    }
  }

  openModal = (name, deviceAdd, pubkey) => () => {
    //console.log(name);
    this.setState({ modal: !this.state.modal })
    this.setState({ name: name })
    this.setState({ deviceAdd: deviceAdd })
    this.setState({ pubkey: pubkey })
  };

  openModalSend = (name, deviceAdd) => () => {
    //console.log(name);
    this.setState({ modal_resp: !this.state.modal_resp })
    this.setState({ name: name })
    this.setState({ deviceAdd: deviceAdd })
  };

  createDevice(){
    this.setState({ showHide: !this.state.showHide })
    
    const url = 'http://163.172.130.246:8080/generate';
    axios.get(url).then(response => response.data)
    .then((data) => {
      this.setState({ add: data })
      //console.log(this.state.add)
     })
    .catch(function (error) {
      console.log(error);
    });
  }

  async closeAndReload(){
    this.setState({ showHide: !this.state.showHide })
    // console.log(this.state.add.deviceAdd);
    // console.log(this.state.add.serverAdd);
    // console.log(this.state.add.port);

    //console.log(this.state.val2);
    if(this.state.val2 !== ""){
      // update server
      const url = 'http://163.172.130.246:8080/devices/' + this.state.add.deviceAdd;
      axios.patch(url, {"deviceAdd":this.state.add.deviceAdd, "name":this.state.val2}).then(response => response.data)
      .then((data) => {
        this.componentDidMount()
        this.handleSet(this.state.add.deviceAdd, this.state.add.serverAdd, this.state.add.port, "0x" + this.state.add.x_pub, "0x" + this.state.add.y_pub)
      })
      .catch(function (error) {
        console.log(error);
      });
      this.setState({ val2: "" })
    } else {
      this.componentDidMount()
      this.handleSet(this.state.add.deviceAdd, this.state.add.serverAdd, this.state.add.port, "0x" + this.state.add.x_pub, "0x" + this.state.add.y_pub)
    }
  }

  deleteClick = value => () => {
    // console.log(value);

    const items = this.state.devices.filter(item => item.deviceAdd !== value);
    this.setState({ devices: items });

    const url = 'http://163.172.130.246:8080/devices/' + value;
    axios.delete(url).then(response => response.data)
    .then((data) => {

     })
    .catch(function (error) {
      console.log(error);
    });

    //this.componentDidMount()
  };

  delete(value) {
    // console.log(value);

    const items = this.state.devices.filter(item => item.deviceAdd !== value);
    this.setState({ devices: items });

    const url = 'http://163.172.130.246:8080/devices/' + value;
    axios.delete(url).then(response => response.data)
    .then((data) => {

     })
    .catch(function (error) {
      console.log(error);
    });

    //this.componentDidMount()
  };

  componentDidMount() {
    //console.log("reload");
    const url = 'http://163.172.130.246:8080/devices';
    axios.get(url).then(response => response.data)
    .then((data) => {
      this.setState({ devices: data })
      //console.log(this.state.devices)
     })
    .catch(function (error) {
      console.log(error); 
    });

    // get the ip of the server
    const url2 = 'http://163.172.130.246:8080/ip';
    axios.get(url2).then(response => response.data)
    .then((data) => {
      // look if server already stored in db, otherwise, store it
      this.setState({ server: data })
      this.getDeviceBlockchain(data)
     })
    .catch(function (error) {
      console.log(error); 
    });
  }


  async getDeviceBlockchain(server){
    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
      const provider = new ethers.providers.Web3Provider(window.ethereum)
      const contract = new ethers.Contract(contractAddr, loraResolverAbi, provider)
      try {

        // if ip4
        var data = ""
        if (server['ADDR_type'] === "IPv4"){
          data = await contract.ipv4Servers(server["ADDR_int"]);
          // const data = await contract.publicstoredData()
          console.log('data: ', data)
        }
        if (server['ADDR_type'] === "IPv6"){
          console.log("get IPv6")
          var num = bigInt(server["ADDR_int"])
          // console.log(num)
          data = await contract.ipv6Servers(num.value);
          // const data = await contract.publicstoredData()
          console.log('data: ', data)
        }
        if (server['ADDR_type'] === "domain"){
          data = await contract.domainServers(server["ADDR_int"]);
          // const data = await contract.publicstoredData()
          console.log('data: ', data)
        }

        if (data['owner'] === "0x0000000000000000000000000000000000000000"){
          console.log("add device")

          // get pubkey
          const url = 'http://163.172.130.246:8080/pubkey';
          axios.get(url).then(response => response.data)
          .then((data) => {
            this.store_pubkey(server, data)
          })
          .catch(function (error) {
            console.log(error); 
          });

        }
      } catch (err) {
        console.log("Error: ", err)
      }
    } 
  }

  async store_pubkey(server, pubkey){
    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
      try {
        const provider = new ethers.providers.Web3Provider(window.ethereum)
        const signer = provider.getSigner()
        const contract = new ethers.Contract(contractAddr, loraResolverAbi, signer)

        if (server['ADDR_type'] === "IPv4"){
          const transaction = await contract.registerIpv4Server(server["ADDR_int"], "0x" + pubkey["x_pub_server"], "0x" + pubkey["y_pub_server"])
          this.setState({willShowLoader: true});
          await transaction.wait()
          this.setState({willShowLoader: false});
        }
        if (server['ADDR_type'] === "IPv6"){
          console.log("add IPv6")
          var num = bigInt(server["ADDR_int"])
          const transaction = await contract.registerIpv6Server(num.value, "0x" + pubkey["x_pub_server"], "0x" + pubkey["y_pub_server"])
          this.setState({willShowLoader: true});
          await transaction.wait()
          this.setState({willShowLoader: false});
        }
        if (server['ADDR_type'] === "domain"){
          const transaction = await contract.registerDomainServer(server["ADDR_int"], "0x" + pubkey["x_pub_server"], "0x" + pubkey["y_pub_server"])
          this.setState({willShowLoader: true});
          await transaction.wait()
          this.setState({willShowLoader: false});
        }
      } catch (err) {
        console.log("Error: ", err)
      }
    }
  }



  // handleGet = async (e) => {
  //   e.preventDefault();
  //   const result = await SimpleContract.methods.get().call();
  //   // setGetNumber(result);
  //   console.log(result);
  // };

  // request access to the user's MetaMask account
  // async requestAccount() {
  //   await window.ethereum.request({ method: 'eth_requestAccounts' });
  // }

  async handleGet() {
    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
      const provider = new ethers.providers.Web3Provider(window.ethereum)
      const contract = new ethers.Contract(contractAddr, loraResolverAbi, provider)
      try {
        const data = await contract.devices("0xd454ddb830bee4cf");
        // const data = await contract.publicstoredData()
        console.log('data: ', data)
      } catch (err) {
        console.log("Error: ", err)
      }
    }    
  }

  // call the smart contract, send an update
  async handleSet(deviceAdd, serverAddr, port, x_pub, y_pub) {
    // console.log(serverAddr);
    // console.log(port);
    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
      try{
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        this.setState({error: false});
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner()
        const contract = new ethers.Contract(contractAddr, loraResolverAbi, signer)

        var transaction = ""
        if (this.state.server['ADDR_type'] === "IPv4"){
          transaction = await contract.registerIpv4Device(deviceAdd, serverAddr, port, x_pub, y_pub)
        }
        if (this.state.server['ADDR_type'] === "IPv6"){
          var num = bigInt(serverAddr)
          transaction = await contract.registerIpv6Device(deviceAdd, num.value, port, x_pub, y_pub)
        }
        if (this.state.server['ADDR_type'] === "domain"){
          transaction = await contract.registerDomainDevice(deviceAdd, serverAddr, port, x_pub, y_pub)
        }

        // const transaction = await contract.registerIpv4Device(deviceAdd, serverAddr, port, x_pub, y_pub)
        // console.log("end 1");
        this.setState({willShowLoader: true});
        await transaction.wait()
        // console.log("end 2");
        this.setState({willShowLoader: false});
      } catch(e) {
        console.log("Error, reject");
        this.delete(deviceAdd)
      }
      
    } else {
      // console.log("Error, no Metamask");
      this.setState({error: true});
    }
  }

  // async handleGet() {
  //   // e.preventDefault();
  //   const result = await SimpleContract.methods.get().call();
  //   // setGetNumber(result);
  //   console.log(result);
  // }
  
  render() {
    return (
      <div className="container">
        <div className="col-xs-8">
          <div className="header">
            <h1>Devices</h1>
            <div>
              {this.state.error ? 
              <div className="d-flex align-items-center">
                <p className="error">Error, no Metamask</p>
              </div>:
              <p></p>}
            </div>
            <div>
              {this.state.willShowLoader ? 
              <div className="d-flex align-items-center">
                <p className="pspinner">TX PENDING</p><Spinner className="spinner" animation="border" />
              </div>:
              <p></p>}
              {/* <Spinner className="spinner" animation="border" /> */}
            </div>
            {/* <Button variant="secondary" onClick={this.handleGet}>Get</Button> */}
            {/* <Button variant="secondary" onClick={this.handleSet}>Set</Button> */}
            <Button variant="secondary" onClick={this.componentDidMount}>Reload</Button>
            <Button variant="primary" onClick={() => this.createDevice()}>Add device</Button>

            <Modal 
              dialogClassName="my-modal"
              show={this.state.showHide}
              onHide={() => this.handleModalShowHide()}
            >
                    {/* <Modal.Header closeButton onClick={() => this.handleModalShowHide()}> */}
                    <Modal.Header>
                      <Modal.Title className="modal-test">{this.state.add.name}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <h5>Name :</h5>
                        <Form>
                          <Form.Group controlId="formBasicName">
                            {/* <Form.Control type="name" placeholder={this.state.name} /> */}
                            <Form.Control
                              placeholder={this.state.add.name}
                              value={this.state.val2}
                              onChange={e => this.setState({ val2: e.target.value })}
                              type="name"
                              className="form-test"
                            />
                          </Form.Group>
                        </Form>
                        <h5>Public key :</h5>
                        <p>x_pub : {this.state.add.x_pub}</p>
                        <p className="p-test">y_pub : {this.state.add.y_pub}</p>
                        <h5>Private key :</h5>
                        <p>{this.state.add.privkey}</p>
                    </Modal.Body>
                    <Modal.Footer>
                    <Button variant="danger" onClick={() => this.handleModalShowHide()}>
                        Close
                    </Button>
                    <Button variant="primary" onClick={() => this.closeAndReload()}>
                        Add device
                    </Button>
                    </Modal.Footer>
            </Modal>

          </div>
          {this.state.devices.map((device) => (
            <Card key={device.deviceAdd} className="card">
              <Card.Header className="card-test">{device.name}</Card.Header>
              <Row>
                <Col xs={10} className="mycard">
                <Card.Body>
                  <Card.Title>{device.deviceAdd}</Card.Title>
                  <Card.Text as="div">
                  <p className="p-test3">x_pub : {device.x_pub}</p>
                  <p className="p-test2">y_pub : {device.y_pub}</p>
                  </Card.Text>
                </Card.Body>
                </Col>
                <Col>
                <div>
                  <Button className="mybutton_device" variant="success" onClick={this.openModalSend(device.name, device.deviceAdd)}>Send</Button>
                  <Button className="mybutton_device" variant="secondary" onClick={this.openModal(device.name, device.deviceAdd, device.pubkey)}>Modify</Button>
                  <Button className="mybutton_device2" variant="danger" onClick={this.deleteClick(device.deviceAdd)}>Delete</Button>
                </div>
                </Col>
              </Row>
            </Card>
          ))}
          <Modal 
            dialogClassName="my-modal"
            show={this.state.modal}
            onHide={() => this.handleModal2ShowHide()}
          >
                {/* <Modal.Header closeButton onClick={() => this.handleModal2ShowHide()}> */}
                <Modal.Header>
                  <Modal.Title className="modal-test">{this.state.name}</Modal.Title>
                  <Modal.Title className="modal-test">{this.state.deviceAdd}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                <h5>Name :</h5>
                <Form>
                  <Form.Group controlId="formBasicName">
                    {/* <Form.Label>Name</Form.Label> */}
                    {/* <Form.Control type="name" placeholder={this.state.name} /> */}
                    <Form.Control
                      placeholder={this.state.name}
                      value={this.state.val}
                      onChange={e => this.setState({ val: e.target.value })}
                      type="name"
                    />
                  </Form.Group>
                </Form>
                </Modal.Body>
                <Modal.Footer>
                <Button variant="danger" onClick={() => this.handleModal2ShowHide()}>
                    Close
                </Button>
                <Button variant="primary" onClick={() => this.submit()}>
                    Modify
                </Button>
                </Modal.Footer>
            </Modal> 

            <Modal 
            dialogClassName="my-modal"
            show={this.state.modal_resp}
            onHide={() => this.handleModal3ShowHide()}
          >
                {/* <Modal.Header closeButton onClick={() => this.handleModal2ShowHide()}> */}
                <Modal.Header>
                  <Modal.Title className="modal-test">{this.state.name}</Modal.Title>
                  <Modal.Title className="modal-test">{this.state.deviceAdd}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                <h5>Message to send :</h5>
                <Form>
                  <Form.Group controlId="formBasicName">
                    {/* <Form.Label>Name</Form.Label> */}
                    {/* <Form.Control type="name" placeholder={this.state.name} /> */}
                    <Form.Control
                      placeholder="payload"
                      value={this.state.down}
                      onChange={e => this.setState({ down: e.target.value })}
                      type="name"
                    />
                  </Form.Group>
                </Form>
                </Modal.Body>
                <Modal.Footer>
                <Button variant="danger" onClick={() => this.handleModal3ShowHide()}>
                    Close
                </Button>
                <Button variant="primary" onClick={() => this.send()}>
                    Send
                </Button>
                </Modal.Footer>
            </Modal> 
        </div>
    </div>
   );
  }
}


export default Devices;
