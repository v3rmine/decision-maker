import csv
import json
from subprocess import run

# NOTE: Abandonned, we find that Huric is not what we want for dependency resolving, a bit too complex
if __name__ == '__main__':
    with open('tests/huric_test_frame_dataset.csv') as csv_file:
        reader = csv.reader(csv_file)
        # Skip the header
        next(reader)

        for (huric_id, sentence, frame_name, frame_token, sem_type, sem_head, tokens) in reader:
            id = f"{huric_id}.{frame_token}.{sem_head}"
            result = json.loads(run('process-prompt.py', input=sentence, text=True, capture_output=True).stdout)
            ok = False
            error = ""
            for frame in result['semantics_frames']:
                if int(frame_token) == int(frame['token_id']):
                    for semantic in frame['elements']:
                        found_tokens = ';'.join(map(str, semantic['tokens_id']))
                        
                        if tokens == found_tokens:
                            ok = True
                        else:
                            error += f"  tokens for head {frame['token_id']}.{sem_head}: {found_tokens}\n"
                            error += f"  expected        {frame_token}.{sem_head}: {tokens}\n"
                else:
                    print(frame_token, frame['token_id'])      
            if ok:
                print(f"Ok {id}")
            else:
                print(f"Error {id}: '{sentence}'")
                print(error)