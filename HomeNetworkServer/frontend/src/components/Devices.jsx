import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Modal, Row, Col, Form, Spinner } from 'react-bootstrap';
// import Web3 from 'web3';
import { ethers } from 'ethers'
import { simpleStorageAbi } from './abis';

// const web3 = new Web3(Web3.givenProvider);
// const contractAddr = '0xc3C5B3159dE1d2f348Ff952a7175648E77Af23c7';
const contractAddr = '0xCd862ceF6D5EDd348854e4a280b62d51F7F62a65';
// const SimpleContract = new web3.eth.Contract(simpleStorageAbi, contractAddr);


class Devices extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      devices: [],
      showHide : false,
      modal : false,
      name : "test",
      deviceAdd: "test",
      pubkey: "test",
      val: "",
      val2: "",
      add: [],
      willShowLoader: false,
      error: false
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
    }
  }

  openModal = (name, deviceAdd, pubkey) => () => {
    //console.log(name);
    this.setState({ modal: !this.state.modal })
    this.setState({ name: name })
    this.setState({ deviceAdd: deviceAdd })
    this.setState({ pubkey: pubkey })
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
        this.handleSet(this.state.add.deviceAdd, this.state.add.serverAdd, this.state.add.port)
      })
      .catch(function (error) {
        console.log(error);
      });
      this.setState({ val2: "" })
    } else {
      this.componentDidMount()
      this.handleSet(this.state.add.deviceAdd, this.state.add.serverAdd, this.state.add.port)
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
      const contract = new ethers.Contract(contractAddr, simpleStorageAbi, provider)
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
  async handleSet(deviceAdd, serverAddr, port) {
    // console.log(serverAddr);
    // console.log(port);
    if (typeof window.ethereum !== 'undefined' || (typeof window.web3 !== 'undefined')) {
      try{
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        this.setState({error: false});
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner()
        const contract = new ethers.Contract(contractAddr, simpleStorageAbi, signer)
        const transaction = await contract.registerIpv4(deviceAdd, serverAddr, port)
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
                        <p className="p-test">{this.state.add.pubkey}</p>
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
                  <Card.Text>
                    {device.pubkey}
                  </Card.Text>
                </Card.Body>
                </Col>
                <Col>
                <div>
                  <Button className="mybutton_device" variant="secondary" onClick={this.openModal(device.name, device.deviceAdd, device.pubkey)}>Modify</Button>
                  <Button className="mybutton_device" variant="danger" onClick={this.deleteClick(device.deviceAdd)}>Delete</Button>
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
        </div>
    </div>
   );
  }
}


export default Devices;
