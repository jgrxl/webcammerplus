// Verification script for platform launcher status checking
// Run this in the browser console on the platform launcher page

console.log("=== Platform Status Verification ===");

// Check all services
async function verifyServices() {
    const services = {
        backend: 'http://localhost:5000/api/v1',
        frontend: 'http://localhost:5173',
        influxdb: 'http://localhost:8086/health',
        docs: 'http://localhost:5000/docs/'
    };
    
    console.log("\n🔍 Checking services...\n");
    
    for (const [name, url] of Object.entries(services)) {
        try {
            const response = await fetch(url);
            const status = response.ok ? '🟢 ONLINE' : '🔴 OFFLINE';
            console.log(`${name.padEnd(10)} : ${status} (${response.status})`);
            
            if (name === 'backend' && response.ok) {
                const data = await response.json();
                console.log(`            API Version: ${data.api_version}`);
            }
            if (name === 'influxdb' && response.ok) {
                const data = await response.json();
                console.log(`            Status: ${data.status}, Version: ${data.version}`);
            }
        } catch (error) {
            console.log(`${name.padEnd(10)} : 🔴 OFFLINE (Connection Failed)`);
            console.log(`            Error: ${error.message}`);
        }
    }
    
    console.log("\n✅ Verification complete!");
}

// Color code verification
console.log("\n📋 Status Color Codes:");
console.log("🟢 Green  = Service is online and healthy");
console.log("🟡 Yellow = Service has configuration issues or warnings");
console.log("🔴 Red    = Service is offline or unreachable");

// Run the verification
verifyServices();

// Export for use in console
window.verifyPlatformStatus = verifyServices;