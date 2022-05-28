from flask import Flask, request
from flask_restful import Resource, Api
import json
import csv
import hashlib
from algosdk.v2client import algod
from contracts import contract , utils
from algosdk import encoding



app = Flask(__name__)
api = Api(app)


algod_address = "http://host.docker.internal:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)


class address_info(Resource):

    """
        Usage_example:
        http://localhost:8501/address_info?address=ZAYO44VBDTUUZVIVCUZ5YOHPC5R4K2TRRDLGHHZ5QLBTSGQXVR72CGTBWI
    
    """
    
    def __init__(self):

        self.algod_client = algod_client


        
        
    def get(self):
        
        input_items = dict(request.args.items())
		
        address_data = input_items.get("address", None)

        return self.algod_client.account_info(address_data)



class create_contract(Resource):

    """
        Usage_example:
        http://localhost:8501/create_contract?sender=ZAYO44VBDTUUZVIVCUZ5YOHPC5R4K2TRRDLGHHZ5QLBTSGQXVR72CGTBWI&pool_name=prova&target=10000&startTime=1653775200&endTime=1653948000
    
    """

    def __init__(self):

        self.algod_client = algod_client

        
    def get(self):
        
        input_items = dict(request.args.items())


        # Need to insert assert for the inputs	

        sender = input_items.get("sender", None) # sender that need to sign the transaction later on
        pool_name = input_items.get("pool_name", None) # name we want to assign to algorand client
        target = int(input_items.get("target", None)) # how much we want to raise 
        startTime = int(input_items.get("startTime", None)) # crowd founding start time
        endTime = int(input_items.get("endTime", None)) # crowd founding end time

        # Contract creation
        contract_create_txn = utils.createCrowdFoundindTxt(self.algod_client,
                                                           sender,
                                                           pool_name,
                                                           target,
                                                           startTime,
                                                           endTime)

        # Return the encoded transaction
        return encoding.msgpack_encode(contract_create_txn)


api.add_resource(address_info, '/address_info')
api.add_resource(create_contract, '/create_contract')


if __name__ == '__main__':
	
    
	from waitress import serve
	serve(app, host="0.0.0.0", port=8501)
