from contracts.external_utils.auction_demo.testing import resources
from datetime import datetime, timedelta
from algosdk import future, encoding, logic
from algosdk.v2client import algod
import random
import requests


def return_application_id(txid, algod_client):

    import json
    import base64

    try:
        confirmed_txn = future.transaction.wait_for_confirmation(algod_client, txid, 4)
        return confirmed_txn["application-index"]

    except Exception as err:
        print(err)

        return None


def create_fake_pool(address_object, end_delta_minutes, target):


    """
    
    """

    startTime = int(datetime.timestamp(datetime.now() + timedelta(seconds=5)))
    endTime = int(datetime.timestamp(datetime.now() + timedelta(minutes=end_delta_minutes)))
    pool_name = "pool_founder" + str(random.randint(0, 10000000))
    target = target # microAlgo

    query = {"sender": address_object.getAddress(), "pool_name":pool_name, "target":target, "startTime": startTime, "endTime":endTime}
    txt_to_sign_encoded = requests.get('http://contract:8501/create_contract', params=query).json()
    
    return txt_to_sign_encoded



def setup_env():


    # Algo client

    algod_address = "http://host.docker.internal:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    founder1 = resources.getTemporaryAccount(algod_client)
    founder2 = resources.getTemporaryAccount(algod_client)
    founder3 = resources.getTemporaryAccount(algod_client)
    
    
    # First address creates a crowdfounding pool
    
    pool_create_txn1 = create_fake_pool(founder1, 1440, 12300000) # 12300000 microAlgo pool
    pool_create_txn1_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn1).sign(founder1.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn1_signed_encoded}
    application_id1 = requests.get('http://contract:8501/sign_contract', params=query).json()

    
    # Second address creates a small crowdfounding pool
    
    pool_create_txn2_ts = create_fake_pool(founder2, 1440, 1000) #1000 microAlgo pool
    pool_create_txn2_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn2_ts).sign(founder2.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn2_signed_encoded}
    application_id2 = requests.get('http://contract:8501/sign_contract', params=query).json()

    # Third address creates a short lasting pool
    
    pool_create_txn3_ts = create_fake_pool(founder3, 3, 10000000) # 10000000 microAlgo pool
    pool_create_txn3_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn3_ts).sign(founder3.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn3_signed_encoded}
    application_id3 = requests.get('http://contract:8501/sign_contract', params=query).json()

    print("Founder 1, " + founder1.getAddress() + " created pool: " + str(application_id1["application_id"]))
    print("Founder 2, " + founder2.getAddress() + " created pool: " + str(application_id2["application_id"]))
    print("Founder 3, " + founder3.getAddress() + " created pool: " + str(application_id3["application_id"]))
    

    
setup_env()