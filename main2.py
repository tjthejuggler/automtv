import subprocess
import whisper_timestamped as whisper
import json
import os

song_filename = "died"

frames_before_prompt = 3
frames_after_prompt = 1

juggling_word_beginning_to_end = False

def do_terminal_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Command output:", result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e.stderr.decode('utf-8'))

def run_spleeter_command(song_filename):
    command = "spleeter separate -p spleeter:4stems -o ./outputs ./songs/"+song_filename +".mp3"
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
            strength_values = strength_values + str(word_frame-(frames_before_prompt+1)) + ": (0.9),\n" + str(word_frame) + ": (0.3),\n" + str(word_frame+(frames_after_prompt+1)) + ": (0.9),\n"
            if word_frame not in frame_dict:
                frame_dict[word_frame] = word_text
                
            else:
                frame_dict[word_frame] += " " + word_text

    strength_values = strength_values[:-2]
    lines = strength_values.split("\n")
    unique_lines = []
    seen_numbers = set()

    for line in lines:
        number = line.split(":")[0].strip()
        if number not in seen_numbers:
            unique_lines.append(line)
            seen_numbers.add(number)
    
    #convert to string separated by newlines
    strength_values = "\n".join(unique_lines)


    return frame_dict, strength_values

def append_next_five_values(d):
    keys = list(d.keys())
    values = list(d.values())
    result = {}
    
    for i, (key, value) in enumerate(zip(keys, values)):
        new_value = value+":2"
        for j in range(1, 4):
            if i + j < len(values):
                new_value += f", {values[i + j]}:{round(1.1 - (j*0.02), 2)}"
                #round new_value to 1 decimal place and remove trailing 0
                #new_value = str(round(float(new_value), 1)).rstrip('0').rstrip('.')
        result[key] = new_value
    return result

def save_transcription_to_file(transcription_dict, song_filename):
    output_path = "./outputs/" + song_filename + "/transcription.json"
    with open(output_path, "w") as outfile:    
        json.dump(transcription_dict, outfile, indent=4)
        print("Transcription saved to: ", output_path)

def save_settings_to_file(strength_values, output, juggling_codes, song_filename):
    settings_dir = "./outputs/" + song_filename + "/settings"
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)

    with open(settings_dir + "/strength_values.txt", "w") as outfile:
        outfile.write(str(strength_values))

    with open(settings_dir + "/output.txt", "w") as outfile:
        outfile.write("\n\n\n"+json.dumps(output, indent = 2, ensure_ascii = False))

    with open(settings_dir + "/juggling_codes.txt", "w") as outfile:
        outfile.write("\n\n\n"+json.dumps(juggling_codes, indent = 2, ensure_ascii = False))

def get_words_color(word):
    with open("./word_color_dictionary.txt", "r") as infile:
        local_word_color_dictionary = json.load(infile)

    if local_word_color_dictionary[word] == None:
        local_word_color_dictionary[word] = ask_gpt_words_color(word)

    with open("./word_color_dictionary.txt", "w") as outfile:
        json.dump(local_word_color_dictionary, outfile, indent=4)

    return local_word_color_dictionary[word]

def calculate_juggling_codes(frame_dict, juggling_word_beginning_to_end):
    juggling_codes = {}
    for key, value in frame_dict.items():
        words_color = get_words_color(value)
        juggling_codes[key] = words_color
    return juggling_codes

def ask_gpt_words_color(word):
    color = ""

    return color

def main():
    
    fps = 20
    use_predictive_prompting = True
    make_juggling = True

    create_song_folder(song_filename)
    run_spleeter_command(song_filename)
    transcription_dict = transcribe_vocals(song_filename)
    save_transcription_to_file(transcription_dict, song_filename)

    frame_dict, strength_values = convert_to_frame_dict(transcription_dict, fps)

    # Create a new dictionary with string keys and string values
    string_keys_dict = {str(k): v for k, v in frame_dict.items()}

    # Convert the dictionary to a pretty formatted string
    pretty_dict_string = json.dumps(string_keys_dict, indent=4)

    print(json.dumps(transcription_dict, indent=2, ensure_ascii=False))
    print(pretty_dict_string)

    #if use_predictive_prompting:
    output = append_next_five_values(frame_dict)
    print(json.dumps(output, indent=2, ensure_ascii=False))

    print("\n\n\n"+strength_values)

    juggling_codes = {}
    if make_juggling:
        juggling_codes = calculate_juggling_codes(frame_dict, juggling_word_beginning_to_end)

    save_settings_to_file(strength_values, output, juggling_codes, song_filename)

if __name__ == "__main__":
    main()