import datetime
import hashlib
import json
from flask import Flask, jsonify
import requests
from uuid import uuid4
from urllib.parse import urlparse



# Armando el blockchain

class Blockchain:
    def __init__(self):
        self.chain = []     
        self.transactions = [] 
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
        
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.node.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f"http://{node}/get_chein")
            if response.status_code == 200:
                length = response.json(['length'])
                chain = response.json(['chain'])

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
            if longest_chain:
                self.chain = longest_chain
                return True

            return False
        
        
    def create_block(self, proof, previous_hash): # esta funcion debe definir el nuevo bloque minado 
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = [] 
        self.chain.append(block)
        return block
    
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.appen({'sender':sender,
                                 'receiver':receiver,
                                 'amount': amount})
        
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    
    
    
    def get_previous_block(self):
        return self.chain[-1]  # para optener el ultimo bloque de la cadena 
    
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False: 
            # iteraremos hasta encontrar el proof que resuelva 
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] == '0000':     #si los 4 primeros indices son 0000
                check_proof = True
                
            else:
                new_proof += 1
                
            return new_proof 
        
        
        
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
        
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            new_proof = block['proof']
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
        return True
    
    
    
# 2  - Minando el blockchain

# creando web app
app = Flask(__name__)

# creando una direccion para el nodo en el puerto 5000
node_address = str(uuid4()).replace('-','')    #crea direccion unica aleatoria 


blockchain = Blockchain()

# minando un nuevo bloque

@app.route('/mine_block', methods=['GET'])

def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender= node_address, receiver= 'Raul', amount= 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Felicidades, haz minado un bloque!!!',
                'index': block['index'], 
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200


# Obteniendo cadena completa

@app.route('/get_chain', methods=['GET'])

def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200



# chequendo validez de la cadena de bloques 
@app.route('/is_valid', methods=['GET'])

def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Todo bien, El blockchain es valido'}
    else:
        response = {'message': 'Tenemos un problema, El blockcahin no es valido'}
         
    return jsonify(response), 200

        
 
        
# Agregando nueva transaccion al blockchain
@app.route('/add_transaction', methods=['POST'])

def add_transaction():
    json = requests.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return "Algun elemento de la transaccion esta faltando", 401
    
 
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message':f"La transaccion sera añadida al bloque {index}"}
    return jsonify(response), 201
    
    
 
# 3 - Desentralizando el blockchain

# conectando nuevos nodos 
@app.route('/connect_node', methods=['POST'])

def connect_node():
    json = requests.get_json()
    nodes = json.get('nodes')
    if nodes in None:
        return "No node", 401
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Todos los nodos estan ahora conectados. proofcoin Blockchain contiene los siguientes nodos: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# remplazando la cadena por la mas larga    
@app.route('/replace_chain', methods=['GET'])

def replace_chain():
    is_chain_replace = blockchain.replace_chain()
    if is_chain_replace:
        
        response = {'message': 'La cadena fue remplazada por la mas larga',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'La cadena es la mas larga',
                    'actual_chain':blockchain.chain}
         
    return jsonify(response), 200        
    
 
    
 
    
 
    
 
    
 
    
 
    
# corriendo  APP
app.run(host='0.0.0.0', port='5000')
































