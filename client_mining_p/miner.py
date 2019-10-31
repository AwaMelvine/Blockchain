import hashlib
import requests

import sys
import json
from uuid import uuid4


def get_id():
    file_name = "my_id.txt"

    try:
        my_id_file = open(file_name, "r")
        return my_id_file.read()
    except:
        new_file = open(file_name, "w")
        node_id = str(uuid4()).replace("-", "")
        new_file.write(node_id)
        new_file.close()
        return node_id


def proof_of_work(block):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    block_string = json.dumps(block, sort_keys=True).encode()

    proof = 0
    while valid_proof(block_string, proof) is False:
        proof += 1
    return proof


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f"{block_string}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    # Change back to 6 zeros
    return guess_hash[:6] == '000000'


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    coins_mined = 0
    proof = 0
    # Run forever until interrupted
    while True:
        response = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = response.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(response)
            break

        # Get the block from `data` and use it to look for a new proof
        # new_proof = ???
        last_block = data["last_block"]

        print("mining...")
        new_proof = proof_of_work(last_block)

        node_id = get_id()

        # When found, POST it to the server {"proof": new_proof, "id": id}
        post_data = {"proof": new_proof, "id": node_id}

        r = requests.post(url=node + "/mine", json=post_data)
        data = r.json()

        # If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if data["message"] == "New block forged":
            coins_mined += 1
            print(data["message"])
            print(f"Coins mined: {coins_mined}")
        else:
            print(data["message"])
