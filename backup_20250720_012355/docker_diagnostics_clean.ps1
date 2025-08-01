# Docker Network Diagnostics (PowerShell)
# Part of Ultimate Suite v11.0

Write-Host "Docker Network Diagnostics" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Test Docker installation
Write-Host "`nTesting Docker Installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "SUCCESS: Docker is installed: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Docker is not installed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Docker is not installed or not accessible" -ForegroundColor Red
    exit 1
}

# Test Docker daemon
Write-Host "`nTesting Docker Daemon..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>$null
    if ($dockerInfo) {
        Write-Host "SUCCESS: Docker daemon is running" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Docker daemon is not running" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Cannot connect to Docker daemon" -ForegroundColor Red
    exit 1
}

# Test Docker Compose
Write-Host "`nTesting Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Host "SUCCESS: Docker Compose is installed: $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Docker Compose is not installed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Docker Compose is not accessible" -ForegroundColor Red
}

# List Docker networks
Write-Host "`nDocker Networks:" -ForegroundColor Yellow
try {
    docker network ls
    Write-Host "SUCCESS: Docker networks listed successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to list Docker networks" -ForegroundColor Red
}

# Test port availability
Write-Host "`nTesting Port Availability..." -ForegroundColor Yellow
$ports = @(5000, 5001, 5002, 5003, 6379, 6380, 3000, 8081, 9090)

foreach ($port in $ports) {
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.ReceiveTimeout = 1000
        $tcpClient.SendTimeout = 1000
        $connection = $tcpClient.ConnectAsync("localhost", $port)
        
        if ($connection.Wait(1000)) {
            Write-Host "WARNING: Port $port is occupied" -ForegroundColor Yellow
        } else {
            Write-Host "SUCCESS: Port $port is available" -ForegroundColor Green
        }
        $tcpClient.Close()
    } catch {
        Write-Host "SUCCESS: Port $port is available" -ForegroundColor Green
    }
}

# Test Redis connectivity
Write-Host "`nTesting Redis Connectivity..." -ForegroundColor Yellow
$redisHosts = @("localhost", "127.0.0.1", "host.docker.internal", "172.17.0.1")
$redisPorts = @(6379, 6380)

foreach ($redisHost in $redisHosts) {
    foreach ($redisPort in $redisPorts) {
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.ReceiveTimeout = 2000
            $tcpClient.SendTimeout = 2000
            $connection = $tcpClient.ConnectAsync($redisHost, $redisPort)
            
            if ($connection.Wait(2000)) {
                Write-Host "SUCCESS: Redis connection successful: $redisHost`:$redisPort" -ForegroundColor Green
            } else {
                Write-Host "ERROR: Redis connection failed: $redisHost`:$redisPort" -ForegroundColor Red
            }
            $tcpClient.Close()
        } catch {
            Write-Host "ERROR: Redis connection failed: $redisHost`:$redisPort" -ForegroundColor Red
        }
    }
}

# Test if Redis container is running
Write-Host "`nChecking Redis Containers..." -ForegroundColor Yellow
try {
    $redisContainers = docker ps -a --filter "name=redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
    if ($redisContainers) {
        Write-Host "Redis containers found:" -ForegroundColor Green
        Write-Host $redisContainers
    } else {
        Write-Host "ERROR: No Redis containers found" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Failed to check Redis containers" -ForegroundColor Red
}

# Summary
Write-Host "`nDiagnostic Summary:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "SUCCESS: Docker installation: OK" -ForegroundColor Green
Write-Host "SUCCESS: Docker daemon: Running" -ForegroundColor Green

# Check if we found any Redis connections
$redisFound = $false
foreach ($redisHost in $redisHosts) {
    foreach ($redisPort in $redisPorts) {
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $connection = $tcpClient.ConnectAsync($redisHost, $redisPort)
            if ($connection.Wait(1000)) {
                $redisFound = $true
                break
            }
            $tcpClient.Close()
        } catch {
            # Ignore errors for summary
        }
    }
    if ($redisFound) { break }
}

if ($redisFound) {
    Write-Host "SUCCESS: Redis connectivity: Available" -ForegroundColor Green
} else {
    Write-Host "ERROR: Redis connectivity: Not available" -ForegroundColor Red
    Write-Host "RECOMMENDATION: Start Redis with docker-compose or install Redis locally" -ForegroundColor Yellow
}

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "===========" -ForegroundColor Cyan
Write-Host "1. To start Redis development stack:" -ForegroundColor White
Write-Host "   docker-compose -f docker-compose.dev-networking.yml up -d redis-dev" -ForegroundColor Gray
Write-Host "2. To start the enhanced server:" -ForegroundColor White
Write-Host "   python server_enhanced.py" -ForegroundColor Gray
Write-Host "3. To test network connectivity:" -ForegroundColor White
Write-Host "   Access http://localhost:5003 in your browser" -ForegroundColor Gray

Write-Host "`nDiagnostics completed successfully!" -ForegroundColor Green
