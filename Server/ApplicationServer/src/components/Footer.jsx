var style = {
  backgroundColor: "#343a40",
  color: "#ffffff",
  borderTop: "1px solid #E7E7E7",
  textAlign: "center",
  padding: "20px",
  position: "fixed",
  left: "0",
  bottom: "0",
  height: "60px",
  width: "100%",
}

var phantom = {
  display: 'block',
  padding: '60px',
  height: '60px',
  width: '100%',
}

function Footer({ children }) {
  return (
      <div>
          <div style={phantom} />
          <div style={style}>
              { children }
              Copyright &copy; Decentralized LoRa infrastructure using blockchain 2021
          </div>
      </div>
  )
}

export default Footer
