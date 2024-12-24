import librosa
import json
import sys
import numpy as np

def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None)
    
    # Tempo analysis
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo)

    # Onset times for detecting attack points
    onset_times = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    
    # Pitch tracking
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # Convert pitches to note names (MIDI note numbers)
    notes = []
    note_timings = []  # To store note timing information
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()  # Find the index with the highest magnitude for each frame
        pitch = pitches[index, t]  # Extract the pitch
        if pitch > 0:  # Only consider non-zero pitches
            midi_note = librosa.hz_to_midi(pitch)  # Convert pitch (Hz) to MIDI note number
            note_name = librosa.midi_to_note(midi_note)
            notes.append(note_name)
            note_timings.append(t * (1 / sr))  # Calculate timing for the note
    
    # Calculate intervals (differences) between consecutive notes
    intervals_up = []
    intervals_down = []
    for i in range(1, len(notes)):
        prev_note = librosa.note_to_midi(notes[i - 1])
        current_note = librosa.note_to_midi(notes[i])
        interval = current_note - prev_note
        if interval > 0:
            intervals_up.append(interval)
        elif interval < 0:
            intervals_down.append(abs(interval))  # Store as positive for down intervals

    # Mapping for interval names
    interval_mapping = {
        1: "Mi 2nds",
        2: "Ma 2nds",
        3: "Mi 3rds",
        4: "Ma 3rds",
        5: "Perfect 4th",
        6: "Augmented 4ths",
        7: "Perfect 5ths",
        8: "Mi 6ths",
        9: "Major 6ths",
        10: "Mi 7ths",
        11: "Ma 7ths",
        12: "Octave"
    }

    # Create display data for intervals_up
    intervals_up_display = []
    for interval in set(intervals_up):
        interval_name = interval_mapping.get(interval, f"Unknown ({interval})")
        intervals_up_display.append({
            "interval": interval_name,
            "count": intervals_up.count(interval)
        })

    # Create display data for intervals_down
    intervals_down_display = []
    for interval in set(intervals_down):
        interval_name = interval_mapping.get(interval, f"Unknown ({interval})")
        intervals_down_display.append({
            "interval": interval_name,
            "count": intervals_down.count(interval)
        })

    transcription = [{"note": note, "time": time} for note, time in zip(notes, note_timings)]
    
    analysis_result = {
        'tempo': tempo,
        'onset_times': onset_times.tolist(),  # Convert NumPy array to list
        'note_percentages': {note: notes.count(note) / len(notes) * 100 for note in set(notes)},
        'transcription': transcription,  # Include transcription in the output
        'intervals_up': intervals_up,
        'intervals_down': intervals_down,
        'intervals_up_display': intervals_up_display,
        'intervals_down_display': intervals_down_display
    }
    
    # Return the result as a JSON string
    return json.dumps(analysis_result, indent=4)

if __name__ == "__main__":
    audio_file_path = sys.argv[1]  # Get the audio file path from the command line arguments
    result = analyze_audio(audio_file_path)
    print(result)
