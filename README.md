Microservice Login and Authentication

This repository contains a microservice built with FastAPI for user registration, authentication, and password reset functionalities. The microservice leverages modern Python technologies like Pydantic, SQLAlchemy, and JSON Web Tokens (JWT) to provide secure and robust authentication mechanisms.
Features

* User Registration: Allows users to create accounts with unique credentials.

* User Authentication: Verifies user identity using secure authentication methods.

* Password Reset: Enables users to securely reset their passwords.

* Token-based Authentication: Uses JSON Web Tokens (JWT) to authenticate and authorize users for accessing protected resources.

* Session Management: Manages user sessions securely to ensure continuous access to the microservice.


<b>Technologies Used<b>

FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
Pydantic: Data validation and settings management using Python type annotations.
SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
JWT (JSON Web Tokens): A compact, URL-safe means of representing claims to be transferred between two parties securely.

<b> Setup </b>

* Clone the Repository 
* git clone https://github.com/sudarshan-uprety/microservice-login-authentication.git


* Install Dependencies
* pip install -r requirements.txt


* create an env (example provided)


* Run the Application
* uvicorn app.main:app --reload