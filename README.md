# Sudoku Solver API (Entry Task)

## Assumed Requirements
* A new user can be registered via `user/register` endpoint, proving a name and a password.
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

## Design considerations
* Framework: `Flask`
	* `Flask` is very lightweight. We do not have a lot of database configurations, and relatively straight forward functionality
	* `Django` would be the second choice, since it is highly configurable, but many of those configurations may be overkill for the task at hand. Therefore, `Flask` was chosen. Django has a great benefit of being highly scalable. Going with `Flask` will not necessarily be a theat to scalability, as the `Flask` app can always be merged with a `Django` project later.
* Database: `SQLite`
	* `Flask` comes with a well-integrated connection to `SQLite`. We would like to have a relationship functionality, therefore NoSQL option might not be sufficient. Since we are having only two tables, storing only `String` and `Integer` types, and have only one relation, `SQLite` might have just the right minimum functionality without using much resources.
* Algorithm for solving the Sudoku:
	* In the work `A study of Sudoku Solving Algorithms.` by Berggren & Nilsson (2012) several Sudoku solving algorithms were compared. Although different algorithms may permorm better under special scenarious (ex. the best-case, or the worst-case), the `backtracking` approach seems to demonstrate the best performance for the average cases. Therefore, this algorithm was selected for the Sudoku solver in this service.
* Authentication: Access Token
    * This method was selected to nurture the "stateless" property of the API. Having an authentication token allows us to bypass a database call when we are authenticating a user, which in result improves the speed. The downside is that token will be good until it expires, opening a vulnerability that it could be stolen from the user in some way and be used for authentication. However, if stateless property is not critical, we can implement blacklisting of tokens, which will allow us to _invalidate_ a token if the user chooses to logout before the expiration time.
* Security:
    * We pass in the API secret key as a system environmental variable to avoid it being stored anywhere.
    * We rely on POST requests as much as possible, since they are not cached by default.

## To run the app
1. Clone the project:<br>
```git clone ...```
2. Change directory into the cloned repository:<br>
```cd ...```
3. Create virtual environment with Python 3:<br>
```python3 -m virtualenv venv```<br>
4. Activate the virtual environment:<br>
```. venv/bin/activate```
5. Install the requirements:<br>
```pip install -r requirements.txt```
6. Set the API secret key as OS environment variable:<br>
```export API_SECRET_KEY=secret```
7. Point to the `Flask` app:<br>
```export FLAST_APP=.```
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
    Extract this token using regular expression:</br>
    ```grep -o '"token":"[^"]*' token.json | grep -o '[^"]*$' > token.txt```
    3. Load the token into the environment variable:
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