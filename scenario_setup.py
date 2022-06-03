from contracts.external_utils.auction_demo.testing import resources
from algosdk import future, encoding, logic
from algosdk.v2client import algod
import requests
from algosdk.constants import MIN_TXN_FEE
from contracts.crowdfounding import scenario_utils



def setup_env():


    # Algo client

    algod_address = "http://host.docker.internal:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    founder1 = resources.getTemporaryAccount(algod_client)
    founder2 = resources.getTemporaryAccount(algod_client)
    founder3 = resources.getTemporaryAccount(algod_client)
    
    
    # First address creates a crowdfounding pool
    
    pool_create_txn1 = scenario_utils.create_pool(founder1, 1440, 12300000) # 12300000 microAlgo pool
    pool_create_txn1_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn1).sign(founder1.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn1_signed_encoded}
    application_id1 = requests.get('http://contract:8501/sign_contract', params=query).json()
    
    scenario_utils.setup_pool(founder1, application_id1["application_id"], algod_client)
    
    
    # Second address creates a small crowdfounding pool
    
    pool_create_txn2 = scenario_utils.create_pool(founder2, 1440, 1000) # 1000 microAlgo pool
    pool_create_txn2_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn2).sign(founder2.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn2_signed_encoded}
    application_id2 = requests.get('http://contract:8501/sign_contract', params=query).json()
    
    scenario_utils.setup_pool(founder2, application_id2["application_id"], algod_client)
    
    
    # Third address creates a short lasting pool
    
    pool_create_txn3 = scenario_utils.create_pool(founder3, 3, 10000000) # 12300000 microAlgo pool
    pool_create_txn3_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn3).sign(founder3.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn3_signed_encoded}
    application_id3 =  requests.get('http://contract:8501/sign_contract', params=query).json()
    
    scenario_utils.setup_pool(founder3, application_id3["application_id"], algod_client)


    print("Founder 1, " + founder1.getAddress() + " created pool: " + str(application_id1["application_id"]))
    print("Founder 2, " + founder2.getAddress() + " created pool: " + str(application_id2["application_id"]))
    print("Founder 3, " + founder3.getAddress() + " created pool: " + str(application_id3["application_id"]))
    

setup_env()