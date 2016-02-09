from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

def main():
	conn = MongoClient('mongodb://127.0.0.1:27017')
	db = conn.test
	user = input("Enter your username: ")
	password = input("Enter your password: ")
	email = input("Enter your email: ")
	if db.users.find({"username": user}).count() == 0:	
		pass_hash = generate_password_hash(password, method='pbkdf2:sha256')
		db.users.insert({"username": user, "password": pass_hash, "email": email})
		print ("User created.")
	else:
		print ("User already present in DB.")

if __name__ == '__main__':
	main()
