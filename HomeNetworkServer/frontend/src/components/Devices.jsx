import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Modal, Row, Col, Form } from 'react-bootstrap';



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
      add: []
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

  closeAndReload(){
    this.setState({ showHide: !this.state.showHide })

    //console.log(this.state.val2);
    if(this.state.val2 !== ""){
      // update server
      const url = 'http://163.172.130.246:8080/devices/' + this.state.add.deviceAdd;
      axios.patch(url, {"deviceAdd":this.state.add.deviceAdd, "name":this.state.val2}).then(response => response.data)
      .then((data) => {
        this.componentDidMount()
      })
      .catch(function (error) {
        console.log(error);
      });
      this.setState({ val2: "" })
    } else {
      this.componentDidMount()
    }
  }

  deleteClick = value => () => {
    //console.log(value);

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
  
  render() {
    return (
      <div className="container">
        <div className="col-xs-8">
          <div className="header">
            <h1>Devices</h1>
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