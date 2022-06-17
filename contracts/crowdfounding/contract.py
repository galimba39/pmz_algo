from pyteal import *
from pyteal.ast.bytes import Bytes



def approval():

   
    # App vars
    founder_actor = Bytes("founder")  # byteslice, actor asking for founds
    token_id = Bytes("token_id") 
 
    funding_name = Bytes("funding_name")
    pool_target = Bytes("pool_target")
    start_time_key = Bytes("start")
    end_time_key = Bytes("end")
    pool_status = Bytes("pool_status")


    target_reserve =  Btoi(Txn.application_args[0])
    starttime_founding =  Btoi(Txn.application_args[1])
    endtime_founding =  Btoi(Txn.application_args[2])
    pool_name =  Txn.application_args[3]

    on_create = Seq(

                Assert(

                    And(
                        Txn.application_args.length() == Int(4),   
                        target_reserve > Int(0),
                        Global.latest_timestamp() < starttime_founding,
                        Global.latest_timestamp() < endtime_founding,
                        starttime_founding < endtime_founding,
                        
                    )
                ),

                App.globalPut(founder_actor, Txn.sender()),
                App.globalPut(start_time_key, starttime_founding),
                App.globalPut(end_time_key,endtime_founding),
                App.globalPut(pool_target, target_reserve),
                App.globalPut(funding_name, pool_name),

                Approve()
    )



    on_setup = Seq(
        
        Assert(

            And(
            
                Gtxn[0].type_enum() == TxnType.Payment, # first txn is payment
                Gtxn[1].type_enum() == TxnType.ApplicationCall, # second txn is call
            )

        ),

        Seq(

            InnerTxnBuilder.Begin(),

            InnerTxnBuilder.SetFields({

                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_total: App.globalGet(pool_target),
                TxnField.config_asset_decimals: Int(3),
                TxnField.config_asset_default_frozen: Int(0), 
                TxnField.config_asset_unit_name: Bytes("unit"),
                TxnField.config_asset_name: Itob(Global.latest_timestamp()),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),
                TxnField.fee : Int(0)

                }),


                InnerTxnBuilder.Submit(),

        ),

        App.globalPut(token_id, InnerTxn.created_asset_id()), #assigning new token id to the app
        App.globalPut(pool_status, Bytes("notmet")), # set the pool status
        
        Approve()

    )


    
    asset_data = AssetHolding.balance(Global.current_application_address(), Txn.assets[0])
    frozen_address =  AssetHolding.frozen(Txn.sender(), Txn.assets[0])

    on_donate = Seq(

        asset_data,
        frozen_address,

        Assert(

            And(

                # Checking if the asset exists and its not deployed yet
                asset_data.hasValue(),
                asset_data.value()> Int(0),
 
                # Checking if crowdfounding is still active
                App.globalGet(start_time_key) <= Global.latest_timestamp(),
                Global.latest_timestamp() < App.globalGet(end_time_key),

                # Defining the group transaction structure
                Gtxn[0].type_enum() == TxnType.ApplicationCall, # second txn is call
                Gtxn[1].type_enum() == TxnType.Payment, # payment must follow application call

                Gtxn[1].sender() == Txn.sender(),
                Gtxn[1].receiver() == Global.current_application_address(),
                Gtxn[1].amount() <= asset_data.value()  # DONATION MUST BE THE REMAINING TARGET AMOUNT AT MOST

            )
       
        ),

        Seq(

            If(

                frozen_address.value() == Int(0)

            ).Then(

                Seq(

                    InnerTxnBuilder.Begin(),

                    InnerTxnBuilder.SetFields({
                        TxnField.type_enum: TxnType.AssetTransfer,
                        TxnField.asset_receiver: Txn.sender(),
                        TxnField.asset_amount: Gtxn[1].amount(),
                        TxnField.xfer_asset: App.globalGet(token_id), 
                        TxnField.fee : Int(0)
                    }),

                    InnerTxnBuilder.Next(),
                    
                    InnerTxnBuilder.SetFields({
                        TxnField.type_enum: TxnType.AssetFreeze,
                        TxnField.freeze_asset: Txn.assets[0], 
                        TxnField.freeze_asset_account: Txn.sender(),
                        TxnField.freeze_asset_frozen: Int(1),
                        TxnField.fee : Int(0)
                    }),

                    InnerTxnBuilder.Submit(),
                    
                )
            
            ).Else(

                Seq(

                    InnerTxnBuilder.Begin(),
                    
                    InnerTxnBuilder.SetFields({
                        TxnField.type_enum: TxnType.AssetFreeze,
                        TxnField.freeze_asset: Txn.assets[0], 
                        TxnField.freeze_asset_account: Txn.sender(),
                        TxnField.freeze_asset_frozen: Int(0),
                        TxnField.fee : Int(0)
                    }),

                    InnerTxnBuilder.Next(),

                    InnerTxnBuilder.SetFields({
                        TxnField.type_enum: TxnType.AssetTransfer,
                        TxnField.asset_receiver: Txn.sender(),
                        TxnField.asset_amount: Gtxn[1].amount(),
                        TxnField.xfer_asset: App.globalGet(token_id), 
                        TxnField.fee : Int(0)
                    }),

                    InnerTxnBuilder.Next(),
                    
                    InnerTxnBuilder.SetFields({
                        TxnField.type_enum: TxnType.AssetFreeze,
                        TxnField.freeze_asset: Txn.assets[0], 
                        TxnField.freeze_asset_account: Txn.sender(),
                        TxnField.freeze_asset_frozen: Int(1),
                        TxnField.fee : Int(0)
                    }),

                    InnerTxnBuilder.Submit(),
                    
                )

            ),

            If(

                Gtxn[1].amount() == asset_data.value() # all tokens will be sold in this txn

            ).Then(

                App.globalPut(pool_status, Bytes("met")), # set the pool status

            ),

            Approve()

        )
    
    )


    asset_owner_data = AssetHolding.balance(Txn.sender(), Txn.assets[0])

    end_pool = Seq(

        asset_owner_data,
        asset_data,

        Assert(
            And(
                # Crowdfunding pool is finished
                Global.latest_timestamp() > App.globalGet(end_time_key), 


                # Below two eligible conditions to call the action
                Or(
                    App.globalGet(founder_actor) == Txn.sender(), # Either you are the founder
                    asset_owner_data.value() > Int(0) # Or you own any tokens
                )
            )
            
        ),

        # Successful pool
        If(
            And(

                 # all the tokens have been distributed, i.e. pool was a success
                App.globalGet(pool_status) == Bytes("met")
                
            )
            
        ).Then(

            # If you are the founder
            If(

                App.globalGet(founder_actor) == Txn.sender(), 

            ).Then(

                Seq(

                # Founder is paid (founder can only be paid)
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({

                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: Balance(Global.current_application_address()) - MinBalance(Global.current_application_address()),

                    TxnField.receiver: Txn.sender(),
                    TxnField.fee : Int(0)

                }),
                InnerTxnBuilder.Submit(),
                Approve()
                )
                
            ).Else(

                # Here if it's a donor (it owns token)

                Seq(

                    InnerTxnBuilder.Begin(),
                    InnerTxnBuilder.SetFields({

                        TxnField.type_enum: TxnType.AssetFreeze,
                        TxnField.freeze_asset: Txn.assets[0], 
                        TxnField.freeze_asset_account: Txn.sender(),
                        TxnField.freeze_asset_frozen: Int(0),
                        TxnField.fee : Int(0)

                    }),
                    InnerTxnBuilder.Submit(),
                    Approve(),
                )

            )

        ).Else(

            # If unsuccessful, return the donation
            Seq(

                # Donor is paid back
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({

                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: asset_owner_data.value(),
                    TxnField.receiver: Txn.sender(),
                    TxnField.fee : Int(0)

                }),
                InnerTxnBuilder.Submit(),
                Approve()
            )

        ),

        Approve(),

    )


    program = Cond(

        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp,
            Cond(
                [Txn.application_args[0] == Bytes("setup"), on_setup],
                [Txn.application_args[0] == Bytes("donate"), on_donate],
                [Txn.application_args[0] == Bytes("end_pool"), end_pool]

            )
        ],
        [Txn.on_completion() == OnComplete.DeleteApplication, Reject()],
        [Txn.on_completion() == OnComplete.UpdateApplication, Reject()],
        [Txn.on_completion() == OnComplete.ClearState, Reject()],
        [Txn.on_completion() == OnComplete.CloseOut, Reject()],
        [Txn.on_completion() == OnComplete.OptIn, Reject()],


    )

    return program

def clear():
    return Approve()

if __name__ == "__main__":
    with open("build/auction_approval.teal", "w") as f:
        compiled = compileTeal(approval(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("build/auction_clear_state.teal", "w") as f:
        compiled = compileTeal(clear(), mode=Mode.Application, version=5)
        f.write(compiled)
