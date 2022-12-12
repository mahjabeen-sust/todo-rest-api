## ToDo Rest API  with Python Flask and PostgreSQL

## Introduction
This project builds a backend for a personal TODO application that requires users to be logged in before they can call the APIs. One user can create multiple todo items and one todo item can only belong to a single user. The data model of a todo item & user is as follows:

**Todo**:

- Id: Unique identifier
- Name: Name of the todo item
- Description (optional): Description of the toto item
- User id: Id of the user who owns this todo item
- Created timestamp: When the item is created
- Updated timestamp: When the item is last updated
- Status: An enum of either: NotStarted, OnGoing, Completed

**User**:

- Id: Unique identifier
- Email: Email address
- Password: Hash of the password
- Created timestamp: When the user is created
- Updated timestamp: When the user is last updated

### **Core features**

This backend application exposes a set of REST APIs for the following endpoints:

- **POST** */api/v1/signup*: Sign up as an user of the system, using email & password
- **POST** */api/v1/signin*: Sign in using email & password. The system will return the JWT token that can be used to call the APIs that follow
- **PUT** */api/v1/changePassword*: Change user’s password
- **GET** */api/v1/todos?status=[status]*: Get a list of todo items. Optionally, a status query param can be included to return only items of specific status. If not present, return all items
- **POST** */api/v1/todos*: Create a new todo item
- **PUT** */api/v1/todos/:id*: Update a todo item
- **DELETE** */api/v1/todos/:id*: Delete a todo item

## Project Setup
You need to install the dependecies for the project like Flask, JWT for Pyhton.

### Cloning the git repo
The code for this project is located on github at the following URL 
[todo-rest-api](https://github.com/mahjabeen-sust/todo-rest-api)

In order to clone it into your project, you can simply type the following command from the folder where you would like to install the project.

`git clone https://github.com/mahjabeen-sust/todo-rest-api`

### Postgres DB Setup

In this project we will be using a Postgres Database. For convenience, we have created a database and provided the url. If you create your own database, you can run the following SQL for creating the tables required for this project.

We need to create a table for the users
```
CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email TEXT NOT NULL UNIQUE,
                                        password TEXT NOT NULL, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                                        update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
```


For the status column of the todo table, we need to create a ENUM type. Run the following SQL to do that.
```
CREATE TYPE status AS ENUM ('NotStarted', 'OnGoing', 'Completed');
```

Then create the todo table.
```
CREATE TABLE IF NOT EXISTS todo (id SERIAL PRIMARY KEY, name TEXT, description TEXT DEFAULT NULL,
                                        user_id INTEGER, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                                        update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status status,
                                        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
```

Once you have your database created, we will get started with the application.

## The Application

Flask is a micro framework for python that makes it possible to create websites and APIs very rapidly.  We're going to use flask as our authentication API's RESTful interface.  The entry point to the application is named app.py and this will serve as the flask web service.

### To install flask and associated dependencies.

Here is the command-line method to install the dependencies for this project.  We're going to use flask, psycopg2 for postgres, pyjwt for the JWT, and python-dotenv to handle environment variables. We have stored the list of the depencied in the requirements.txt file. Run the following command:
```
pip install -r requirements.txt
```

### Using python-dotenv for easy environment variable management
One of our imports in the program is python-dotenv.  This creates a way to pull in environment variables at runtime using a .env file found in the project folder.  This allows for easy management of our variables.  If you run this app in a container, you could set up your docker run command to include the necessary env vars for your environment, as long as the following variables are set.

We created sample.env as a template.  To run this, set the variables to the appropriate values for your database server and choose a phrase for your authentication hash secret and then change the name of the file to .env, or just set these variables in your environment.  Linux is case-sensitive, remember!
```
DATABASE_URL=[database url]
AUTHSECRET=[secret for the JWT]
EXPIRESSECONDS=3000 
```

At this point, if you have everything set up and you ran the application, it should run on port 5000.  Remember to turn off debug mode in production!

In order to run this from the command line just type...

**python app.py**