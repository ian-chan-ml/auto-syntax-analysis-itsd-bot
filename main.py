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


def syntax_analysis(content):
    client = language_v1.LanguageServiceClient()

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_syntax(
        request={"document": document, "encoding_type": encoding_type}
    )

# Loop through tokens returned from the API
    for token in response.tokens:
        # Get the text content of this token. Usually a word or punctuation.
        text = token.text
        print(f"Token text: {text.content}")
        print(f"Location of this token in overall document: {text.begin_offset}")
        # Get the part of speech information for this token.
        # Part of speech is defined in:
        # http://www.lrec-conf.org/proceedings/lrec2012/pdf/274_Paper.pdf
        part_of_speech = token.part_of_speech
        # Get the tag, e.g. NOUN, ADJ for Adjective, et al.
        print(
            "Person: {}".format(
                language_v1.PartOfSpeech.Tag(part_of_speech.person).name
            )
        )
        # Get the voice, e.g. ACTIVE or PASSIVE
        print(
            "Aspect: {}".format(
                language_v1.PartOfSpeech.Voice(part_of_speech.aspect).name
            )
        )
        # Get the tense, e.g. PAST, FUTURE, PRESENT, et al.
        print(
            "Mood: {}".format(
                language_v1.PartOfSpeech.Tense(part_of_speech.mood).name
            )
        )
        # See API reference for additional Part of Speech information available
        # Get the lemma of the token. Wikipedia lemma description
        # https://en.wikipedia.org/wiki/Lemma_(morphology)
        print(f"Lemma: {token.lemma}")
        # Get the dependency tree parse information for this token.
        # For more information on dependency labels:
        # http://www.aclweb.org/anthology/P13-2017
        dependency_edge = token.dependency_edge
        print(f"Head token index: {dependency_edge.head_token_index}")
        print(
            "Label: {}".format(
                language_v1.DependencyEdge.Label(dependency_edge.label).name
            )
        )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
