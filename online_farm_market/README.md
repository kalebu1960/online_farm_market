Online Farm Market - CLI (Phase 3)

Quick start:

1) Install pipenv if not installed:
   pip install pipenv

2) In project root run:
   pipenv install

3) Enter the shell:
   pipenv shell

4) Initialize DB and seed categories:
   python -m online_farm_market.cli init-db

5) Register a seller:
   python -m online_farm_market.cli register --name "Caleb" --email caleb001@gmail.com --phone 0712345678

6) Login:
   python -m online_farm_market.cli login --email caleb001@gmail.com

7) Add an item (requires two photo file paths):
   python -m online_farm_market.cli add-item --title "Free-range Eggs" --description "Fresh eggs" --price 250 --category "Poultry" --photo1 path/to/photo1.jpg --photo2 path/to/photo2.jpg

8) List items:
   python -m online_farm_market.cli list-items

9) View item:
   python -m online_farm_market.cli view-item --id 1
