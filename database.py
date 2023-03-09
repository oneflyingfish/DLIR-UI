import json,os
import streamlit as st

def ReadUsersDatabase():
    with open("datas/users.json", "r") as f:
        usersDatabase = json.load(f)
        if "users" not in usersDatabase:
            usersDatabase["users"]={}
        if "models" not in usersDatabase:
            usersDatabase["models"]={}
        if "system_path" not in usersDatabase or len(usersDatabase["system_path"])<1:
            usersDatabase["system_path"]=os.getcwd()
    return usersDatabase

def WriteUsersDatabase(usersDatabase):
    with open("datas/users.json", "w") as f:
        json.dump(usersDatabase, f,indent=4)