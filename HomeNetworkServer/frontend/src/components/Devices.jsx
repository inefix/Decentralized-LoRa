import React from "react";
import axios from 'axios';
import './Devices.css';
import { Button, Card, Modal, Row, Col } from 'react-bootstrap';



class Devices extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      devices: [],
      showHide : false,
      add: []
    };

    this.componentDidMount = this.componentDidMount.bind(this);
  }

  handleModalShowHide() {
    this.setState({ showHide: !this.state.showHide })
  }

  createDevice(){
    this.setState({ showHide: !this.state.showHide })
    
    const url = 'http://163.172.130.246:8080/generate';
    axios.get(url).then(response => response.data)
    .then((data) => {
      this.setState({ add: data })
      console.log(this.state.add)
     })
    .catch(function (error) {
      console.log(error);
    });
  }

  closeAndReload(){
    this.setState({ showHide: !this.state.showHide })

    this.componentDidMount()
  }

  deleteClick = value => () => {
    console.log(value);

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
    const url = 'http://163.172.130.246:8080/devices';
    axios.get(url).then(response => response.data)
    .then((data) => {
      this.setState({ devices: data })
      console.log(this.state.devices)
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
            >
                    {/* <Modal.Header closeButton onClick={() => this.handleModalShowHide()}> */}
                    <Modal.Header>
                      <Modal.Title>{this.state.add.deviceAdd}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <h5>Public key :</h5>
                        <p className="p-test">{this.state.add.pubkey}</p>
                        <h5>Private key :</h5>
                        <p>{this.state.add.privkey}</p>
                    </Modal.Body>
                    <Modal.Footer>
                    <Button variant="secondary" onClick={() => this.closeAndReload()}>
                        Close
                    </Button>
                    </Modal.Footer>
            </Modal>

          </div>
          <React.Fragment>
          {this.state.devices.map((device) => (
            <Card key={device.deviceAdd} className="card">
              {/* <Card.Header>{device.deviceAdd}</Card.Header> */}
              <Row>
                <Col xs={10} className="mycard">
                <Card.Body>
                  <Card.Title>{device.deviceAdd}</Card.Title>
                  <Card.Text>
                    {device.pubkey}
                  </Card.Text>
                </Card.Body>
                </Col>
                <Col center>
                <div className="mydiv">
                  <Button variant="secondary" onClick={this.componentDidMount}>Modify</Button>
                  <Button variant="danger" onClick={this.deleteClick(device.deviceAdd)}>Delete</Button>
                </div>
                </Col>
              </Row>
            </Card>
          ))}
          </React.Fragment>
        </div>
    </div>
   );
  }
}


export default Devices;