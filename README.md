# Welcome to Ochem For Fun
This is a Python project built using [![Pygame](https://img.shields.io/badge/Pygame-v2.5.2-green.svg)](https://www.pygame.org/news) and is a game that generates organic chemistry questions in a quiz-like way. There are three different game modes and a database that can be searched.  
## About This Project
I initially wanted to make an interface that allowed the user to browse a database of organic chemistry molecules, where I would write a code to generate the bond-line structure of each molecule. 
While working on it, the idea of making a game that uses the database came up, which would be a fun tool for people who need more practice for nomenclature-related questions in organic chemistry. 
I decided to use Pygame to design the graphical interface for the game and use a Sqlite3 database to store molecule names, pH's, and their bond-line structure as images.
## INstallation
Step 1: Clone the repo using the following link: https://github.com/CrestyDY/Ochem-For-Fun.git  
Step 2: Install the required dependencies from the [requirements.txt](.idea/Ochem_Survival/requirements.txt) file (ensure you have Python installed). You can use the following command:
```sh
pip install -r requirements.txt
```
Step 3: To initialize the Sqlite3 database, you'll need to run the [Sqlite_table.py](.idea/Ochem_Survival/Games/Sqlite_table.py) file.  
Step 4: Run the [NewGame.py](.idea/Ochem_Survival/Games/NewGame.py) file to run the game.  
## Demonstration
Link to demo: [DEMO](https://youtu.be/Be6dBS28guI)  
## Bugs
High score only updates after you close the program and rerun the NewGame.py file  
## Images
Main Menu:  
![Main Menu](https://cdn.discordapp.com/attachments/875014472912232498/1336140814337839174/image.png?ex=67a2b99a&is=67a1681a&hm=39a0faf68d85eeaf17d1bcddeac0581154a17e62e96be6a07ff3d0c94f7ca921&)  
Questions from Time Trial/ Survival:
![Questions](https://cdn.discordapp.com/attachments/875014472912232498/1336140888115773502/image.png?ex=67a2b9ac&is=67a1682c&hm=85ef404e08c876f15b98f9340a3a6ed51447d7aa96314498eced0ba8abd703b2&)  
Questions from Blind Mode: 
![Questions](https://cdn.discordapp.com/attachments/875014472912232498/1336140962631520388/image.png?ex=67a2b9bd&is=67a1683d&hm=a4fcdc6ca132427f824a22461b7fe8043237db0cae38be0d85b4fc82cf41afea&)  
Database search feature:  
![Database search feature](https://cdn.discordapp.com/attachments/875014472912232498/1336142228074139738/image.png?ex=67a2baeb&is=67a1696b&hm=8aafa3348d5624d56cb75f8b2a2fbd8de523c0657d90dbf214c952bc80a25b5f&)
![Database search feature](https://media.discordapp.net/attachments/875014472912232498/1336141048581324861/image.png?ex=67a2b9d2&is=67a16852&hm=12cb496a42f356eaf776e092875a656c81e4ba7f320b8a0426c8509e7ac97fb8&=&format=webp&quality=lossless&width=1042&height=671)  
![Database search feature](https://cdn.discordapp.com/attachments/875014472912232498/1336141172246184038/image.png?ex=67a2b9ef&is=67a1686f&hm=d0b102a9601c43ac00f6acb55f32d820d74aea1b6123db6a17b95ab83c5ccaf9&)


