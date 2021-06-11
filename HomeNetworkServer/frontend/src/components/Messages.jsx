import React from "react";
import axios from 'axios';
import './Style.css';
import { Button, Card, Row, Col } from 'react-bootstrap';
import { ethers } from 'ethers'



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

        // send to the server that has payed for this owner and device
        const url = 'http://163.172.130.246:8080/pay/' + this.state.address + '/' + key;
        axios.patch(url, {"payed": true}).then(response => response.data)
        .then((data) => {
          console.log("payed !");
        })
        .catch(function (error) {
          console.log(error);
        });

      }
    }
    this.componentDidMount()
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
  
  render() {
    return (
      <div className="container">
        <div className="col-xs-8">
          <div className="header">
            <h1>Messages</h1>
            <div>
              {(() => {
                if (this.state.total > 0) {
                  return (
                    <div className="d-flex align-items-center">
                    <p className="p_pay">{this.state.total} messages to pay for</p>
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