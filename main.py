import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google.cloud import language_v1
import re

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.message(re.compile("(AWS|Twingate|Leapp|SSO|Datadog)"))
def message_hello(message, say):
    # Extract the text from the message
    text = message['text']

    # Split text into sentences
    sentences = re.split(r'[.!?]', text)

    # Find the sentence containing the matched keyword
    matched_sentence = next((sentence for sentence in sentences if re.search("(AWS|Twingate|Leapp|SSO|Datadog)", sentence)), None)

    if matched_sentence:
        # say() sends a message to the channel with the matched sentence
        syntax_analysis(matched_sentence.strip())
        say(f"Here's a sentence with your keyword, <@{message['user']}>: {matched_sentence.strip()}.")
    else:
        # In case no sentence contains the keyword
        say(f"Keyword found, but no complete sentence detected, <@{message['user']}>.")



# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
