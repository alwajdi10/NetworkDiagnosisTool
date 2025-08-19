import os
import sqlite3
import uuid
import time
import socket
import subprocess
import re
import psutil
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, jsonify
import network_scanner
import report_generator

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'network.db'

def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            mac_address TEXT,
            ip_address TEXT,
            connection_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Activity log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            title TEXT,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Network performance table
    c.execute('''
        CREATE TABLE IF NOT EXISTS network_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bandwidth_mbps REAL,
            latency_ms REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_user_network_info():
    try:
        # Get real MAC address
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                        for elements in range(0, 6*8, 8)][::-1])
        
        # Get real IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        
        return mac, ip
    except:
        return "00:00:00:00:00:00", "127.0.0.1"

def log_activity(user_id, activity_type, title, description):
    conn = get_db()
    conn.execute('''
        INSERT INTO activity_log (user_id, type, title, description)
        VALUES (?, ?, ?, ?)
    ''', (user_id, activity_type, title, description))
    conn.commit()
    conn.close()

def store_performance_data(user_id, bandwidth, latency):
    conn = get_db()
    conn.execute('''
        INSERT INTO network_performance (user_id, bandwidth_mbps, latency_ms)
        VALUES (?, ?, ?)
    ''', (user_id, bandwidth, latency))
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        return redirect('/logout')
    
    # Calculate real connection time
    connection_start = datetime.strptime(user['connection_start'], '%Y-%m-%d %H:%M:%S')
    connection_minutes = int((datetime.now() - connection_start).total_seconds() / 60)
    
    # Get real network devices
    devices = network_scanner.scan_network()
    
    # Get real performance data from database
    performance_records = conn.execute('''
        SELECT bandwidth_mbps, latency_ms, timestamp 
        FROM network_performance 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''', (session['user_id'],)).fetchall()
    
    # If no performance data exists, collect some
    if not performance_records:
        bandwidth, latency = network_scanner.get_real_performance()
        store_performance_data(session['user_id'], bandwidth, latency)
        performance_records = conn.execute('''
            SELECT bandwidth_mbps, latency_ms, timestamp 
            FROM network_performance 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''', (session['user_id'],)).fetchall()
    
    # Prepare performance data for charts
    performance_data = {
        'bandwidth': [record['bandwidth_mbps'] for record in reversed(performance_records)],
        'latency': [record['latency_ms'] for record in reversed(performance_records)],
        'timestamps': [datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M') 
                      for record in reversed(performance_records)]
    }
    
    # Get recent activities
    activities = conn.execute('''
        SELECT * FROM activity_log 
        WHERE user_id = ?
        ORDER BY timestamp DESC 
        LIMIT 10
    ''', (session['user_id'],)).fetchall()
    
    # Add initial activity if none exist
    if not activities:
        log_activity(session['user_id'], 'connected', 'Connexion initiale', 'Session démarrée avec succès')
        activities = conn.execute('''
            SELECT * FROM activity_log 
            WHERE user_id = ?
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                           user=user,
                           connection_time=connection_minutes,
                           devices=devices,
                           activities=activities,
                           performance_data=performance_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        
        if user:
            session['user_id'] = user['id']
            # Update connection start time
            conn.execute('UPDATE users SET connection_start = CURRENT_TIMESTAMP WHERE id = ?', 
                        (user['id'],))
            conn.commit()
            log_activity(user['id'], 'connected', 'Connexion réussie', 'Utilisateur connecté au système')
            conn.close()
            return redirect('/')
        else:
            conn.close()
            return render_template('login.html', error="Identifiants invalides")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form.get('name', username)
        
        mac, ip = get_user_network_info()
        
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, name, mac_address, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, name, mac, ip))
            user_id = cursor.lastrowid
            
            conn.commit()
            session['user_id'] = user_id
            log_activity(user_id, 'connected', 'Compte créé', 'Nouveau compte enregistré avec succès')
            return redirect('/')
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Nom d'utilisateur déjà utilisé")
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], 'disconnected', 'Déconnexion', 'Utilisateur déconnecté du système')
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/refresh_network')
def refresh_network():
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    # Scan real network
    devices = network_scanner.scan_network()
    
    # Get real performance data
    bandwidth, latency = network_scanner.get_real_performance()
    store_performance_data(session['user_id'], bandwidth, latency)
    
    log_activity(session['user_id'], 'scan', 'Scan réseau', f'Réseau scanné - {len(devices)} appareils détectés')
    
    return jsonify({'devices': devices, 'bandwidth': bandwidth, 'latency': latency})

@app.route('/generate_report')
def generate_report():
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Get real network data
    devices = network_scanner.scan_network()  # ✅ Your existing function
    
    # Get performance history
    performance_records = conn.execute('''
        SELECT AVG(bandwidth_mbps) as avg_bandwidth, AVG(latency_ms) as avg_latency
        FROM network_performance 
        WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    
    # Generate report with real data - ✅ Now works perfectly!
    report_content = report_generator.generate_report(user, devices, performance_records)
    
    log_activity(session['user_id'], 'report', 'Rapport généré', 'Rapport de diagnostic créé avec données temps réel')
    conn.close()
    
    return jsonify({'report_content': report_content})

@app.route('/api/performance_data')
def get_performance_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Non authentifié'}), 401
    
    # Get real-time performance
    bandwidth, latency = network_scanner.get_real_performance()
    store_performance_data(session['user_id'], bandwidth, latency)
    
    return jsonify({
        'bandwidth': bandwidth,
        'latency': latency,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })

def background_monitoring():
    """Background thread for continuous monitoring"""
    while True:
        time.sleep(60)  # Update every minute
        # This would run performance monitoring in background
        # For now, we'll update when requested

if __name__ == '__main__':
    init_db()
    # Start background monitoring thread
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5000)