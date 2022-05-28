# pmz2022

1) Setup the sandbox. Go to the sandbox folder and run

> ./sandbox up

2) Build up the backend. In this folder, run

> docker-compose up --build

Currently you can interact with the backend API this way:

> http://localhost:8501/address_info?address=PUBLICKEY

to get the address infom and 

> http://localhost:8501/create_contract?sender=PUBLICKEY&pool_name=prova&target=10000&startTime=1653775200&endTime=1653948000

To ask that a crowdfounding pool named "prova", having a target to raise 10000 microalgos, with the corresponding _StartTime_ and _endTime_ will be setup by the address _PUBLICKEY_

**Please notice** that in order to make it works, the algorand address asking to build the contract must be founded.
Back to the algorand folder, run
> ./sandbox enter algod

and the 

> goal clerk send -a 100000000 -f 6B2KSSG2ZWW3X3NNONJ4NNFWJXBHGI3K7VUZHISFKUVP2UEXF22QJDF7WY -t PUBLICKEY
