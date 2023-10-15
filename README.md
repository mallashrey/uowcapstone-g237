# Capstone Project - Group 237

## Project Overview

JFAMS Alloc is a web app that uses Machine Learning (ML) methodologies to enhance recruitment and role assignment within software development companies by assisting effective candidate sourcing and increasing the accuracy and efficiency of recruitment process based on the personality suitability.

## Specification
Runs on Python 3.11 and HTML5 with dependencies

## Project Setup

Follow these steps to set up the project:

1. Install Python 3.10 or later.

2. Clone the repository:

   ```bash
   git clone https://github.com/susantoferry/uowcapstone-g237.git
   
3. Go to your directory:
   
   ```bash
   cd uowcapstone-g237
   
4. Set up a virtual environment and install dependencies using pipenv:
   
    ### For windows
    ```bash
    pip install virtualenv
    ```

    ### For Mac
    ```bash
    pip3 install virtualenv
    ```   
   
5. Activate the virtual environment:
   
    ```bash
    source myvenv/bin/activate
    ```

6. For installing dependencies:

    ### For windows
    ```bash
    pip install -r requirements.txt
    ```

    ### For Mac
    ```bash
    pip3 install -r requirements.txt
    ```       
   
7. Run the Django development server:

   ### For windows
    ```bash
    python manage.py runserver
    ```

    ### For Mac
    ```bash
    python3 manage.py runserver
    ```    

8. For missing dependencies while trying to run the program. Copy these commands below to install dependencies.

    ### For windows
    ```bash
    pip install daphne
    pip install django-extensions
    pip install channels
    pip install tqdm
    pip install pandas
    pip install tensorflow
    pip install transformers
    ```

    ### For Mac
    ```bash
    pip3 install daphne
    pip3 install django-extensions
    pip3 install channels
    pip3 install tqdm
    pip3 install pandas
    pip3 install tensorflow
    pip3 install transformers
    ```   

9. Try to rerun the program.

    ```bash
    python3 manage.py runserver
    ```

    ### If program can be run on your machine, it will show the command like below:
    ```bash
    Django version 4.1.7, using settings 'uowcapstone.settings'
    Starting ASGI/Daphne version 4.0.0 development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
    ```

10. Access the application at http://localhost:8000.

11. User Password
    username: Ferry
    password: password
   
   
   
