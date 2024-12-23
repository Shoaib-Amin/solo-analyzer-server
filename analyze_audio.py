import librosa
import json
import sys
import numpy as np

def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    
    # Tempo analysis
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # print(tempo, 'tempo')
    tempo = float(tempo)
    # print(tempo, 'tempo 2')
    # Onset times for detecting attack points
    onset_times = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    # print(onset_times, 'onset_times')
    # # Pitch and magnitude analysis
     # Pitch tracking using piptrack (extracts pitches and magnitudes)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # Convert pitches to note names
    notes = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()  # Find the index with the highest magnitude for each frame
        pitch = pitches[index, t]  # Extract the pitch
        if pitch > 0:  # Only consider non-zero pitches
            note = librosa.hz_to_note(pitch)  # Convert pitch (Hz) to note name
            notes.append(note)
    
    # Calculate the percentage of time each note is used
    unique_notes, counts = np.unique(notes, return_counts=True)
    note_percentages = {note: count / len(notes) * 100 for note, count in zip(unique_notes, counts) if count > 0}
    # print(pitches, 'pitches')
    # print(magnitudes, 'magnitudes')
    # # Convert pitches and magnitudes (NumPy arrays) to lists
    pitches = pitches.tolist()  # Convert NumPy array to list
    # magnitudes = magnitudes.tolist()  # Convert NumPy array to list
    # print(pitches, 'pitches 2')
    # print(magnitudes, 'magnitudes 2')
    # Calculate dynamic range (peak to average ratio)
    # rms = librosa.feature.rms(y=y)
    # print(rms, 'rms')
    # dynamic_range = rms.max() - rms.mean()
    # print(dynamic_range, 'dynamic_range')
    # Ensure dynamic_range is a scalar (if necessary, avoid returning NumPy types)
    # dynamic_range = dynamic_range.item() if isinstance(dynamic_range, np.ndarray) else dynamic_range
    # print(dynamic_range, 'dynamic_range 2')
    # Create a result dictionary, making sure all arrays are converted to lists
    max_onsets = 10
    analysis_result = {
        'tempo': tempo,
        'onset_times': onset_times.tolist()[:max_onsets],  # Convert NumPy array to list
        'note_percentages': note_percentages
        # 'dynamic_range': dynamic_range,  # Already scalar
        # 'pitches': pitches,
        # 'magnitudes': magnitudes
    }
    
    # Return the result as a JSON string
    return json.dumps(analysis_result, indent=4)

if __name__ == "__main__":
    audio_file_path = sys.argv[1]  # Get the audio file path from the command line arguments
    result = analyze_audio(audio_file_path)
    print(result)
