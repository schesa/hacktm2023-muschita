import sys

import openai
import os
import csv


class gpt():
    def __init__(self):
        self.open_api_key = ""
        self.msg_length_max = 3000
        self.is_first_msg = True
        self.prev_conf = []
        self.iteration = 0
        
    def get(self, msg):
        
        if len(msg) > self.msg_length_max:
            msg = msg[0:self.msg_length_max]
        
        content_msg = ""
        if self.is_first_msg:
            self.is_first_msg = False
            content_msg = "using the next information, build a pitch on behalf of the person (not use starting useless phrases, \
                          start it immediately. use around 170 words):" + msg
        else:
            content_msg = "using the previous information and the new one, tune the pitch\
                          (do not use starting useless phrases, please, just run the pitch immedeately. \
                          use around 170 words): " + msg
            
        openai.api_key = self.open_api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": content_msg},
            ]
        )
        
        result = ''
        for choice in response.choices:
            result += choice.message.content
        
        print("iterator =", self.iteration, "content: \n", result)
        self.iteration = self.iteration + 1
        return result
   
   
class pitch_generator():
    
    def __init__(self):
        self.root = os.path.dirname(os.path.realpath(__file__))
        self.csvdir = os.path.join(self.root, 'output')    
        
    def get(self, name):
        result = ""
        for entry in os.listdir(self.csvdir):
            filepath = os.path.join(self.csvdir, entry)
            filepath_name, file_extension = os.path.splitext(entry)
            
            if not os.path.isfile(filepath) \
               or filepath_name != name:
                continue
                
            gptclient = gpt()
            with open(filepath, mode='r', newline='', encoding="utf8") as csvfile:
                csv.field_size_limit(int(sys.maxsize/10))
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    msg = row[0] + ": " + row[1]
                    result = gptclient.get(msg)
        return result
        
    
# def main():
#     generator = pitch_generator()
#
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     csvdir = os.path.join(current_dir, 'output')
#     for entry in os.listdir(csvdir):
#         name, file_extension = os.path.splitext(entry)
#         print("current name", name, "\n\n")
#         res = generator.get(name)
#         # print(res)
#
#
# if __name__ == "__main__":
#     main()
#