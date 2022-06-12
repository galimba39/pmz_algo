### Contract interaction

Crowdfunding pool smart contracts permit 4 interactions:

- A contract generation step, stating the hard cap target amount in microAlgos, its start and end time and the contract name. On top of these, funder creator, the token id and the pool status are tracked as global variables.

- A setup phase is involved to fund the app with its minimum algo amount and in this phase the contract creates its token as well.

- The donation step organizes donor and pool interactions such as exchanging tokens for donated algos, freezing them and eventually handling same donor multiple donations.

- End pool phase offers solution both to 
	- the donors which can either unfreeze their tokens or withdrawing their original funds, according to the crowdfunding outcome and 
	- the entrepreneur who can withdraw the raised funds.