from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import json
from flask import abort
from flask import make_response
from flask import g
import sqlite3

app = Flask(__name__)

DATABASE = 'database/database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
	
# Run before every request
@app.before_request
def before_request():
    g.db = get_db()

# Run after every request
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
		
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)
	
# Get list of all students
@app.route('/students/list', methods = ['GET'])
def get_all_students():
	query = 'SELECT * FROM students'
	cur = g.db.execute(query)
	list_students = cur.fetchall()
	list = { "list_students" :[dict(id = row[0], name = row[1], phone = row[4], email = row[5]) for row in list_students]}
	return jsonify(list)

# Get a student by id
@app.route('/students/search/<int:student_id>', methods = ['GET'])
def get_a_student(student_id):
	query = 'SELECT * FROM students WHERE id = ?'
	cur = g.db.execute(query, (student_id,))
	query_result = cur.fetchone()
	if query_result is None:
		return jsonify({'message': 'Student does not exist'})
	student = {"id" : query_result[0], "name" : query_result[1], "phone" : query_result[4], "email" : query_result[5]}
	return jsonify(student)
	
# Add a new student
@app.route('/students/add', methods = ['POST'])
def add_student():
	new_student = {
        'name': request.json['name'],
        'phone': request.json['phone'],
        'email': request.json['email'],
    	'user_created': request.json['user_created']
	}
	query = 'INSERT INTO students(name, phone, email, user_created) values (?,?,?,?)'
	cur = g.db.execute(query, (new_student['name'], new_student['email'], new_student['phone'], new_student['user_created']))
	g.db.commit()
	return jsonify({'message': 'Successfully add new student'})

# Update a student record by id
@app.route('/students/update/<int:student_id>', methods = ['PUT'])
def put_students(student_id):
	query = 'SELECT * FROM students WHERE id = ?'
	update_student = {
		'column' : request.json['column'],
		'value' : request.json['value']
	}
	cur = g.db.execute(query, (student_id,))
	query_result = cur.fetchone()
	if query_result is None:
		return jsonify({'message': 'Student does not exist'})
	query_update = 'UPDATE students SET ' + update_student['column'] + '= ? WHERE id = ?'
	g.db.execute(query_update, (update_student['value'],student_id,))
	g.db.commit()
	return jsonify({'message': 'Successfully update'})
	
# Delete a student record by id
@app.route('/students/delete/<int:student_id>', methods = ['DELETE'])
def delete_students(student_id):
	query = 'SELECT * FROM students WHERE id = ?'
	cur = g.db.execute(query, (student_id,))
	query_result = cur.fetchone()
	if query_result is None:
		return jsonify({'message': 'Student does not exist'})
	query_delete = 'DELETE FROM students WHERE id = ?'
	g.db.execute(query_delete, (student_id,))
	g.db.commit()
	return jsonify({'message': 'Successfully delete'})
	
@app.route('/teachers', methods=['GET'])
def get_teachers():
	return 'Return GET teachers'
	
@app.route('/teachers', methods=['POST'])
def post_teachers():
	return 'Return POST teachers'

@app.route('/teachers', methods=['PUT'])
def put_teachers():
	return 'Return PUT teachers'
	
@app.route('/teachers', methods=['DELETE'])
def delete_teachers():
	return 'Return DELETE teachers'
	
# /users/get/
@app.route('/users/get/email=<email>@<host>&password=<password>', methods=['GET'])
def get_users(email, host, password):
    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    query = "select * from users where email = ? and password = ?"
    email = email + '@' + host
    c.execute(query, (email, password))
    record = c.fetchone()
    if record is None:
        non_exist_return = 'Khong ton tai user'  #
        return non_exist_return
    user_return = jsonify(
        {"id": record[0], "username": record[1], "password": record[3], "email": record[2], "phone": record[4]})  #
    return user_return


# /users/add/
@app.route('/users/add/username=<name>&email=<email>@<host>&password=<password>&phone=<phone>', methods=['POST', 'GET'])
def post_users(name, email, password, phone, host):
    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    email = email + '@' + host
    query = "insert into users (name,email,password,phone) values (?,?,?,?)"
    try:
        c.execute(query, (name, email, password, phone))
    except sqlite3.Error:
        return 'Error'
    conn.commit()
    conn.close()
    return 'Success Add'


# /users/update/
# url for update email
@app.route('/users/update/email=<email>@<host0>&password=<password>&<column>=<value>@<host>', methods=['PUT', 'GET'])
# url for update name,phone , password
@app.route('/users/update/email=<email>@<host0>&password=<password>&<column>=<value>', methods=['PUT', 'GET'])
def put_users(email, host0, password, column, value, host=None):
    if column == 'id':
        return
    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    query = "select * from users where email = ? and password = ?"
    email = email + '@' + host0
    c.execute(query, (email, password))
    record = c.fetchone()
    if record is None:
        wrong_return = "Wrong Identity Or Non Exist"  #
        return wrong_return
    else:
        if host is not None:
            value = value + '@' + host
        update_query = "update users set {0} = ? where email = ? and password = ?".format(column)
        try:
            c.execute(update_query, (value, email, password))
            conn.commit()
        except sqlite3.Error:
            error_return = 'Error'  #
            return error_return

    success_return = 'Success Update'  #
    return success_return


# /users/delete/
@app.route('/users/delete/email=<email>@<host>&password=<password>', methods=['DELETE', 'GET'])
def delete_users(email, host, password):
    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    delete_query = "delete from users where email = ? and password = ?"
    email = email + '@' + host
    c.execute(delete_query, (email, password))
    conn.commit()

    return 'Success Del'

if __name__ == '__main__':
	app.run(debug=True)