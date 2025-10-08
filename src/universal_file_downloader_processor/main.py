#!/usr/bin/env python
import sys
from universal_file_downloader_processor.crew import UniversalFileDownloaderProcessorCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        # 'google_drive_url': 'https://drive.google.com/file/d/10mKRhNLFCK-_pawRoRtyO2tPP6zBwpTm/view'
        'google_drive_url': 'https://www.dropbox.com/scl/fi/x7tnq20alq1d5xczsezum/real-estate-mock-contract.pdf?rlkey=kxxxiocwcrszp42ogfir8teqs&e=1&st=145dttjk&dl=0'
    }
    UniversalFileDownloaderProcessorCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'google_drive_url': 'sample_value'
    }
    try:
        UniversalFileDownloaderProcessorCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        UniversalFileDownloaderProcessorCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'google_drive_url': 'sample_value'
    }
    try:
        UniversalFileDownloaderProcessorCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
