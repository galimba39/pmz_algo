from datetime import datetime, timedelta
from algosdk import future, encoding, logic
from base64 import b64decode
import json
import base64
import random
import requests



def inspect_transaction(txid, algod_client):

    try:
        confirmed_txn = future.transaction.wait_for_confirmation(algod_client, txid, 4)

        print("Transaction information: {}".format(
            json.dumps(confirmed_txn, indent=4)))
        print("Decoded note: {}".format(base64.b64decode(
            confirmed_txn["txn"]["txn"]["note"]).decode()))
        
        return confirmed_txn

    except Exception as err:
        print(err)

        return None
        


        
def return_application_id(txid, algod_client):

    

    try:
        confirmed_txn = future.transaction.wait_for_confirmation(algod_client, txid, 4)
        return confirmed_txn["application-index"]

    except Exception as err:
        print(err)

        return None
        
        

        
def sign_multiple_transactions(list_of_transaction, private_key, client)-> None:

    """
    
    """
    
    signed_list = [txn.sign(private_key) for txn in list_of_transaction]
    
    send_tx_step = client.send_transactions(signed_list)
    inspect_transaction(send_tx_step, client)
    
    
    
    
def setup_transaction(founder_address, pool_app_id, client) -> list:

    """
        This step create tokens as a mean of participation to the pool.
    """

    fundAppTxn = future.transaction.PaymentTxn(
            sender = founder_address,
            receiver = logic.get_application_address(pool_app_id),
            amt = 500000,
            sp = client.suggested_params(),
        )

    setupTxn = future.transaction.ApplicationNoOpTxn(
            sender = founder_address,
            index=pool_app_id,
            app_args=[b"setup"],
            sp=client.suggested_params()
    )

    future.transaction.assign_group_id([fundAppTxn, setupTxn])

    return [fundAppTxn, setupTxn]
    
    
    
def create_pool(address_object, end_delta_minutes, target):


    startTime = int(datetime.timestamp(datetime.now() + timedelta(seconds=5)))
    endTime = int(datetime.timestamp(datetime.now() + timedelta(minutes=end_delta_minutes)))
    pool_name = "pool_founder" + str(random.randint(0, 10000000))
    target = target # microAlgo

    query = {"sender": address_object.getAddress(), "pool_name":pool_name, "target":target, "startTime": startTime, "endTime":endTime}
    txt_to_sign_encoded = requests.get('http://contract:8501/create_contract', params=query).json()
    
    return txt_to_sign_encoded



def setup_pool(founder_object, pool_app_id, client):

    
    # Create setup transaction
    
    setup_txn_list = setup_transaction(founder_object.getAddress(), pool_app_id, client)
    
    try:
    
        sign_multiple_transactions(setup_txn_list, founder_object.getPrivateKey(), client)
        
    except:
    
        print("Unsuccessful pool setup")