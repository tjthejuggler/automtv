import subprocess
import whisper_timestamped as whisper
import json
import pyperclip

song_filename = "lucy"
fps = 20
frames_before_prompt = 8
frames_after_prompt = 4
use_predictive_prompting = True

def do_terminal_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Command output:", result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e.stderr.decode('utf-8'))

def run_spleeter_command(song_filename):
    command = "spleeter separate -p spleeter:4stems -o ./outputs "+song_filename +".mp3"
    do_terminal_command(command)

def create_song_folder(song_filename):
    command = "mkdir ./outputs/"+song_filename
    do_terminal_command(command)

def transcribe_vocals(song_filename):
    # command = "whisper --model large"
    # do_terminal_command(command)
    audio = whisper.load_audio("./outputs/"+song_filename+"/vocals.wav")
    model = whisper.load_model("large")
    result = whisper.transcribe(model, audio, language="en")
    return result

def convert_to_frame_dict(nested_dict, fps):
    frame_dict = {}
    strength_values = ""
    for segment in nested_dict["segments"]:
        start_time = segment["start"]
        end_time = segment["end"]
        words = segment["words"]

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        for word in words:
            word_text = word["text"]
            word_start = word["start"]
            word_end = word["end"]
            word_frame = int(word_start * fps)
            strength_values = strength_values + str(word_frame-(frames_before_prompt+1)) + ": (0.85),\n" + str(word_frame) + ": (0.55),\n" + str(word_frame+(frames_after_prompt+1)) + ": (0.85),\n"
            if word_frame not in frame_dict:
                frame_dict[word_frame] = word_text
                
            else:
                frame_dict[word_frame] += " " + word_text

    strength_values = strength_values[:-2]
    return frame_dict, strength_values



create_song_folder(song_filename)
run_spleeter_command(song_filename)
transcription_dict = transcribe_vocals(song_filename)

# Save transcription to file
output_path = "./outputs/" + song_filename + "/transcription.json"
with open(output_path, "w") as outfile:    
    json.dump(transcription_dict, outfile, indent=4)
    print("Transcription saved to: ", output_path)

frame_dict, strength_values = convert_to_frame_dict(transcription_dict, fps)

# Create a new dictionary with string keys and string values
string_keys_dict = {str(k): v for k, v in frame_dict.items()}

# Convert the dictionary to a pretty formatted string
pretty_dict_string = json.dumps(string_keys_dict, indent=4)

print(json.dumps(transcription_dict, indent = 2, ensure_ascii = False))

print(pretty_dict_string)
if use_predictive_prompting:
    def append_next_five_values(d):
        keys = list(d.keys())
        values = list(d.values())
        result = {}
        
        for i, (key, value) in enumerate(zip(keys, values)):
            new_value = value+":2.2"
            for j in range(1, 6):
                if i + j < len(values):
                    new_value += f", {values[i + j]}:{round(1.5 - (j*0.1), 2)}"
                    #round new_value to 1 decimal place and remove trailing 0
                    #new_value = str(round(float(new_value), 1)).rstrip('0').rstrip('.')
            result[key] = new_value
        return result

    output= append_next_five_values(frame_dict)

    print(json.dumps(output, indent = 2, ensure_ascii = False))

#print(transcription_dict)

print("\n\n\n"+strength_values)

#save transcription to clipboard with pyperclip

pyperclip.copy(str(transcription_dict))

