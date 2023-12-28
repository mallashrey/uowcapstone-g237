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
    python -m venv myvenv
    cd myvenv\Scripts
    activate
    ```

6. Copy these commands below to install dependencies.

    ### For windows
    ```bash
    pip install daphne django-extensions channels tqdm pandas tensorflow transformers
    ```

    ### For Mac
    ```bash
    pip3 install daphne, django-extensions, channels, tqdm, pandas, tensorflow, transformers
    ```

7. Download the ML model for running the questionnaire to determine personality traits

    ```bash
    https://drive.google.com/file/d/1ItgQD1pxvlq2U3rZtsBglQq8C7DTDmYw/view?usp=drive_link
    ```

    ### Once you've downloaded it copy the file and paste at capstone/ml_model/
    

8. Run the Django development server:

   ### For windows
    ```bash
    python manage.py runserver
    ```

    ### For Mac
    ```bash
    python3 manage.py runserver
    ```    


    ### If program can be run on your machine, it will show the command like below:
    ```bash
    Django version 4.1.7, using settings 'uowcapstone.settings'
    Starting ASGI/Daphne version 4.0.0 development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
    ```


9. Access the application at http://localhost:8000.

10. User Password

    ### Manager account
    ```bash
    username: ferry
    password: password
    or
    username: anne
    password: password
    or
    username: shrey
    password: password
    or
    username: musong
    password: password
    or
    username: jenna
    password: password
    ```
    

    ### User account
    ```bash
    username: user
    password: password
    or
    username: user2
    password: password
    or
    username: user3
    password: password
    ```
    


   
   
   
