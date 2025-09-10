from flask import render_template, request, redirect, url_for, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_db_connection

main_routes = Blueprint('main_routes', __name__)

# Protect routes that require login
def check_logged_in():
    return 'user_logged_in' in session

@main_routes.route('/')
def index():
    if check_logged_in():
        return redirect(url_for('main_routes.dashboard'))
    return render_template('index.html')

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if check_logged_in():
        return redirect(url_for('main_routes.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_logged_in'] = True
            session['user_id'] = user['id']  # Store user ID in session
            return redirect(url_for('main_routes.dashboard'))
        else:
            # Return an error message if login fails
            return "Invalid credentials", 401
        
    return render_template('login.html')

@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            conn.close()
            return "Username already exists", 400
        
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for('main_routes.login'))
    
    return render_template('register.html')

@main_routes.route('/dashboard')
def dashboard():
    if not check_logged_in():
        return redirect(url_for('main_routes.login'))

    user_id = session['user_id']  # Get user ID from the session
    conn = get_db_connection()
    
    # Fetch VPCs associated with the logged-in user
    vpcs = conn.execute('SELECT * FROM vpcs WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    return render_template('dashboard.html', vpcs=vpcs)

@main_routes.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('main_routes.index'))

@main_routes.route('/create_vpc', methods=['GET', 'POST'])
def create_vpc():
    if not check_logged_in():
        return redirect(url_for('main_routes.login'))
    
    if request.method == 'POST':
        vpc_name = request.form['vpcName']
        cidr_block = request.form['cidrBlock']
        user_id = session['user_id']  # Get user ID from session

        # Save VPC to the database
        conn = get_db_connection()
        conn.execute('INSERT INTO vpcs (vpc_name, cidr_block, user_id) VALUES (?, ?, ?)', (vpc_name, cidr_block, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('main_routes.index'))

    return render_template('create_vpc.html')

@main_routes.route('/add_subnet', methods=['GET', 'POST'])
def add_subnet():
    if not check_logged_in():
        return redirect(url_for('main_routes.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        subnet_name = request.form['subnetName']
        subnet_cidr = request.form['subnetCIDR']
        vpc_id = request.form['vpcSelect']  # Make sure vpc_id is selected
        
        # Fetch vpc_name from the VPCs table
        conn = get_db_connection()
        vpc_name = conn.execute('SELECT vpc_name FROM vpcs WHERE id = ?', (vpc_id,)).fetchone()['vpc_name']
        
        # Save Subnet to the database
        conn.execute('INSERT INTO subnets (subnet_name, subnet_cidr, vpc_id, vpc_name, user_id) VALUES (?, ?, ?, ?, ?)', 
                     (subnet_name, subnet_cidr, vpc_id, vpc_name, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('main_routes.index'))

    # Fetch VPCs that belong to the logged-in user
    conn = get_db_connection()
    vpcs = conn.execute('SELECT id, vpc_name FROM vpcs WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return render_template('add_subnet.html', vpcs=vpcs)


@main_routes.route('/view_subnets/<int:vpc_id>')
def view_subnets(vpc_id):
    if not check_logged_in():
        return redirect(url_for('main_routes.login'))

    user_id = session['user_id']
    conn = get_db_connection()

    # Fetch subnets associated with the VPC ID and user
    subnets = conn.execute('SELECT * FROM subnets WHERE vpc_id = ? AND user_id = ?', (vpc_id, user_id)).fetchall()

    # Fetch VPC name for the given VPC ID
    vpc_name = conn.execute('SELECT vpc_name FROM vpcs WHERE id = ?', (vpc_id,)).fetchone()
    vpc_name = vpc_name['vpc_name'] if vpc_name else "Unknown VPC"
    
    conn.close()

    return render_template('view_subnets.html', subnets=subnets, vpc_name=vpc_name)

@main_routes.route('/user_manual')
def user_manual():
    return render_template('user_manual.html')

@main_routes.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')
