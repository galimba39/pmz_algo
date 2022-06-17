from datetime import datetime, timedelta
from algosdk import future, encoding, logic
from base64 import b64decode
import json
import base64
import random
import requests
from functools import partial
from algosdk.constants import MIN_TXN_FEE


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
    
    future.transaction.wait_for_confirmation(client, send_tx_step, 4)
#    inspect_transaction(send_tx_step, client)
    
    
    
    
def setup_transaction(founder_address, pool_app_id, client) -> list:

    """
        This step create tokens as a mean of participation to the pool.
    """

    params = client.suggested_params()
    params.fee = 2 * MIN_TXN_FEE
    params.flat_fee = True

    fundAppTxn = future.transaction.PaymentTxn(
            sender = founder_address,
            receiver = logic.get_application_address(pool_app_id),
            amt = 200000, 
            sp = client.suggested_params(),
        )

    setupTxn = future.transaction.ApplicationNoOpTxn(
            sender = founder_address,
            index=pool_app_id,
            app_args=[b"setup"],
            sp= params
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
        

def get_latest_token(client, app_id):

    
    return client.account_info(logic.get_application_address(app_id))['created-assets'][-1]["index"]


def asset_optin(founder_object, client, asset_id):

    optin_txn = asset_optin_txn(client, founder_object.getAddress(), asset_id)
    optintxn_signed = optin_txn.sign(founder_object.getPrivateKey())
    txid = client.send_transaction(optintxn_signed)
    future.transaction.wait_for_confirmation(client, txid,4)



def asset_optin_txn(client,address,asset_id):

    """
        Source: https://developer.algorand.org/docs/get-details/asa/#receiving-an-asset
        Papabile backend
    """

    # OPT-IN

    account_info = client.account_info(address)
    check_asset_presence = any([asset['asset-id']==asset_id for asset in account_info['assets']])

    if check_asset_presence:

        return None

    else:

        # Return asset optin transaction to sign
        txn_to_sign = future.transaction.AssetTransferTxn(
            sender=address,
            sp=client.suggested_params(),
            receiver=address,
            amt=0,
            index=asset_id)

        return txn_to_sign
        
        
        

def donate_action(client,
                  donor,
                  app_id,
                  amount,
                  asset_id):

    partecipation_amount = amount
    
    params = client.suggested_params()
    params.fee = 5 * MIN_TXN_FEE
    params.flat_fee = True

    donateTxn = future.transaction.ApplicationNoOpTxn(
            sender = donor,
            index=app_id,
            app_args=[b"donate"],
            foreign_assets=[asset_id], # si legge dall'applicazione
            sp= params
    )

    donationamtTxn = future.transaction.PaymentTxn(
            sender = donor,
            receiver = logic.get_application_address(app_id),
            amt = partecipation_amount,
            sp = params#client.suggested_params(),
        )


    future.transaction.assign_group_id([donateTxn, donationamtTxn])

    return [donateTxn, donationamtTxn]
    

def end_pool_txn(address_object, app_id, client):
    
    
    params = client.suggested_params()
    params.fee = 3 * MIN_TXN_FEE
    params.flat_fee = True
    
    asset_id = get_latest_token(client, app_id)
        
    claim_txn = future.transaction.ApplicationNoOpTxn(
            sender = address_object.getAddress(),
            index = app_id,
            app_args = [b"end_pool"],
            foreign_assets=[asset_id],
            sp = params
    )

    signed_claim = claim_txn.sign(address_object.getPrivateKey())

    txid = client.send_transaction(signed_claim)

    future.transaction.wait_for_confirmation(client, txid,4)
    
    return asset_id


claim_token = partial(end_pool_txn)
claim_funds = partial(end_pool_txn)

