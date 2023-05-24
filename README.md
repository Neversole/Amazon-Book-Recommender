# Amazon Book Recommender Engine
-------------------------

This repo contains a group project that was completed during my studies. This project uses Amazon product metadata to produce a graphical user interface that generates book recommendations for a user. The focus of this project is to use co-purchasing history to map the relationship between books and evaluate the connections to make accurate product recommendations. 

-------------------------

# Files
### Data Folder
* amazon-meta.txt - The original dataset used for this project.

### parser.py
This code parses the amazon-meta.txt file to create two csv files, procucts.csv and reviews.csv. These csv files are the datasets that are then uploaded to mongoDB for further use.

### mongoDB_query.py
This code creates our database in mongoDB.

### Amazon_streamlit_app.py
This file contains the code for the Amazon book recommender app.







version https://git-lfs.github.com/spec/v1
oid sha256:8e0b05116b5fcc199827be1e261ce8cabca341605e0df662bfdb86108a10478a
size 25
