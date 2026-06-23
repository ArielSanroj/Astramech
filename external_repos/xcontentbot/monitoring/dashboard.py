"""Dashboard HTML generation."""


def generate_dashboard_html() -> str:
    """Generate simple HTML dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>xcontentbot Monitoring Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .healthy { background-color: #d4edda; color: #155724; }
            .degraded { background-color: #fff3cd; color: #856404; }
            .unhealthy { background-color: #f8d7da; color: #721c24; }
            .critical { background-color: #f5c6cb; color: #721c24; }
            .metric { display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>xcontentbot Monitoring Dashboard</h1>
        <div id="status"></div>
        <div id="metrics"></div>
        <script>
            async function loadStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();

                    document.getElementById('status').innerHTML = `
                        <div class="status ${data.status}">
                            <h2>Overall Status: ${data.status.toUpperCase()}</h2>
                            <p>Last updated: ${new Date(data.timestamp).toLocaleString()}</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('status').innerHTML = `
                        <div class="status unhealthy">
                            <h2>Error loading status</h2>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
            }

            async function loadMetrics() {
                try {
                    const response = await fetch('/metrics');
                    const data = await response.json();

                    document.getElementById('metrics').innerHTML = `
                        <h2>Metrics</h2>
                        <div class="metric">
                            <h3>System</h3>
                            <p>Memory: ${data.system.memory.percent.toFixed(1)}%</p>
                            <p>CPU: ${data.system.cpu.percent.toFixed(1)}%</p>
                        </div>
                        <div class="metric">
                            <h3>Application</h3>
                            <p>Posts: ${data.application.counters['posts.started'] || 0}</p>
                            <p>Success Rate: ${((data.application.counters['posts.success'] || 0) / Math.max(data.application.counters['posts.started'] || 1, 1) * 100).toFixed(1)}%</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('metrics').innerHTML = `
                        <div class="status unhealthy">
                            <h2>Error loading metrics</h2>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
            }

            loadStatus();
            loadMetrics();
            setInterval(loadStatus, 30000);
            setInterval(loadMetrics, 30000);
        </script>
    </body>
    </html>
    """
