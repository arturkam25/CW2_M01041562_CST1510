# Week 7 - Secure Authentication System 

**Student:** Artur Kamerski  
**Student ID:** M01041562  
**Module:** CST1510 - BSc Cyber Security and Digital Forensics  
**Project:** Week 7 Lab - Secure Login & User Authentication  
**Coursework Part:** Multi-Domain Intelligence Platform - Authentication Module

---

## Project Overview

This project implements a **secure user authentication system** using Python and the `bcrypt` hashing library.  
The goal is to demonstrate key cybersecurity principles, including:

- Secure password storage  
- Password hashing and verification  
- Input validation  
- Basic user management  
- Safe login and registration workflows  

The solution follows the laboratory requirements from Week 7 and forms the basis for the authentication layer in the upcoming Multi-Domain Intelligence Platform (CW2).

---

## Features Implemented

###  Password Hashing  
- Uses `bcrypt.gensalt()` and `bcrypt.hashpw()`  
- Produces a salted, irreversible hash  

###  Password Verification  
- Secure comparison using `bcrypt.checkpw()`  

###  User Registration  
- Validates username (3–20 chars, alphanumeric)  
- Validates password (min. 6 characters)  
- Ensures unique usernames  
- Stores credentials in a safe, consistent format

###  User Login  
- Checks whether user exists  
- Compares hashed passwords  
- Gives clear success and error messages  

###  Validation Layer  
- Username validation  
- Password validation  
- Password confirmation  

###  File-Based User Storage  
All users are stored inside:


