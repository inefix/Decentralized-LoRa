import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Modal, Row, Col, Form, Spinner } from 'react-bootstrap';
import { ethers } from 'ethers'
import { loraResolverAbi } from './abis';
import bigInt from 'big-integer';

const contractAddr = '0x4a9fF7c806231fF7d4763c1e83E8B131467adE61';

class Devices extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      devices: [],
      showHide : false,
      modal : false,
      modal_resp : false,
      name : "",
      deviceAdd: "",
      x_pub: "",
      y_pub: "",
      pubkey: "",
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
    this.setState({ deviceAdd: "" })
    this.setState({ x_pub: "" })
    this.setState({ y_pub: "" })
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

  openModal = (name, deviceAdd) => () => {
    //console.log(name);
    this.setState({ modal: !this.state.modal })
    this.setState({ name: name })
    this.setState({ deviceAdd: deviceAdd })
  };

  openModalSend = (name, deviceAdd) => () => {
    //console.log(name);
    this.setState({ modal_resp: !this.state.modal_resp })
    this.setState({ name: name })
    this.setState({ deviceAdd: deviceAdd })
  };

  createDevice(){
    this.setState({ showHide: !this.state.showHide })
  }

  async closeAndReload(){
    this.setState({ showHide: !this.state.showHide })

    if(this.state.val2 !== "" && this.state.deviceAdd !== "" && this.state.x_pub !== "" && this.state.y_pub !== ""){
      // update server
      const url = 'http://163.172.130.246:8080/devices';
      axios.post(url, {"deviceAdd":this.state.deviceAdd, "name":this.state.val2, "x_pub": this.state.x_pub, "y_pub": this.state.y_pub}).then(response => response.data)
      .then((data) => {
        this.componentDidMount()
        // console.log(data)
        this.handleSet(this.state.deviceAdd, data["serverAdd"], data["port"], "0x" + this.state.x_pub, "0x" + this.state.y_pub)

        this.setState({ val2: "" })
        this.setState({ deviceAdd: "" })
        this.setState({ x_pub: "" })
        this.setState({ y_pub: "" })
      })
      .catch(function (error) {
        console.log(error);
        this.setState({ val2: "" })
        this.setState({ deviceAdd: "" })
        this.setState({ x_pub: "" })
        this.setState({ y_pub: "" })
      });
    } else {
      this.componentDidMount()
    }
  }

  deleteClick = value => () => {
    const items = this.state.devices.filter(item => item.deviceAdd !== value);
    this.setState({ devices: items });

    const url = 'http://163.172.130.246:8080/devices/' + value;
    axios.delete(url).then(response => response.data)
    .then((data) => {

     })
    .catch(function (error) {
      console.log(error);
    });
  };


  delete(value) {

    const items = this.state.devices.filter(item => item.deviceAdd !== value);
    this.setState({ devices: items });

    const url = 'http://163.172.130.246:8080/devices/' + value;
    axios.delete(url).then(response => response.data)
    .then((data) => {
      this.componentDidMount()
     })
    .catch(function (error) {
      console.log(error);
    });
  };

  componentDidMount() {
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
          // console.log('data: ', data)
        }
        if (server['ADDR_type'] === "IPv6"){
          console.log("get IPv6")
          var num = bigInt(server["ADDR_int"])
          data = await contract.ipv6Servers(num.value);
        }
        if (server['ADDR_type'] === "domain"){
          data = await contract.domainServers(server["ADDR_int"]);
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

  // call the smart contract, send an update
  async handleSet(deviceAdd, serverAddr, port, x_pub, y_pub) {
    console.log(deviceAdd);
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
        console.log(e);
        console.log(deviceAdd);
        this.delete(deviceAdd)
      }
      
    } else {
      // console.log("Error, no Metamask");
      this.setState({error: true});
    }
  }

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
            </div>
            <Button variant="secondary" onClick={this.componentDidMount}>Reload</Button>
            <Button variant="primary" onClick={() => this.createDevice()}>Add device</Button>

            <Modal 
              dialogClassName="my-modal"
              show={this.state.showHide}
              onHide={() => this.handleModalShowHide()}
            >
                    <Modal.Header>
                      <Modal.Title className="modal-test">Add a new device</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <h5>Name :</h5>
                        <Form>
                          <Form.Group controlId="formBasicName">
                            <Form.Control
                              placeholder="name"
                              value={this.state.val2}
                              onChange={e => this.setState({ val2: e.target.value })}
                              type="name"
                              className="form-test"
                            />
                          </Form.Group>
                        </Form>

                        <h5>deviceAdd :</h5>
                        <Form>
                          <Form.Group controlId="formBasicName">
                            <Form.Control
                              placeholder="deviceAdd"
                              value={this.state.deviceAdd}
                              onChange={e => this.setState({ deviceAdd: e.target.value })}
                              type="name"
                              className="form-test"
                            />
                          </Form.Group>
                        </Form>

                        <h5>Public key :</h5>
                        <Form>
                          <Form.Group controlId="formBasicName">
                            <Form.Control
                              placeholder="x_pub"
                              value={this.state.x_pub}
                              onChange={e => this.setState({ x_pub: e.target.value })}
                              type="name"
                              className="form-test2"
                            />
                          </Form.Group>
                        </Form>
                        <Form>
                          <Form.Group controlId="formBasicName">
                            <Form.Control
                              placeholder="y_pub"
                              value={this.state.y_pub}
                              onChange={e => this.setState({ y_pub: e.target.value })}
                              type="name"
                              className="form-test"
                            />
                          </Form.Group>
                        </Form>

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
                  <Button className="mybutton_device" variant="secondary" onClick={this.openModal(device.name, device.deviceAdd)}>Modify</Button>
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
                <Modal.Header>
                  <Modal.Title className="modal-test">{this.state.name}</Modal.Title>
                  <Modal.Title className="modal-test">{this.state.deviceAdd}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                <h5>Name :</h5>
                <Form>
                  <Form.Group controlId="formBasicName">
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
                <Modal.Header>
                  <Modal.Title className="modal-test">{this.state.name}</Modal.Title>
                  <Modal.Title className="modal-test">{this.state.deviceAdd}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                <h5>Message to send :</h5>
                <Form>
                  <Form.Group controlId="formBasicName">
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
