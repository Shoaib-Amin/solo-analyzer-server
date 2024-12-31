const express = require("express");
const multer = require('multer');
const { exec, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const router = express.Router();
const upload = multer({ dest: 'uploads/' });


router.get('/test', (req, res) => {
    res.json('test route is working')
})

router.post('/audio', async (req, res) => {
    console.log('in the request')
    console.log(req.body, 'requested body')
    try {
        // Check if audio exists in the request body
        const { audio } = req.body;
        if (!audio) {
            return res.status(400).json({ error: 'No audio data provided.' });
        }

        // Decode the Base64 string into a Buffer
        const buffer = Buffer.from(audio, 'base64');
        console.log(buffer, 'Decoded buffer');

        // Create a temporary file path to save the audio
        const tempFilePath = path.join(__dirname, '../uploads', `audio_${Date.now()}.mp3`);
        console.log('came in the request')
        // Write the buffer to the temporary file
        // fs.writeFileSync(tempFilePath, buffer);
        fs.writeFileSync(tempFilePath, buffer, (err) => {
            if (err) {
                console.log('Error writing file:', err);
                return res.status(500).json({ error: 'Error saving audio file.' });
            }
            console.log('Temporary audio file saved at:', tempFilePath);
        });

        // Call Python script to analyze the audio file
        const pythonProcess = spawn('python', ['analyze_audio.py', tempFilePath]);

        let output = '';
        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error('stderr:', data.toString());
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python script exited with code ${code}`);
                return res.status(500).json({ error: 'Error executing Python script.' });
            }

            try {
                const analysisResult = JSON.parse(output); // Parse the Python script output (JSON)

                // Clean up the temporary file
                fs.unlinkSync(tempFilePath);
                console.log('Temporary file deleted after analysis.');

                // Send the analysis result back to the client
                res.json(analysisResult);
            } catch (error) {
                console.error('Error parsing Python output:', error);
                res.status(500).json({ error: 'Error parsing Python output.' });
            }
        });
    } catch (error) {
        console.error('Error handling audio upload:', error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});

router.post('/test', upload.single('audio'), (req, res) => {
    console.log(req.file, 'requeste file')

    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No audio file uploaded.' });
        }
        const filePath = path.join(__dirname, '..', req.file.path);
        console.log('Audio file uploaded at:', filePath);

        const pythonProcess = spawn('python', ['analyze_audio.py', filePath]);

        let output = '';
        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error('stderr:', data.toString());
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python script exited with code ${code}`);
                return res.status(500).json({ error: 'Error executing Python script.' });
            }
            try {
                const analysisResult = JSON.parse(output)
                fs.unlinkSync(filePath); // Clean up the uploaded file
                res.json(analysisResult); // Send the analysis result
            } catch (error) {
                console.error('Error parsing Python output:', error);
                res.status(500).json({ error: 'Error parsing Python output.' });
            }
        });
        //      // Run the Python script for audio analysis
        // exec(`python analyze_audio.py "${"C:/Users/lenovo/Downloads/the-cradle-of-your-soul-15700.mp3"}"`, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
        //     if (error) {
        //       console.error('Error executing Python script:', error);
        //       return res.status(500).json({ error: 'Error processing the audio file.' });
        //     }
        //     if (stderr) {
        //       console.error('Python script stderr:', stderr);
        //       return res.status(500).json({ error: 'Error in Python script.' });
        //     }

        //     // Parse the output JSON from the Python script
        //     const analysisResult = JSON.parse(stdout);

        //     // Clean up the uploaded file after processing
        //     fs.unlinkSync(filePath);

        //     res.json(analysisResult);
        //   });
    } catch (error) {
        console.error('Error handling file upload:', error);
        res.status(500).json({ error: error });
    }
})

module.exports = router;