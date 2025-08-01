const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

let startTime = Date.now();

app.get('/', (req, res) => {
    res.json({
        message: 'NoxGuard Frontend',
        status: 'running',
        uptime: Date.now() - startTime,
        environment: process.env.NODE_ENV || 'development'
    });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'noxguard-frontend',
        uptime: Date.now() - startTime
    });
});

app.listen(port, () => {
    console.log(`NoxGuard Frontend running on port ${port}`);
});
