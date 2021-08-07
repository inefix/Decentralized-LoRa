import json
import time

abi_mpc = json.loads('[{"inputs":[{"internalType":"address payable","name":"_recipient","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"constant":false,"inputs":[],"name":"claimTimeout","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"close","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"expiration","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"newExpiration","type":"uint256"}],"name":"extend","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"isValidSignature","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"recipient","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"sender","outputs":[{"internalType":"address payable","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]')
runtimeBytecode_mpc = '0x608060405234801561001057600080fd5b506004361061007d5760003560e01c806366d003ac1161005b57806366d003ac1461016f57806367e404ce146101b95780639714378c14610203578063b2af9362146102315761007d565b80630e1da6c314610082578063415ffba71461008c5780634665096d14610151575b600080fd5b61008a61030e565b005b61014f600480360360408110156100a257600080fd5b8101908080359060200190929190803590602001906401000000008111156100c957600080fd5b8201836020820111156100db57600080fd5b803590602001918460018302840111640100000000831117156100fd57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610357565b005b610159610467565b6040518082815260200191505060405180910390f35b61017761046d565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6101c1610493565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61022f6004803603602081101561021957600080fd5b81019080803590602001909291905050506104b8565b005b6102f46004803603604081101561024757600080fd5b81019080803590602001909291908035906020019064010000000081111561026e57600080fd5b82018360208201111561028057600080fd5b803590602001918460018302840111640100000000831117156102a257600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610529565b604051808215151515815260200191505060405180910390f35b60025442101561031d57600080fd5b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16146103b157600080fd5b6103bb8282610529565b6103c457600080fd5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc839081150290604051600060405180830381858888f1935050505015801561042c573d6000803e3d6000fd5b506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16ff5b60025481565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461051157600080fd5b600254811161051f57600080fd5b8060028190555050565b6000806105923085604051602001808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660601b815260140182815260200192505050604051602081830303815290604052805190602001206105f6565b90506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166105d6828561064e565b73ffffffffffffffffffffffffffffffffffffffff161491505092915050565b60008160405160200180807f19457468657265756d205369676e6564204d6573736167653a0a333200000000815250601c01828152602001915050604051602081830303815290604052805190602001209050919050565b60008060008061065d856106d5565b92509250925060018684848460405160008152602001604052604051808581526020018460ff1660ff1681526020018381526020018281526020019450505050506020604051602081039080840390855afa1580156106c0573d6000803e3d6000fd5b50505060206040510351935050505092915050565b600080600060418451146106e857600080fd5b6020840151915060408401519050606084015160001a9250828282925092509250919390925056fea265627a7a72315820b76f0f1cee859ce5547cf4dc1552adf93171ccfe07e152a85efabc97ed5c0f6064736f6c63430005110032'

async def verify_mpc_payment(web3, client, signature, contract_add, payed_amount, remote_host, balance_threshold, time_threshold):
    db = client['lora_db']
    collection_MPC = db['MPC']
    contract_mpc = web3.eth.contract(contract_add, abi=abi_mpc)

    # verify valid bytecode 
    bytecode = await web3.eth.getCode(contract_add)
    bytecode = bytecode.hex()
    if bytecode == runtimeBytecode_mpc :

        # verify if MPC document present
        # get amount and calculate new one
        mpc_document = await get_mpc_document(collection_MPC, contract_add)
        # print("mpc_document :", mpc_document)
        if mpc_document == None :
            amount = 0
        else :
            amount = mpc_document['amount']

        expiration = await contract_mpc.functions.expiration().call()
        # print("expiration :", expiration)
        # verify that the smart contract has not expired
        epoch_time = int(time.time())
        if expiration > epoch_time :

            new_amount = amount + payed_amount

            # verify enough ether stored in contract
            balance = await web3.eth.getBalance(contract_add)
            # print("balance :", balance)
            if balance > new_amount :
                
                # verify signature
                valid_sig = await contract_mpc.functions.isValidSignature(new_amount, signature).call()
                print("Is signature of payment valid ?", valid_sig)

                if valid_sig :

                    # if a threshold of balance and time is passed, close the contract
                    balance_limit = balance_threshold * balance
                    time_limit = expiration - time_threshold
                    if new_amount < balance_limit and epoch_time < time_limit :
                        print("Payment threshold not exceeded")

                        # store in MPC DB
                        await store_mpc(collection_MPC, contract_add, signature, new_amount, expiration, remote_host)

                        return True

                    else :
                        print("threshold exceeded")
                        # close the contract
                        nonce = await web3.eth.getTransactionCount(ether_add)  
                        chainId = await web3.eth.chainId
                        
                        transaction = contract_mpc.functions.close(new_amount, signature).buildTransaction({
                            'chainId': chainId,
                            'gas': 70000,
                            'gasPrice': web3.toWei('1', 'gwei'),
                            'nonce': nonce,
                        })
                        signed_txn = web3.eth.account.signTransaction(transaction, private_key=private_key)
                        close = await web3.eth.sendRawTransaction(signed_txn.rawTransaction)

                        print("close :", close)

                        # delete the MPC document
                        await delete_mpc_document(collection_MPC, contract_add)
                        return "error : smart contract closed"

                else :
                    print("signature is not valid")
                    return False

            else :
                print("not enough balance in the smart contract")
                return False

        else :
            print("the smart contract has expired")
            return False
    
    else :
        print("runtimeBytecode does not match")
        return False


async def get_mpc_document(collection_MPC, contract_add) :
    x = {"_id" : contract_add}
    document = await collection_MPC.find_one(x)
    return document


async def delete_mpc_document(collection_MPC, contract_add) :
    x = {"_id" : contract_add}
    await collection_MPC.delete_many(x)


async def store_mpc(collection_MPC, contract_add, signature, new_amount, expiration, remote_host) :
    x = {"_id" : contract_add}
    document = await collection_MPC.find_one(x)
    if document == None :
        # create new document
        data = {"_id" : contract_add, "signature": signature, "amount": new_amount, "expiration": expiration, "host": remote_host}
        result = await collection_MPC.insert_one(data)
    
    else :
        # update document
        data = {"signature": signature, "amount": new_amount, "expiration": expiration}
        await collection_MPC.update_one(x, {'$set': data})
