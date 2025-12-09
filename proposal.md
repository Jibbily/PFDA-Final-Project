# Python Game - Liar's Dice

# Repository:
https://github.com/Jibbily/PFDA-Final-Project.git

## Description

In this project I will create a game in python that involves players taking turns at bidding the number of dice in play, or calling the previous player's bid as a lie.
They will do this by answering simple (bid) or (challenge) prompts in the terminal on their turn.

## Features

Each player will have their set of digital dice and so a class will need to be made for each one.
The actions players can take will use simple input functions, and the prompts for those actions will print directions beforehand.
While loops will be used to control the state of the game including player turns, which players still have dice in turn granting them the ability to keep playing, and the current bid amount which controls the minimum bid the next player can place.

### Challenges

Control of the game state is a section I might have difficulty with. Since the bid uses 2 types of number values which dictate what counts as the minimum by placing their digits adjacent to one another, I will need to create an If function that properly allows and denies certain bids.

### Outcomes

The ideal outcome is for the game tobe functional from start to finish. Even if it is confusing to use, as long as it successfully works then that expectation is met. Printing directions on how to play the game shouldn't be difficult, so making the game easy to use is my secondary expectation.

### Milestones

Create main function, and necessary code that tracks "game pieces" such as players
Create code that tracks dice state and updates amount
Create gameplay loop of players placing their bids or calling challenges
Add print directions to clearly prompt input, and add hidden mechanic to only display player info for the current player only
