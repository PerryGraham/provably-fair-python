# Implementation of Provably fair in python
Provably fair is a handshake process used in modern gambling applications to ensure fairness to the user. The concept is that the user can provide a seed that is used to generate the bet outcome. Randomness is ensured by a server seed to make sure the client cannot cheat. The hashed server seed is provided to the client before their bet is placed, meaning the client is able to *control the randomness* of the result. 

### Setup
I'm using windows powershell:   
`python -m venv venv`   
`Set-ExecutionPolicy Unrestricted -Scope Process`   
`.\venv\Scripts\Activate.ps1`   
`pip instal -r requirements.txt`

### Start API
`uvicorn main:app --reload`

Go to http://127.0.0.1:8000/docs

## How *provably fair* works

![](https://i.ibb.co/R4KLGBd/provably-drawio.png)

Context: In this example I am using a coin flip as the betting event. The user can bet on heads or tails. 

The result of the coin flip is calculated using a **game seed**. The game seed is made up of 3 things: the server seed, client seed and nonce. The purpose of a nonce is to allow the system to use the same server and client seed for multiple bets by incrementing the nonce each time. This saves the system from having to regenerate seeds each time. 

**Step one:** Upon client connection, the server generates a server seed and stores it for later. The client is given the SHA512 hash of the server seed. This serves as proof that the server seed was generated before the bet was placed. A client is able to request a new server seed as they please. 

**Step 2:** The client places their bet on heads or tails, along with this bet they include the client seed, which is a string of whatever they please. The server then combines the client seed, server seed and nonce to calculate the result of the coin flip.

**Step 3:** The server responds to the bet request with the coin flip outcome, the unhashed server seed, and nonce. The client now has all the information required to calculate that the hashed server seed that was given to them before their bet was placed was used (in combination with the client seed they provided) to produce outcome that the server provided. Note that the **verification function needs to be implemented client side** as an API endpoint implementation (used in this repo) does not ensure fairness. 


