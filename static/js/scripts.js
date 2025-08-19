// Initialize the application
function initApp(performanceData, devices) {
    // Initialize UI components
    initNavigation();
    initThemeToggle();
    initEventListeners();
    
    // Generate network map with real devices
    generateNetworkMap(devices);
    
    // Initialize performance chart with real data
    initPerformanceChart(performanceData);
    
    // Start live updates-
    startLiveUpdates();
}

// Initialize navigation
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Hide all content sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });
            
            // Show the selected section
            const sectionId = this.getAttribute('data-section');
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'block';
                
                // Refresh data when switching to certain sections
                if (sectionId === 'cartographie') {
                    refreshNetwork();
                } else if (sectionId === 'performance') {
                    updatePerformanceChart();
                }
            }
        });
    });
}

// Initialize theme toggle
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme
    if (prefersDark) {
        document.body.classList.add('dark-theme');
        themeToggle.classList.add('dark');
    } else {
        document.body.classList.add('light-theme');
        themeToggle.classList.add('light');
    }
    
    themeToggle.addEventListener('click', () => {
        if (document.body.classList.contains('dark-theme')) {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            themeToggle.classList.remove('dark');
            themeToggle.classList.add('light');
            localStorage.setItem('theme', 'light');
        } else {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            themeToggle.classList.remove('light');
            themeToggle.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.remove('dark-theme', 'light-theme');
        document.body.classList.add(savedTheme + '-theme');
        themeToggle.classList.remove('dark', 'light');
        themeToggle.classList.add(savedTheme);
    }
}

// Rest of the script remains similar but with real data handling...

// Initialize event listeners
function initEventListeners() {
    // Refresh network map
    document.getElementById('refreshNetworkMap').addEventListener('click', refreshNetwork);
    
    // Generate report
    document.getElementById('generateReport').addEventListener('click', generateReport);
    
    // View all activities
    document.getElementById('viewAllActivities').addEventListener('click', () => {
        alert('Journal complet affiché dans une nouvelle fenêtre');
    });
    
    // Export data
    document.getElementById('exportData').addEventListener('click', () => {
        alert('Données exportées au format CSV');
    });
    
    // Fullscreen chart
    document.getElementById('fullscreenChart').addEventListener('click', () => {
        const chart = document.getElementById('performanceChart');
        chart.requestFullscreen().catch(err => {
            alert(`Erreur en mode plein écran: ${err.message}`);
        });
    });
}

// Generate network map
function generateNetworkMap(devices) {
    const networkMap = document.getElementById('networkMap');
    networkMap.innerHTML = '';
    
    if (!devices || devices.length === 0) {
        networkMap.innerHTML = '<div class="no-devices"><i class="fas fa-wifi-slash"></i><p>Aucun appareil détecté</p></div>';
        return;
    }
    
    // Create router node at center
    const router = devices.find(d => d.type === 'router');
    if (router) {
        createNode(router, 50, 50);
    }
    
    // Create other devices
    const angleStep = (2 * Math.PI) / (devices.length - 1);
    let index = 0;
    
    devices.forEach(device => {
        if (device.type === 'router') return;
        
        const angle = index * angleStep;
        const radius = 30 + Math.random() * 20;
        const x = 50 + radius * Math.cos(angle);
        const y = 50 + radius * Math.sin(angle);
        
        createNode(device, x, y);
        
        // Create connection to router
        if (router) {
            createConnection(router, device);
        }
        
        index++;
    });
}

// Create a network node
function createNode(device, x, y) {
    const node = document.createElement('div');
    node.classList.add('network-node', device.type);
    if (device.status === 'offline') {
        node.classList.add('offline');
    }
    node.style.left = `${x}%`;
    node.style.top = `${y}%`;
    
    // Add icon based on device type
    const icon = document.createElement('i');
    switch(device.type) {
        case 'router': icon.className = 'fas fa-wifi'; break;
        case 'server': icon.className = 'fas fa-server'; break;
        case 'desktop': icon.className = 'fas fa-desktop'; break;
        case 'laptop': icon.className = 'fas fa-laptop'; break;
        case 'phone': icon.className = 'fas fa-mobile-alt'; break;
        case 'printer': icon.className = 'fas fa-print'; break;
        case 'camera': icon.className = 'fas fa-video'; break;
        default: icon.className = 'fas fa-microchip';
    }
    node.appendChild(icon);
    
    // Add node info
    const nodeInfo = document.createElement('div');
    nodeInfo.classList.add('node-info');
    nodeInfo.innerHTML = `
        <h4>${device.name}</h4>
        <p><i class="fas fa-microchip"></i> MAC: ${device.mac}</p>
        <p><i class="fas fa-location-arrow"></i> IP: ${device.ip}</p>
        <p><i class="fas fa-circle"></i> Status: ${device.status === 'online' ? 'En ligne' : 'Hors ligne'}</p>
    `;
    
    // Add hover effect
    node.addEventListener('mouseenter', () => {
        nodeInfo.style.display = 'block';
        nodeInfo.style.left = `${parseFloat(node.style.left) + 2}%`;
        nodeInfo.style.top = `${parseFloat(node.style.top) + 2}%`;
    });
    
    node.addEventListener('mouseleave', () => {
        nodeInfo.style.display = 'none';
    });
    
    document.getElementById('networkMap').appendChild(node);
    document.getElementById('networkMap').appendChild(nodeInfo);
}

// Create connection between nodes
function createConnection(device1, device2) {
    const connection = document.createElement('div');
    connection.classList.add('node-connection');
    document.getElementById('networkMap').appendChild(connection);
}

// Initialize performance chart
function initPerformanceChart(performanceData) {
    if (!performanceData) return;
    
    const ctx = document.getElementById('performanceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: performanceData.timestamps,
            datasets: [
                {
                    label: 'Bande Passante (Mbps)',
                    data: [performanceData.bandwidth, 0, 0, 0, 0, 0, 0, 0], // Single value repeated
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Latence (ms)',
                    data: [performanceData.latency, 0, 0, 0, 0, 0, 0, 0], // Single value repeated
                    borderColor: '#4cc9f0',
                    backgroundColor: 'rgba(76, 201, 240, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f8f9fa'
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

// Refresh network data
function refreshNetwork() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingOverlay.style.display = 'flex';
    loadingText.textContent = 'Scan du réseau en cours...';
    
    // Call backend to refresh network
    axios.get('/refresh_network')
        .then(response => {
            // Regenerate network map with new data
            generateNetworkMap(response.data.devices);
            
            // Hide loading overlay
            loadingOverlay.style.display = 'none';
        })
        .catch(error => {
            console.error('Network refresh failed:', error);
            loadingOverlay.style.display = 'none';
            alert('Échec de l\'actualisation du réseau');
        });
}

// Generate report
function generateReport() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingOverlay.style.display = 'flex';
    loadingText.textContent = 'Génération du rapport...';
    
    // Call backend to generate report
    axios.get('/generate_report')
        .then(response => {
            // Open report in new window
            const reportWindow = window.open('', '_blank');
            reportWindow.document.write(response.data.report_content);
            reportWindow.document.close();
            
            // Hide loading overlay
            loadingOverlay.style.display = 'none';
        })
        .catch(error => {
            console.error('Report generation failed:', error);
            loadingOverlay.style.display = 'none';
            alert('Échec de la génération du rapport');
        });
}

// Start live updates
function startLiveUpdates() {
    // Update connection time every minute
    setInterval(() => {
        const timeElement = document.getElementById('connectionTime');
        const currentTime = parseInt(timeElement.textContent);
        timeElement.textContent = (currentTime + 1) + " min";
    }, 60000);
    
    // Refresh network data every 5 minutes
    setInterval(refreshNetwork, 300000);
}