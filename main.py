import subprocess

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
    command = "whisper ./outputs/"+song_filename+"/vocals.wav --model large"
    do_terminal_command(command)

song_filename = "lucy"

create_song_folder(song_filename)
run_spleeter_command(song_filename)
transcribe_vocals(song_filename)