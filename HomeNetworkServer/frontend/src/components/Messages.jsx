import React from "react";
import axios from 'axios';
import './Messages.css';
import { Button, Card, Modal, Row, Col } from 'react-bootstrap';



class Messages extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      messages: [],
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

    const items = this.state.messages.filter(item => item.deviceAdd !== value);
    this.setState({ messages: items });

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
    const url = 'http://163.172.130.246:8080/msg';
    axios.get(url).then(response => response.data)
    .then((data) => {
      this.setState({ messages: data })
      console.log(this.state.messages)
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
            <h1>Messages</h1>
            <Button variant="secondary" onClick={this.componentDidMount}>Reload</Button>
            <Button variant="primary" onClick={() => this.createDevice()}>Add message</Button>

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
          {this.state.messages.map((message, i) => (
            <Card key={i} className="card">
              <Card.Header>{message._id}</Card.Header>
              <Row>
              <Col xs={10}>
              <Card.Body>
                <Card.Title>{message.payload}</Card.Title>
                <Card.Text>
                  {message.header.pType}, {message.header.counter}, {message.header.deviceAdd}
                </Card.Text>
              </Card.Body>
              </Col>
              <Col center>
              <Button variant="secondary" onClick={this.componentDidMount}>Modify</Button>
              <Button variant="danger" onClick={this.deleteClick(message.payload)}>Delete</Button>
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