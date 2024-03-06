# TODO: protocol sequence + explanation

"""
Rock Paper Scissors:
Since there is no server to make global decisions, The first things the clients do after receiving each other's socket address,
is to "crown" one of them to be the decision maker, using a game similar to Rock Paper Scissors.

-How does the "game" work?
1. Both clients randomly generate a number between 1-3. (1 = rock, 2 = paper, 3 = scissors)
2. They send the number to each other. This is also used to test if the socket address that was given a moment ago by the
Rendezvous Server is correct - The client will terminate connection if it doesn't receive a number.
3. The highest number wins, except 1 defeats 3, since the game is circular.
4. The winner gets to be the decision maker.

-What does decision maker means?
TODO: Explain this
"""
