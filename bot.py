import openai
from mastodon import Mastodon
import time
import json
import os



# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI")

# Set up Mastodon API credentials
mastodon = Mastodon(
    access_token=os.getenv("MASTODON"),
    api_base_url="https://botsin.space/@circuitousstories"
)

# Define the interval in seconds between each iteration of the bot
ITERATION_INTERVAL =  10# 12 hours

def generate_prompt(previous_segments, story_start):
    """
    Generates a prompt for the OpenAI API based on the previous story segments and votable options.
    Returns the prompt as a string.
    """
    prompt = " ".join(previous_segments)
    if story_start != True:
        prompt += "\n\nWhat should the hero do next?\nPlease send two options as a list of two strings"
    else:
        prompt += "\n\nHow should the story start?\nPlease send two options as a list of two strings"

    return prompt

def generate_votable_options(previous_segments):
    """
    Generates two new votable options based on the previous story segments using the OpenAI API.
    Returns the votable options as a list of two strings.
    """
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=generate_prompt(previous_segments),
        max_tokens=50,
        n=2,
        stop=None,
        temperature=0.5,
    )
    
    # Extract the generated text from the OpenAI API response
    new_segment = (response.choices[0].text.strip(), response.choices[1].text.strip())
    
    return new_segment

def post_votable_options(previous_segments, story_start):
    """
    Creates and posts two votable options based on the previous story segments.
    """
    # Combine the previous story segments into a single string
    prompt = " ".join(previous_segments)
    
    # Generate the votable options using the OpenAI API
    votable_options = generate_votable_options(prompt, story_start)
    
    # Add the votable options to the prompt as well
    prompt += "\n\nWhat should the hero do next?"
    
    poll = Mastodon.make_poll(Mastodon, options=[votable_options[0], votable_options[1]], expires_in=ITERATION_INTERVAL)

    # Post the votable options to your Mastodon account
    # mastodon.status_post(status=prompt, poll=poll)
    print(prompt)
    print(votable_options[0], votable_options[1])
    save_state(previous_segments, votable_options)

def load_state():
    """
    Loads the current state of the story and votable options from a file.
    Returns a tuple containing the previous story segments and the votable options.
    """
    try:
        with open("state.json", "r") as f:
            state = json.load(f)
        return state["previous_segments"], state["votable_options"]
    except:
        return ["Once upon a time..."], generate_votable_options("Once upon a time...", True)

def save_state(previous_segments, votable_options):
    """
    Saves the current state of the story and votable options to a file.
    """
    state = {"previous_segments": previous_segments, "votable_options": votable_options}
    with open("state.json", "w") as f:
        json.dump(state, f)

def main(previous_statments, votable_options):

    while True:
        post_votable_options(previous_statments)
        save_state(previous_statments, votable_options)
        time.sleep(ITERATION_INTERVAL)

if __name__ == "__main__":
    previous_statments,votable_options = load_state()
    main(previous_statments, votable_options)
