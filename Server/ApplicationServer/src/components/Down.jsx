import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Row, Col, Modal, Form } from 'react-bootstrap';


class Down extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      messages: [],
      modal_resp: false,
      deviceAdd: "",
      payload: "",
      down: "",
      id: ""
    };

    this.componentDidMount = this.componentDidMount.bind(this);
  }


  handleModalShowHide() {
    this.setState({ modal_resp: !this.state.modal_resp })
    this.setState({ deviceAdd: "" })
    this.setState({ down: "" })
  }

  openModalSend = (id, deviceAdd, payload) => () => {
    //console.log(name);
    this.setState({ modal_resp: !this.state.modal_resp })
    this.setState({ id: id })
    this.setState({ deviceAdd: deviceAdd })
    this.setState({ payload: payload })
  };

  send() {
    this.setState({ modal_resp: !this.state.modal_resp })

    if(this.state.down !== ""){
      // update server
      const url = 'http://163.172.130.246:8080/down/' + this.state.id;
      axios.patch(url, {"deviceAdd":this.state.deviceAdd, "payload":this.state.down}).then(response => response.data)
      .then((data) => {
        this.componentDidMount()
        // console.log("send")
      })
      .catch(function (error) {
        console.log(error);
      });

      this.setState({ deviceAdd: "" })
      this.setState({ payload: "" })
      this.setState({ id: "" })
      this.setState({ down: "" })
    }
  }

  deleteClick = value => () => {
    const items = this.state.messages.filter(item => item._id !== value);
    this.setState({ messages: items });

    const url = 'http://163.172.130.246:8080/down/' + value;
    axios.delete(url).then(response => response.data)
    .then((data) => {

     })
    .catch(function (error) {
      console.log(error);
    });

  };

  async componentDidMount() {
    const url = 'http://163.172.130.246:8080/down';
    axios.get(url).then(response => response.data)
    .then((data) => {
      this.setState({ messages: data })
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
            <h1>Down messages</h1>
            <Button variant="secondary" onClick={this.componentDidMount}>Reload</Button>
          </div>
          {this.state.messages.map((message, i) => (
            <Card key={i} className="card">
              <Card.Header>{message.date}</Card.Header>
              <Row>
              <Col xs={9}>
              <Card.Body>
                <Card.Title>{message.payload}</Card.Title>
                <Card.Text>
                  {message.deviceAdd}, sent : {String(message.payed)}
                </Card.Text>
              </Card.Body>
              </Col>
              <Col>
              <div>
              <Button className="mybutton_message" variant="secondary" onClick={this.openModalSend(message._id, message.deviceAdd, message.payload)}>Modify</Button>
              <Button className="mybutton_message2" variant="danger" onClick={this.deleteClick(message._id)}>Delete</Button>
              </div>
              </Col>
              </Row>
            </Card>
          ))}

          <Modal 
            dialogClassName="my-modal"
            show={this.state.modal_resp}
            onHide={() => this.handleModalShowHide()}
          >
                <Modal.Header>
                  <Modal.Title className="modal-test">{this.state.deviceAdd}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                <h5>Message to send :</h5>
                <Form>
                  <Form.Group controlId="formBasicName">
                    <Form.Control
                      placeholder={this.state.payload}
                      value={this.state.down}
                      onChange={e => this.setState({ down: e.target.value })}
                      type="name"
                    />
                  </Form.Group>
                </Form>
                </Modal.Body>
                <Modal.Footer>
                <Button variant="danger" onClick={() => this.handleModalShowHide()}>
                    Close
                </Button>
                <Button variant="primary" onClick={() => this.send()}>
                    Modify
                </Button>
                </Modal.Footer>
            </Modal> 
        </div>
    </div>
   );
  }
}


export default Down;