Markdown
# Spare Parts Inventory Manager

## About This Project
I created this desktop application to understand how software development, databases, and user interfaces work together. It is an inventory management tool built with Python. To make the project realistic and practical, the application features an "Auto-Seeding" mechanism: upon its first launch, if no database is found, it automatically creates a local database and populates it with authentic Leibinger spare parts, inspired by the printing industry my family is familiar with.

## A Note on Transparency (How I Built This)
I am currently at the beginning of my programming journey, actively learning and preparing for an IT Ausbildung in Germany. I want to be completely honest about my development process: I did not write every single line of this code from scratch by myself. 

I designed the project concept, decided on the features, and planned the database logic. Then, I used AI as a pair programmer and mentor to help me write, structure, and debug the actual Python code. This project taught me how to read code, how Tkinter and SQLite work together, how to implement database auto-seeding, and how to use AI effectively as a problem-solving tool.

## Features
* Auto-Seeding Database: Automatically generates and populates inventory.db with real-world data on the first run.
* Barcode Scanner Simulation: A quick-scan input that instantly reduces stock by 1 when a Part ID is entered.
* Database Management: Full ability to add, update, rename, and delete spare parts.
* Local Database: Uses SQLite for lightweight, serverless data storage.
* Professional UI: A clean user interface built with Tkinter and ttk.

## Tech Stack
* Python 3
* Tkinter (GUI)
* SQLite3 (Database)
* PyInstaller (Used to package the project into a standalone .exe)

## Project Files
* main.py: The single core application file containing the interface, database logic, and auto-seeding script.

## Developer
Derin Rodoslu
