
This is a Python project built using [![Pygame](https://img.shields.io/badge/Pygame-v2.5.2-green.svg)](https://www.pygame.org/news) and is a game that generates organic chemistry questions in a quiz-like way. There are three different game modes and a database that can be searched.  

I initially wanted to make an interface that allowed the user to browse a database of organic chemistry molecules, where I would write a code to generate the bond-line structure of each molecule. 
While working on it, the idea of making a game that uses the database came up, which would be a fun tool for people who need more practice for nomenclature-related questions in organic chemistry. 
I decided to use Pygame to design the graphical interface for the game and use a Sqlite3 database to store molecule names, pH's, and their bond-line structure as images.

Step 1: Clone the repo using the following link: https://github.com/CrestyDY/Ochem-For-Fun.git  
Step 2: Install the required dependencies from the [requirements.txt](.idea/Ochem_Survival/requirements.txt) file (ensure you have Python installed). You can use the following command:
```sh
pip install -r requirements.txt
```
Step 3: To initialize the Sqlite3 database, you'll need to run the [Sqlite_table.py](.idea/Ochem_Survival/Games/Sqlite_table.py) file.  
Step 4: Run the [NewGame.py](.idea/Ochem_Survival/Games/NewGame.py) file to run the game.  

Link to demo: [DEMO](https://youtu.be/Be6dBS28guI)  
