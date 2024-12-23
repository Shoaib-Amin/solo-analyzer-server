const express = require('express');
const cors = require('cors')

const analyzerRoute = require('./routes/analyzer.route')

const app = express();
const port = 8080;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));

app.use("/analyze", analyzerRoute);

app.listen(port, () => {
    console.log(`Server is running on port ${port}`)
})