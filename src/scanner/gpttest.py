import sys

import openai
import os
import csv


class gpt():
    def __init__(self):
        self.open_api_key = "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"
        self.msg_length_max = 3000
        self.is_first_msg = True
        self.prev_conf = []
        self.iteration = 0

    def get(self, msg):

        if len(msg) > self.msg_length_max:
            msg = msg[0:self.msg_length_max]

        template = "this is my pitch: \"Empowering sales teams with Apple Glasses, our startup revolutionizes customer \
        interactions through real-time, augmented reality insights, intuitively predicting customer needs. \
        This AR application not only enhances sales performance but also paves the way for a personalized shopping experience.\" \
        change it to include the personal info (use 200 words. don't use starting useless phrases):"

        content_msg = template + "\n" + "\"" + msg + "\"" + "\nRemove any personal name from the pitch and use the message limitation up to 200 words!"

        # print(content_msg, "\n------\n")
        # if self.is_first_msg:
        #     self.is_first_msg = False
        #     # content_msg = "using the next information, generate a pitch on behalf of the person (not use starting useless phrases, \
        #     #               start it immediately. use around 170 words. remove any personal names):" + msg
        #     content_msg = "using the next person description, generate a pitch on behalf of the person (not use starting useless phrases, \
        #                   start it immediately. use around 170 words. remove any personal names):" + msg
        #
        # else:
        #     content_msg = "using the previous information and the new one, tune the pitch\
        #                   (do not use starting useless phrases, please, just run the pitch immedeately. \
        #                   use around 170 words, remove any personal names): " + msg

        openai.api_key = self.open_api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": content_msg},
            ]
        )

        result = ''
        for choice in response.choices:
            result += choice.message.content

        # print("iteration =", self.iteration, "content: \n", result)
        self.iteration = self.iteration + 1
        return result


class pitch_generator():

    def __init__(self):
        self.root = os.path.dirname(os.path.realpath(__file__))
        self.csvdir = os.path.join(self.root, 'person_descr')

    def get(self, name):
        result = ""
        for entry in os.listdir(self.csvdir):
            filepath = os.path.join(self.csvdir, entry)
            filepath_name, file_extension = os.path.splitext(entry)

            if not os.path.isfile(filepath) \
               or filepath_name != name:
                continue

            gptclient = gpt()
            with open(filepath, mode='r', newline='', encoding="utf8") as f:
                descr = f.read()
                result = gptclient.get(descr)
                # csv.field_size_limit(1000000)
                # csvreader = csv.reader(csvfile)
                # for row in csvreader:
                #     msg = row[0] + ": " + row[1]
                #     result = gptclient.get(msg)
        return result

#
# def main():
#     generator = pitch_generator()
#
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     # csvdir = os.path.join(current_dir, 'output')
#     pitch_dif = os.path.join(current_dir, 'person_descr')
#     for entry in os.listdir(pitch_dif):
#         name, file_extension = os.path.splitext(entry)
#         print("current name", name, "\n\n")
#         res = generator.get(name)
#         print(res)
#
#
# if __name__ == "__main__":
#     main()
