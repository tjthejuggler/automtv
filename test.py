import json

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
            strength_values = strength_values + str(word_frame-1) + ": (0.9),\n" + str(word_frame) + ": (0.55),\n" + str(word_frame+1) + ": (0.9),\n"
            if word_frame not in frame_dict:
                frame_dict[word_frame] = word_text
                
            else:
                frame_dict[word_frame] += " " + word_text

    strength_values = strength_values[:-2]
    return frame_dict, strength_values


with open("./outputs/lucy/transcription.json") as f:
    nested_dict = json.load(f)

fps = 20
frame_dict, strength_values = convert_to_frame_dict(nested_dict, fps)

# Create a new dictionary with string keys and string values
string_keys_dict = {str(k): v for k, v in frame_dict.items()}

# Convert the dictionary to a pretty formatted string
pretty_dict_string = json.dumps(string_keys_dict, indent=4)

print(pretty_dict_string)

print("\n\n\n"+strength_values)








