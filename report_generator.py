import datetime
import logging
import sqlite3
from typing import Dict, List, Optional, Any
import network_scanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_report(user, devices, performance_data=None):
    """
    Generate a professional network diagnostic report
    
    Args:
        user: SQLite Row object with user data (from database)
        devices: List of device dictionaries from network_scanner.scan_network()
        performance_data: SQLite Row object with avg_bandwidth and avg_latency
    
    Returns:
        str: Complete HTML report
    """
    try:
        logger.info(f"Generating report for user: {user['name'] if user else 'Unknown'}")
        
        # Extract user information safely
        user_info = extract_user_info(user)
        
        # Process devices data
        devices_data = process_devices_data(devices)
        
        # Get real-time network performance
        current_performance = get_current_performance(performance_data)
        
        # Get network infrastructure data
        infrastructure = get_infrastructure_data()
        
        # Analyze network state and generate recommendations
        analysis = analyze_network_state(devices_data, current_performance, infrastructure)
        
        # Generate HTML report
        html_report = generate_html_report(user_info, devices_data, current_performance, infrastructure, analysis)
        
        logger.info("Report generated successfully")
        return html_report
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return generate_error_report(str(e))

def extract_user_info(user):
    """Extract and format user information from database row"""
    if not user:
        return {
            'name': 'Unknown User',
            'username': 'unknown',
            'ip_address': '0.0.0.0',
            'mac_address': '00:00:00:00:00:00',
            'connection_start': 'Unknown',
            'connection_duration': 0
        }
    
    try:
        # Calculate connection duration
        if user['connection_start']:
            connection_start = datetime.datetime.strptime(user['connection_start'], '%Y-%m-%d %H:%M:%S')
            duration_minutes = int((datetime.datetime.now() - connection_start).total_seconds() / 60)
        else:
            duration_minutes = 0
            
        return {
            'name': user['name'] or user['username'],
            'username': user['username'],
            'ip_address': user['ip_address'] or '0.0.0.0',
            'mac_address': user['mac_address'] or '00:00:00:00:00:00',
            'connection_start': user['connection_start'] or 'Unknown',
            'connection_duration': duration_minutes
        }
    except Exception as e:
        logger.error(f"Error extracting user info: {e}")
        return {
            'name': 'User Data Error',
            'username': 'error',
            'ip_address': '0.0.0.0',
            'mac_address': '00:00:00:00:00:00',
            'connection_start': 'Unknown',
            'connection_duration': 0
        }

def process_devices_data(devices):
    """Process and validate devices data from network scanner"""
    if not devices:
        return []
    
    processed_devices = []
    for device in devices:
        try:
            processed_device = {
                'id': device.get('id', 0),
                'name': device.get('name', f"Device-{device.get('ip', 'Unknown').split('.')[-1]}"),
                'ip': device.get('ip', '0.0.0.0'),
                'mac': device.get('mac', 'Unknown'),
                'type': device.get('type', 'unknown'),
                'status': device.get('status', 'unknown'),
                'signal': max(0, min(100, device.get('signal', 0)))  # Ensure signal is 0-100
            }
            processed_devices.append(processed_device)
        except Exception as e:
            logger.warning(f"Error processing device {device}: {e}")
            continue
    
    return processed_devices

def get_current_performance(performance_data):
    """Get current network performance metrics"""
    try:
        # Get real-time performance from network scanner
        current_bandwidth, current_latency = network_scanner.get_real_performance()
        
        # Use database averages if available, otherwise use current values
        if performance_data:
            avg_bandwidth = performance_data.get('avg_bandwidth') or current_bandwidth
            avg_latency = performance_data.get('avg_latency') or current_latency
        else:
            avg_bandwidth = current_bandwidth
            avg_latency = current_latency
        
        return {
            'current_bandwidth': current_bandwidth,
            'avg_bandwidth': avg_bandwidth,
            'current_latency': current_latency,
            'avg_latency': avg_latency,
            'measurement_time': datetime.datetime.now().strftime('%H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        return {
            'current_bandwidth': 0,
            'avg_bandwidth': 0,
            'current_latency': 999,
            'avg_latency': 999,
            'measurement_time': datetime.datetime.now().strftime('%H:%M:%S')
        }

def get_infrastructure_data():
    """Get network infrastructure information"""
    try:
        return {
            'network_range': network_scanner.get_network_range(),
            'gateway_ip': network_scanner.get_gateway_ip(),
            'local_ip': network_scanner.get_local_ip(),
            'interfaces': network_scanner.get_network_interfaces(),
            'local_mac': network_scanner.get_local_mac()
        }
    except Exception as e:
        logger.error(f"Error getting infrastructure data: {e}")
        return {
            'network_range': '192.168.1',
            'gateway_ip': '192.168.1.1',
            'local_ip': '192.168.1.100',
            'interfaces': [],
            'local_mac': '00:00:00:00:00:00'
        }

def analyze_network_state(devices, performance, infrastructure):
    """Analyze network state and generate insights"""
    analysis = {
        'total_devices': len(devices),
        'online_devices': len([d for d in devices if d['status'] == 'online']),
        'offline_devices': len([d for d in devices if d['status'] == 'offline']),
        'issues_found': [],
        'recommendations': [],
        'security_alerts': [],
        'performance_score': 0,
        'performance_grade': 'C',
        'overall_health': 'fair'
    }
    
    try:
        # Analyze device connectivity
        offline_devices = [d for d in devices if d['status'] == 'offline']
        if offline_devices:
            analysis['issues_found'].append(f"{len(offline_devices)} appareils hors ligne")
            offline_names = [d['name'] for d in offline_devices[:3]]
            analysis['recommendations'].append(f"🔴 Vérifier la connectivité: {', '.join(offline_names)}")
        
        # Analyze signal strength
        online_devices = [d for d in devices if d['status'] == 'online']
        if online_devices:
            avg_signal = sum(d['signal'] for d in online_devices) / len(online_devices)
            if avg_signal < 70:
                analysis['issues_found'].append("Signal WiFi faible")
                analysis['recommendations'].append("📶 Améliorer le positionnement du routeur")
        else:
            avg_signal = 0
        
        # Analyze performance
        bandwidth = performance['avg_bandwidth']
        latency = performance['avg_latency']
        
        if bandwidth < 10:
            analysis['issues_found'].append("Bande passante insuffisante")
            analysis['recommendations'].append("🌐 Contacter le fournisseur d'accès internet")
        
        if latency > 100:
            analysis['issues_found'].append("Latence réseau élevée")
            analysis['recommendations'].append("⚡ Optimiser la configuration réseau")
        
        # Check for weak signal devices
        weak_devices = [d for d in online_devices if d['signal'] < 50]
        if weak_devices:
            weak_names = [d['name'] for d in weak_devices[:2]]
            analysis['recommendations'].append(f"📡 Signal faible: {', '.join(weak_names)} - rapprocher du routeur")
        
        # Security analysis
        unknown_devices = [d for d in devices if d['type'] == 'unknown']
        if len(unknown_devices) > 3:
            analysis['security_alerts'].append(f"{len(unknown_devices)} appareils non identifiés")
            analysis['recommendations'].append("🔒 Vérifier les appareils non autorisés")
        
        # Calculate performance score
        score = calculate_performance_score(bandwidth, latency, avg_signal, analysis['online_devices'], analysis['total_devices'])
        analysis['performance_score'] = score
        analysis['performance_grade'] = get_performance_grade(score)
        
        # Determine overall health
        if len(analysis['issues_found']) == 0:
            analysis['overall_health'] = 'excellent'
            analysis['recommendations'].append("✅ Le réseau fonctionne de manière optimale")
        elif bandwidth < 5 or latency > 200 or analysis['online_devices'] == 0:
            analysis['overall_health'] = 'poor'
        elif len(analysis['issues_found']) > 3:
            analysis['overall_health'] = 'fair'
        else:
            analysis['overall_health'] = 'good'
            
    except Exception as e:
        logger.error(f"Error during network analysis: {e}")
        analysis['issues_found'].append("Erreur lors de l'analyse")
    
    return analysis

def calculate_performance_score(bandwidth, latency, signal, online_devices, total_devices):
    """Calculate overall performance score (0-100)"""
    score = 0
    
    # Bandwidth score (40% weight)
    if bandwidth >= 50:
        score += 40
    elif bandwidth >= 25:
        score += 30
    elif bandwidth >= 10:
        score += 20
    else:
        score += 10
    
    # Latency score (30% weight)
    if latency <= 20:
        score += 30
    elif latency <= 50:
        score += 25
    elif latency <= 100:
        score += 15
    else:
        score += 5
    
    # Signal score (20% weight)
    if signal >= 80:
        score += 20
    elif signal >= 60:
        score += 15
    elif signal >= 40:
        score += 10
    else:
        score += 5
    
    # Connectivity score (10% weight)
    if total_devices > 0:
        connectivity_ratio = online_devices / total_devices
        if connectivity_ratio >= 0.9:
            score += 10
        elif connectivity_ratio >= 0.7:
            score += 8
        elif connectivity_ratio >= 0.5:
            score += 5
        else:
            score += 2
    
    return min(100, max(0, score))

def get_performance_grade(score):
    """Convert score to letter grade"""
    if score >= 85:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 55:
        return 'C'
    else:
        return 'D'

def get_device_icon(device_type):
    """Get emoji icon for device type"""
    icons = {
        'router': '🌐',
        'server': '🖥️',
        'desktop': '💻',
        'laptop': '💻',
        'phone': '📱',
        'printer': '🖨️',
        'camera': '📹',
        'unknown': '❓'
    }
    return icons.get(device_type, '❓')

def get_device_type_name(device_type):
    """Get French name for device type"""
    names = {
        'router': 'Routeur',
        'server': 'Serveur',
        'desktop': 'Ordinateur de bureau',
        'laptop': 'Ordinateur portable',
        'phone': 'Téléphone',
        'printer': 'Imprimante',
        'camera': 'Caméra',
        'unknown': 'Inconnu'
    }
    return names.get(device_type, 'Inconnu')

def generate_html_report(user_info, devices, performance, infrastructure, analysis):
    """Generate the complete HTML report"""
    
    # Get current timestamp
    report_time = datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    current_year = datetime.datetime.now().year
    
    # Calculate network statistics
    total_devices = analysis['total_devices']
    online_devices = analysis['online_devices']
    offline_devices = analysis['offline_devices']
    
    # Generate device cards HTML
    device_cards_html = ""
    for device in devices:
        status_class = 'online' if device['status'] == 'online' else 'offline'
        device_cards_html += f"""
        <div class="device-card {status_class}">
            <div class="device-icon">{get_device_icon(device['type'])}</div>
            <div class="device-name">{device['name']}</div>
            <div class="device-ip">{device['ip']}</div>
            <div class="device-signal">Signal: {device['signal']}%</div>
        </div>
        """
    
    # Generate device table HTML
    device_table_html = ""
    for device in devices:
        signal = device['signal']
        signal_color = '#28a745' if signal > 70 else '#ffc107' if signal > 40 else '#dc3545'
        status_class = 'online' if device['status'] == 'online' else 'offline'
        
        device_table_html += f"""
        <tr>
            <td><strong>{device['name']}</strong></td>
            <td>{get_device_type_name(device['type'])}</td>
            <td><code>{device['ip']}</code></td>
            <td><code>{device['mac']}</code></td>
            <td class="status-{status_class}">
                {"🟢 En ligne" if device['status'] == "online" else "🔴 Hors ligne"}
            </td>
            <td>
                <div class="signal-display">
                    {signal}%
                    <div class="signal-bar">
                        <div class="signal-fill" style="width: {signal}%; background-color: {signal_color};"></div>
                    </div>
                </div>
            </td>
        </tr>
        """
    
    # Generate interfaces HTML
    interfaces_html = ""
    if infrastructure['interfaces']:
        interface_rows = ""
        for interface in infrastructure['interfaces']:
            status_class = 'online' if interface.get('status') == 'up' else 'offline'
            interface_rows += f"""
            <tr>
                <td><strong>{interface.get('name', 'Unknown')}</strong></td>
                <td><code>{interface.get('ip', 'N/A')}</code></td>
                <td><code>{interface.get('netmask', 'N/A')}</code></td>
                <td class="status-{status_class}">
                    {"🟢 Actif" if interface.get('status') == 'up' else "🔴 Inactif"}
                </td>
                <td>{interface.get('speed', 'N/A')} Mbps</td>
            </tr>
            """
        
        interfaces_html = f"""
        <div class="section">
            <h2><span class="icon">🔧</span>Interfaces Réseau</h2>
            <table>
                <thead>
                    <tr>
                        <th>Interface</th>
                        <th>Adresse IP</th>
                        <th>Masque</th>
                        <th>Statut</th>
                        <th>Vitesse</th>
                    </tr>
                </thead>
                <tbody>
                    {interface_rows}
                </tbody>
            </table>
        </div>
        """
    
    # Generate recommendations HTML
    recommendations_html = ""
    for rec in analysis['recommendations']:
        css_class = "error" if "🔴" in rec else "warning" if "⚠️" in rec or "📶" in rec or "⚡" in rec else ""
        recommendations_html += f'<li class="recommendation-item {css_class}">{rec}</li>'
    
    # Generate issues HTML
    issues_html = ""
    if analysis['issues_found']:
        issues_list = "".join([f'<li class="issue-item">{issue}</li>' for issue in analysis['issues_found']])
        issues_html = f'<ul class="issues-list">{issues_list}</ul>'
    else:
        issues_html = '<p class="no-issues">✅ Aucun problème critique détecté</p>'
    
    # Generate security alerts HTML
    security_html = ""
    if analysis['security_alerts']:
        security_list = "".join([f'<li class="security-item">{alert}</li>' for alert in analysis['security_alerts']])
        security_html = f"""
        <div class="section">
            <h2><span class="icon">🔒</span>Alertes de Sécurité</h2>
            <ul class="security-list">{security_list}</ul>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Réseau - {user_info['name']}</title>
    <style>
        {get_report_css()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rapport de Diagnostic Réseau</h1>
            <div class="subtitle">
                Généré le {report_time}<br>
                Analyse du réseau de {user_info['name']}
            </div>
        </div>
        
        <div class="content">
            <!-- Performance Grade -->
            <div class="performance-grade grade-{analysis['performance_grade']}">
                <div class="grade-icon">🏆</div>
                <div class="grade-info">
                    <h2>Note Globale: {analysis['performance_grade']}</h2>
                    <p>Score: {analysis['performance_score']}/100 • État: {analysis['overall_health'].title()}</p>
                </div>
            </div>
            
            <!-- User Information -->
            <div class="section">
                <h2><span class="icon">👤</span>Informations Utilisateur</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Nom:</span>
                        <span class="info-value">{user_info['name']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Nom d'utilisateur:</span>
                        <span class="info-value">{user_info['username']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Adresse IP:</span>
                        <span class="info-value">{user_info['ip_address']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Adresse MAC:</span>
                        <span class="info-value">{user_info['mac_address']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Connexion depuis:</span>
                        <span class="info-value">{user_info['connection_start']}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Durée de session:</span>
                        <span class="info-value">{user_info['connection_duration']} minutes</span>
                    </div>
                </div>
            </div>
            
            <!-- Network Statistics -->
            <div class="section">
                <h2><span class="icon">📈</span>Statistiques Réseau</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">🌐</div>
                        <div class="stat-info">
                            <div class="stat-value">{performance['avg_bandwidth']:.1f} Mbps</div>
                            <div class="stat-label">Bande Passante</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-info">
                            <div class="stat-value">{performance['avg_latency']:.0f} ms</div>
                            <div class="stat-label">Latence</div>
                        </div>
                    </div>
                    <div class="stat-card {'success' if online_devices == total_devices else 'warning' if online_devices > 0 else 'error'}">
                        <div class="stat-icon">📱</div>
                        <div class="stat-info">
                            <div class="stat-value">{online_devices}/{total_devices}</div>
                            <div class="stat-label">Appareils En Ligne</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔗</div>
                        <div class="stat-info">
                            <div class="stat-value">{infrastructure['network_range']}.0/24</div>
                            <div class="stat-label">Réseau</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Device Map -->
            <div class="section">
                <h2><span class="icon">🗺️</span>Cartographie des Appareils</h2>
                <div class="device-map">
                    {device_cards_html}
                </div>
            </div>
            
            <!-- Device Details Table -->
            <div class="section">
                <h2><span class="icon">📋</span>Détails des Appareils</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Nom</th>
                                <th>Type</th>
                                <th>IP</th>
                                <th>MAC</th>
                                <th>Statut</th>
                                <th>Signal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {device_table_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            {interfaces_html}
            
            <!-- Issues Found -->
            <div class="section">
                <h2><span class="icon">⚠️</span>Problèmes Détectés</h2>
                {issues_html}
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <h2><span class="icon">💡</span>Recommandations</h2>
                <ul class="recommendations-list">
                    {recommendations_html}
                </ul>
            </div>
            
            {security_html}
            
            <!-- Infrastructure Summary -->
            <div class="section">
                <h2><span class="icon">🏗️</span>Infrastructure Réseau</h2>
                <div class="infrastructure-grid">
                    <div class="infra-item">
                        <span class="infra-label">Passerelle:</span>
                        <span class="infra-value">{infrastructure['gateway_ip']}</span>
                    </div>
                    <div class="infra-item">
                        <span class="infra-label">Plage réseau:</span>
                        <span class="infra-value">{infrastructure['network_range']}.0/24</span>
                    </div>
                    <div class="infra-item">
                        <span class="infra-label">Votre IP:</span>
                        <span class="infra-value">{infrastructure['local_ip']}</span>
                    </div>
                    <div class="infra-item">
                        <span class="infra-label">Votre MAC:</span>
                        <span class="infra-value">{infrastructure['local_mac']}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Network Diagnostic Tool</strong> • Généré le {report_time}</p>
            <p>© {current_year} • Données collectées en temps réel</p>
        </div>
    </div>
</body>
</html>"""

def get_report_css():
    """Return the CSS styles for the report"""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 30px;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #4361ee;
        }
        
        .section h2 {
            color: #3f37c9;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.5em;
        }
        
        .icon {
            font-size: 1.2em;
        }
        
        .performance-grade {
            display: flex;
            align-items: center;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 10px;
            gap: 20px;
        }
        
        .grade-A { background: #d4edda; color: #155724; border: 2px solid #c3e6cb; }
        .grade-B { background: #d1ecf1; color: #0c5460; border: 2px solid #bee5eb; }
        .grade-C { background: #fff3cd; color: #856404; border: 2px solid #ffeaa7; }
        .grade-D { background: #f8d7da; color: #721c24; border: 2px solid #f5c6cb; }
        
        .grade-icon {
            font-size: 3em;
        }
        
        .grade-info h2 {
            margin: 0;
            color: inherit;
        }
        
        .info-grid, .infrastructure-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .info-item, .infra-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #4361ee;
        }
        
        .info-label, .infra-label {
            font-weight: bold;
            color: #666;
        }
        
        .info-value, .infra-value {
            color: #333;
            font-family: monospace;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #4361ee;
        }
        
        .stat-card.success { border-left-color: #28a745; }
        .stat-card.warning { border-left-color: #ffc107; }
        .stat-card.error { border-left-color: #dc3545; }
        
        .stat-icon {
            font-size: 2em;
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #4361ee;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .device-map {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .device-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border: 2px solid #e9ecef;
        }
        
        .device-card.online { border-color: #28a745; }
        .device-card.offline { border-color: #dc3545; opacity: 0.6; }
        
        .device-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .device-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .device-ip {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .device-signal {
            font-size: 0.8em;
            color: #888;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background: linear-gradient(135deg, #4361ee, #3f37c9);
            color: white;
            font-weight: 600;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-online {
            color: #28a745;
            font-weight: bold;
        }
        
        .status-offline {
            color: #dc3545;
            font-weight: bold;
        }
        
        .signal-display {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .signal-bar {
            width: 50px;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .signal-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .issues-list, .recommendations-list, .security-list {
            list-style: none;
            padding: 0;
        }
        
        .issue-item, .recommendation-item, .security-item {
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #4361ee;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .recommendation-item.warning {
            border-left-color: #ffc107;
            background: #fff8e1;
        }
        
        .recommendation-item.error {
            border-left-color: #dc3545;
            background: #ffebee;
        }
        
        .security-item {
            border-left-color: #ff6b35;
            background: #fff5f5;
        }
        
        .no-issues {
            color: #28a745;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            background: #d4edda;
            border-radius: 8px;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }
            
            .content {
                padding: 20px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats-grid, .info-grid, .infrastructure-grid {
                grid-template-columns: 1fr;
            }
            
            .device-map {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            }
            
            .performance-grade {
                flex-direction: column;
                text-align: center;
            }
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                border-radius: 0;
            }
            
            .header {
                background: #4361ee !important;
                -webkit-print-color-adjust: exact;
            }
        }
    """

def generate_error_report(error_message):
    """Generate error report when main report generation fails"""
    current_time = datetime.datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
    
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Erreur - Rapport de Diagnostic Réseau</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
            padding: 20px;
            margin: 0;
        }}
        .error-container {{
            max-width: 600px;
            margin: 50px auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .error-icon {{
            font-size: 4em;
            color: #dc3545;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #dc3545;
            margin-bottom: 20px;
        }}
        .error-message {{
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
            word-wrap: break-word;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        .retry-info {{
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h1>Erreur de Génération du Rapport</h1>
        <p>Une erreur s'est produite lors de la génération du rapport de diagnostic réseau.</p>
        
        <div class="error-message">
            <strong>Détails de l'erreur:</strong><br>
            {error_message}
        </div>
        
        <div class="retry-info">
            <strong>💡 Solutions suggérées:</strong><br>
            • Actualisez la page et réessayez<br>
            • Vérifiez votre connexion réseau<br>
            • Contactez l'administrateur système si le problème persiste
        </div>
        
        <div class="timestamp">
            Erreur survenue le {current_time}
        </div>
    </div>
</body>
</html>"""

# Test function to validate the report generator
def test_report_generation():
    """Test the report generator with sample data"""
    try:
        # Create sample user data (simulating SQLite Row)
        class MockUser:
            def __init__(self):
                self.data = {
                    'id': 1,
                    'username': 'testuser',
                    'name': 'Test User',
                    'ip_address': '192.168.1.100',
                    'mac_address': 'AA:BB:CC:DD:EE:FF',
                    'connection_start': '2025-01-15 10:30:00'
                }
            
            def __getitem__(self, key):
                return self.data.get(key)
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        # Create sample devices data
        sample_devices = [
            {
                'id': 1,
                'name': 'Router-Main',
                'ip': '192.168.1.1',
                'mac': '00:11:22:33:44:55',
                'type': 'router',
                'status': 'online',
                'signal': 100
            },
            {
                'id': 2,
                'name': 'Laptop-Office',
                'ip': '192.168.1.101',
                'mac': 'AA:BB:CC:DD:EE:01',
                'type': 'laptop',
                'status': 'online',
                'signal': 85
            },
            {
                'id': 3,
                'name': 'Phone-Android',
                'ip': '192.168.1.102',
                'mac': 'AA:BB:CC:DD:EE:02',
                'type': 'phone',
                'status': 'online',
                'signal': 72
            },
            {
                'id': 4,
                'name': 'Printer-HP',
                'ip': '192.168.1.103',
                'mac': 'AA:BB:CC:DD:EE:03',
                'type': 'printer',
                'status': 'offline',
                'signal': 0
            }
        ]
        
        # Create sample performance data
        class MockPerformance:
            def __init__(self):
                self.data = {
                    'avg_bandwidth': 45.5,
                    'avg_latency': 28.3
                }
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        mock_user = MockUser()
        mock_performance = MockPerformance()
        
        # Generate report
        report_html = generate_report(mock_user, sample_devices, mock_performance)
        
        # Save test report
        with open('test_network_report.html', 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        print("✅ Test report generated successfully!")
        print(f"📄 Report saved as 'test_network_report.html' ({len(report_html)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run test when script is executed directly
    print("🧪 Testing Network Report Generator...")
    test_report_generation()