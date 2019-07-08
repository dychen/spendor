# Splendor
Training an AI over the board game Splendor (original, not the expansions)
https://en.wikipedia.org/wiki/Splendor_(game)

# Playing
```
$ python game.py

[Long printout of game state]

>> Move? [0/1/2/3] [data]:
# Possible moves:

# Take three gems
>> t3 [5-element array of the number of gems to take of each color in the order: W,U,G,R,B]
# E.g.
>> t3 1 1 1 0 0 # Takes one white, one blue, and one green gem. Takes zero red or black gems.
>> t3 0 1 0 1 1 # Takes one blue, one red, and one black gem.
>> t3 1 0 0 0 1 # Takes one white and one black gem - do this if taking more puts you over the stack limit.

# Take two gems
>> t2 [5-element array of the number of gems to take - should always have one 2 and four 0s]
# E.g.
>> t2 0 0 2 0 0 # Takes two green gems.
>> t2 0 0 0 2 0 # Takes two red gems.
# Remember that you cannot take two if the corresponding gem stack is below 4.
# If you want to take only 1 gem, use t3 ("take 3") instead (e.g. t3 1 0 0 0 0).

# Reserve a card
>> r [tier - 1, 2, or 3] [index - 0, 1, 2, or 3]
# These are zero-indexed, so 0 is the first card, 1 is the second, etc.
# E.g.
>> r 1 0 # Reserve the first card in Tier 1
>> r 2 1 # Reserve the second card in Tier 2
>> r 3 3 # Reserve the last card in Tier 3

# Buy a card
>> b [tier - 1, 2, or 3] [index - 0, 1, 2, or 3] [buy from reserve - 1 if YES, 0 if NO]
# Again, these are zero-indexed
# E.g.
>> b 1 0 0 # Buy the first card in Tier 1
>> b 1 0 1 # Buy the first card in your reserve (the first 1 for tier is ignored)
>> b 3 2 0 # Buy the third card in Tier 3
>> b 0 1 1 # Buy the second card in your reserve (index - 1, buy from reserve - 1/YES)
>> b 0 1 0 # INVALID - can't buy from Tier 0 (tier - 0, index - 1, buy from reserve - 0/NO)
```

# Board state
```
=====NEW STATE=====
=TIER 1= # Tier 1 dev cards
[Card 1]
[Card 2]
[Card 3]
[Card 4]
=TIER 2= # Tier 2 dev cards
[Card 1]
[Card 2]
[Card 3]
[Card 4]
=TIER 3= # Tier 3 dev cards
[Card 1]
[Card 2]
[Card 3]
[Card 4]
=GEMS=
[Number of each gem on the board in the following order: White, Blue, Green, Red, Black]
# ^ This gem order is used in all places that use a gem array (e.g. card cost)
=PLAYER [i]= # For each player
  POINTS: [Number of victory points for each player - max of 15]
  NORM GEMS: [Number of each gem the player has in order: W,U,G,R,B] AND [Player gold count]
  CARD GEMS: [Number of gems the player has from cards in order: W,U,G,R,B]
  TOTL GEMS: [Effective total gems the player has from gems + cards] AND [Player gold count]
    CARD: [Card the player owns]
    ...
    RESERVED: [Card the player has reserved]
    ...
========END========
```

# Cards
Read card state (7-element array) as follows:
```
[White cost, Blue cost, Green cost, Red cost, Black cost, Gem bonus color (always +1), Points/prestige]
```

# Rules questions (unresolved)?
* Can you reserve a card if the gold stack is depleted? Currently, it throws an error
