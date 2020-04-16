# Sudoku Solver API

## Assumed Requirements
* A new user can be registered via `user/register` path, proving a name and a password.
	* If the name already exists, the system will not create a new user, and return the error message.
* A registered user can login, using `user/login`, and providing the name and the password
* Logged-in users can:
	* solve the sudoku, using `/sudoku` path, and providing a Sudoku as a 2-D JSON Array
	* view history of previously uploaded Sudokus via `/history` path
	* delete it's own user account

## Bonus Features
* Users are divided into `admin` and `non-admin` groups
* Logged-in admins can:
	* delete other users
	* view the history of all users together through `/history_all` path
	* promote or demote other user to `admin` group
	* perform all other functions that `non-admin` users can perform
* Configurations `settings.py` file allows to specify:
	* For how long the user will remain authenticated (i.e. token expiration time)
	* Whether the history of the user should be deleted, when the user is deleted

## To run the app
1. Clone the project:<br>
```git clone https://github.com/alex-ulnv/sudoku_solver_api.git```
2. Change directory into the cloned repository:<br>
```cd sudoku_solver_api```
3. Create virtual environment with Python 3:<br>
```python3 -m virtualenv venv```<br>
4. Activate the virtual environment:<br>
```. venv/bin/activate```
5. Install the requirements:<br>
```pip install -r requirements.txt```
6. Set the API secret key as OS environment variable:<br>
```export API_SECRET_KEY=secret```
7. Point to the `Flask` app:<br>
```export FLASK_APP=.```
8. Run the server:<br>
```flask run```

## Test cases
You can test the API with Postman or with just a Unix `curl` command.
### Using the CURL command (since it is _usually_ included with a Unix system)
#### Simple use case:
1. Register a new user "bee" with the password "12345":<br>
```curl 127.0.0.1:5000/user/register -d '{"name": "bee", "password": "12345"}' -H 'Content-Type: application/json'```
2. Login as a new user:<br>
Note: you will be issued an access token for 30 minutes by default, you can change in the `settings.py` file.<br>
    1. Get the authentication token<br>
    ```curl -X GET 127.0.0.1:5000/user/login --user bee:12345 > token.json```<br>
    2. If successful, the API will return a token that will be stored in `token.json`<br>
    Extract this token using regular expression:<br>
    ```grep -o '"token":"[^"]*' token.json | grep -o '[^"]*$' > token.txt```
    3. Load the token into the environment variable:<br>
    ```export TOKEN=$(cat token.txt)```
3. Using your favorite text editor, create a file that contains a (not-solved) Sudoku as a 2-D JSON array of integers. Creating this file will help us to avoid extra long commands in the shell. Let's call this file `input.json`. For the simplicity of testing, I have already prepared this file with one Sudoku task.<br>
You can view it by running:<br>
```python show_board.py input.json```
4. Send the Sudoku to be solved, using the authentication token:<br>
```curl -vX POST 127.0.0.1:5000/sudoku -d @input.json -H "Content-Type: application/json" -H "x-access-token: ${TOKEN}" > solution.json```
5. Raw JSON result is stored in `solution.json`. Use the script to view it in a readable form:<br>
```python show_board.py solution.json```
6. Optional: send another Sudokus if you wish.
7. Check the history of _your_ Sudokus:<br>
```curl -vX POST 127.0.0.1:5000/history -d @input.json -H "Content-Type: application/json" -H "x-access-token: ${TOKEN}" > history.json```<br>
Use the Python script to format the raw JSON output into a more readable form:<br>
```python show_history.py history.json```
8. Delete the user: (must be the user himself/herself or an admin performing this action)<br>
```curl -X DELETE "Content-Type: application/json" -H "x-access-token: ${TOKEN}" 127.0.0.1:5000/user/delete/bee```
#### Promote/Demote a User & View everybody's history:
1. Create a new user:<br>
```curl 127.0.0.1:5000/user/register -d '{"name": "bee100", "password": "12345"}' -H 'Content-Type: application/json'```
2. Log in as an admin. The default admin account exists with username/password provided below:<br>
    1. ```curl -X GET 127.0.0.1:5000/user/login --user admin:12345 > token.json```<br>
    2. ```grep -o '"token":"[^"]*' token.json | grep -o '[^"]*$' > token.txt```<br>
    3. ```export TOKEN=$(cat token.txt)```
3. Promote the user `bee100`:<br>
```curl -X PUT -H "x-access-token: ${TOKEN}" 127.0.0.1:5000/user/promote/bee100```<br>
4. Demote the user `bee100`:<br>
```curl -X PUT -H "x-access-token: ${TOKEN}" 127.0.0.1:5000/user/demote/bee100```<br>
5. View everybody's history:<br>
    1. ```curl -X POST -H "x-access-token: ${TOKEN}" 127.0.0.1:5000/history_all > history.json```<br>
    2. ```python show_history.py history.json```
