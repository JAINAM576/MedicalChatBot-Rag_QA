import os 
from pathlib import Path
import logging

logging.basicConfig(filename="structure.log",level=logging.INFO,format='[%(asctime)s]: %(message)s : ')

set_of_files=[
"src/__init__.py",
"src/helper.py",
"src/prompt.py",
".env",
"app.py",
"research/trail.ipynb"
]


for filePath in set_of_files:
    filePath=Path(filePath)
    filedir,filename=os.path.split(filePath)
    print(filedir,filename)

    if filedir!="":
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Creating director {filedir} for file {filename}")

    if (not os.path.exists(filePath)) or (not os.path.getsize(filePath)==0):
        with open(filePath,"w") as f:
            logging.info(f"Creating empty file {filename}")
    else :
            logging.info(f"file  {filename} is already exists !")
