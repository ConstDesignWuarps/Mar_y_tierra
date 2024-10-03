from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# Simulated user data for authentication
users = {
    'miglesia@mx1.ibm.com': 'pass1',
    'user2': 'pass2'
}


@app.route('/')
def index():
    return render_template('../index.html')  # Render your front-end HTML


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if user exists and password matches
    if username in users and users[username] == password:
        return jsonify({'status': 'success', 'message': f'Welcome {username}'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(debug=True)
