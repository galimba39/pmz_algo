from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful.utils import cors
import json
import csv
import hashlib
from algosdk.v2client import algod
from contracts import contract , utils
from algosdk import encoding, future

from sqlalchemy import create_engine


app = Flask(__name__)
api = Api(app)
api.decorators=[cors.crossdomain(origin='*')]


algod_address = "http://host.docker.internal:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)

POSTGRES_USER = 'user'
POSTGRES_PASSWORD = 'password'
POSTGRES_DB = 'database'
service = 'db'
service_port = '5432'






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
        db_string = 'postgresql://{}:{}@{}:{}/{}'.format(POSTGRES_USER, POSTGRES_PASSWORD, service, service_port, POSTGRES_DB)
        self.db = create_engine(db_string)

        
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

        # Insert data in DB
        
        insert_data_string = "INSERT INTO crowdfounding_contracts (founder, pool_name, target, startTime, endTime, create_tx_id, app_id) " +\
                   "VALUES ('" + str(sender) + "','" + str(pool_name)[0:64] + "'," + str(target) +\
                            "," + str(startTime) + "," + str(endTime) + ",'" + str(contract_create_txn.get_txid()) + "',-1);"
                           
        self.db.execute(insert_data_string)

        # Return the encoded transaction

        return encoding.msgpack_encode(contract_create_txn)
        



class sign_contract(Resource):

    """
        Usage_example:
        http://localhost:8501/sign_contract?contract_txn=gqNzaWfEQEMv1HImtBJ3WoSMrMQ3bwIQqPtOpaepbBqPsiR1cLqoIE85uOEFnOzX2n7DrOQsbBOKKjLxK42hSE/ht1a2GAKjdHhui6RhcGFhlMQIAAAAAAAAE4jECAAAAABimOlXxAgAAAAAYpo6zcQKcHJvdmFfcG0zeqRhcGFwxQIkBiAGAQAFBAYDJgQIdG9rZW5faWQFc3RhcnQDZW5kC3Bvb2xfdGFyZ2V0MRgjEkABmjEZIxJAAAEANhoAgAVzZXR1cBJAAUM2GgCABmRvbmF0ZRJAAAEAMgo2MABwADUBNQAxADYwAHABNQM1AjQBNAAjDRApZDIHDhAyBypkDBAzABAhBBIQMwEQIhIQMwEAMQASEDMBBzIKEhAzAQgyAA8QRDMBCDQADkAAfzQCIxJAAEWxJLIQNjAAsi0xALIuI7IvtiKyEDMBCDQACbIIMQCyB7YlshAxALIUNACyEihkshG2JLIQNjAAsi0xALIuIrIvsyJDIkOxIrIQMwEINAAJsggxALIHtiWyEDEAshQ0ALISKGSyEbYkshA2MACyLTEAsi4isi+zIkM0AiMSQAA0sSSyEDYwALItMQCyLiOyL7YlshAxALIUMwEIshIoZLIRtiSyEDYwALItMQCyLiKyL7MiQ7ElshAxALIUMwEIshIoZLIRtiSyEDYwALItMQCyLiKyL7MiQzMAECISMwEQIQQSEESxIQWyECtksiIhBbIjI7IkgAR1bml0siUyBxayJjIKsikyCrIqMgqyKzIKsiyzKLQ8ZyJDMRslEjYaABcjDRAyBzYaARcMEDIHNhoCFwwQNhoBFzYaAhcMEESAB2ZvdW5kZXIxAGcpNhoBF2cqNhoCF2crNhoAF2eADWZvdW5kaW5nX25hbWU2GgNnIkOkYXBnc4KjbmJzAqNudWkEpGFwc3XEBAaBAUOjZmVlzQPoomZ2zR0So2dlbqpzYW5kbmV0LXYxomdoxCAAovdNZJR7ZhhICbsDRxklR55VCfDpzUWEoZc2sIw9N6Jsds0g+qNzbmTEIHmvO4ztnPm09cuE9ZG+m81iwHCu/JC34cLImy06CJKOpHR5cGWkYXBwbA==

    """


    def __init__(self):

        self.algod_client = algod_client
        
        db_string = 'postgresql://{}:{}@{}:{}/{}'.format(POSTGRES_USER, POSTGRES_PASSWORD, service, service_port, POSTGRES_DB)
        self.db = create_engine(db_string)
        
        
    def get(self):
    
        input_items = dict(request.args.items())
        contract_txn = input_items.get("contract_txn", None) # contract transaction to sign
        contract_txn_decoded = encoding.future_msgpack_decode(contract_txn)
        
        # check presence 
        
        check_result_cur = self.db.execute("SELECT COUNT(*) FROM crowdfounding_contracts WHERE RTRIM(create_tx_id,' ')='"  + str(contract_txn_decoded.get_txid()) + "'")
        check_result = [r[0] for r in check_result_cur]
        
        # E controlliamo che l'app id sia nel nostro db
        if ((isinstance(contract_txn_decoded, future.transaction.SignedTransaction)) & 
            (check_result[0]>0)):
        
            # If correct transaction type, return appid 
            
            txid = self.algod_client.send_transaction(contract_txn_decoded)
            application_id = utils.return_application_id(txid, self.algod_client)
            
            # Update db data
            
            self.db.execute("UPDATE crowdfounding_contracts SET app_id =" + str(application_id) + \
                            "WHERE RTRIM(create_tx_id,' ')='"  + str(contract_txn_decoded.get_txid()) + "'")
            
            # Return data
                        
            return {"application_id": application_id}
            
        else:
         
            return {"application_id": None}
            


class get_all_contracts(Resource):

    """
        Not limiting get may lead to too big results
        Example: http://localhost:8501/get_all_contracts
    """

    def __init__(self):

        self.algod_client = algod_client
        
        db_string = 'postgresql://{}:{}@{}:{}/{}'.format(POSTGRES_USER, POSTGRES_PASSWORD, service, service_port, POSTGRES_DB)
        self.db = create_engine(db_string)
        
        
    def get(self):
    
        contract_data_result = self.db.execute("SELECT * FROM crowdfounding_contracts where app_id >0")
        return [dict(r) for r in contract_data_result]





api.add_resource(address_info, '/address_info')
api.add_resource(create_contract, '/create_contract')
api.add_resource(get_all_contracts, '/get_all_contracts')
api.add_resource(sign_contract, '/sign_contract')


if __name__ == '__main__':
    
    
    from waitress import serve
    serve(app, host="0.0.0.0", port=8501)
