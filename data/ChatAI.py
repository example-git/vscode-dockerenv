import nest_asyncio
nest_asyncio.apply()
import asyncio
import distutils
import distutils.util
import os
import random
import re
import data.helper as helper
from aitextgen import aitextgen
from data.helper import activesettings
import data.lists as lists
global settingsfile, debug


activesettings()
togpu = bool(distutils.util.strtobool(helper.togpu))
gpt2 = aitextgen(model_folder=helper.modelfolder, to_gpu=togpu)
    
    
def generate(self, numtokens, receivedmessage):
    output = gpt2.generate(
        max_length=numtokens + 100,
        prompt=receivedmessage + "\r\n",
        do_sample=True,
        top_p=0.85,
        top_k=0,
        repetition_penalty=1.1,
        return_as_list=True
    )
    return output


def generatecustom(self, numtokens, receivedmessage):
    output = gpt2.generate(
        max_length=numtokens + 100,
        prompt=receivedmessage + "\r\n",
        do_sample=True,
        top_p=0.85,
        top_k=0,
        repetition_penalty=1.1,
        return_as_list=True
    )
    return output


class ChatAI:
    def __init__(self, processed_input=None) -> None:
        activesettings()
        togpu = bool(distutils.util.strtobool(helper.togpu))
        self.model_folder = helper.modelfolder
        self.maxlines = int(helper.maxlines)
        self.debug = int(helper.debug)
        self.togpu = togpu
        self.prefix = str(helper.prefix)
        self.gpt2 = gpt2
        if not os.path.isdir(f"{self.model_folder}"):
            raise Exception(
                f"You need to train the model first. Do this in colab or locally and make sure the finished model is in a folder called \"{modelfolder}\".")

    def get_bot_response(self, receivedmessage):
        """ Get a processed response to a given message using GPT model """
        self.custommsg = False
        old_msgs = ""
        old_msgs = receivedmessage.split('\r\n')
        oldmsg = []
        for m in old_msgs:
            oldmsg.append(m)
        self.oldmsg = oldmsg
        # oldmsg.append(str(message + "\r\n"))
        print(" ", flush=True)
        print("============================+CONTEXT+============================", flush=True)
        print(receivedmessage, flush=True)
        print("============================+CONTEXT+============================", flush=True)
        print(" ", flush=True)
        if self.debug == 1:
            print("==============================DEBUG==============================", flush=True)
            print(oldmsg, flush=True)
            print("===========================OLDMSG-LOG============================", flush=True)
        numtokens = len(gpt2.tokenizer(receivedmessage)["input_ids"])
        if self.debug == 1:
            print(" ", flush=True)
            print("Num Tokens: ", flush=True)
            print(numtokens, flush=True)
            print(" ", flush=True)
        if numtokens >= 1000:
            while numtokens >= 1000:
                receivedmessage = ' '.join(receivedmessage.split(' ')[20:])  # pretty arbitrary
                numtokens = len(self.gpt2.tokenizer(receivedmessage)["input_ids"])
        generateout = generate(self, numtokens=numtokens, receivedmessage=receivedmessage)
        formatted = self.formatmessage(outputtext=generateout)
        return formatted

    def get_bot_custom(self, receivedmessage):
        """ Get a processed response to a given message using GPT model """
        self.custommsg = True
        old_msgs = ""
        old_msgs = receivedmessage.split('\r\n')
        oldmsg = []
        cleaned = []
        for m in old_msgs:
            oldmsg.append(m)
            if m.startswith(f"{self.prefix}gen"):
                continue
            cleaned.append(m)
        cleaned2 = ""
        for c in cleaned:
            c = c.replace('? ', '. ')
            c = c.replace('! ', '. ')
            cleaned2 += str(c)
        cleaned3 = ""
        cleaned3 = cleaned2.split('. ')
        cleanedtxt = ""
        for c in cleaned3:
            oldmsg.append(c + ".")
            cleanedtxt += str(c + ".\r\n")
        self.oldmsg = oldmsg
        print(" ", flush=True)
        print("============================+CONTEXT+============================", flush=True)
        print(cleanedtxt, flush=True)
        print(receivedmessage, flush=True)
        print("============================+CONTEXT+============================", flush=True)
        print(" ", flush=True)
        if self.debug == 1:
            print("==============================DEBUG==============================", flush=True)
            print(cleaned, flush=True)
            print(cleaned2, flush=True)
            print(cleaned3, flush=True)
            print(oldmsg, flush=True)
            print("===========================OLDMSG-LOG============================", flush=True)
        numtokens = len(self.gpt2.tokenizer(cleanedtxt)["input_ids"])
        print(numtokens)
        if self.debug == 1:
            print(" ", flush=True)
            print("Num Tokens: ", flush=True)
            print(numtokens, flush=True)
            print(" ", flush=True)
        if numtokens >= 1000:
            while numtokens >= 1000:
                cleaned = ' '.join(cleanedtxt.split(' ')[20:])  # pretty arbitrary
                numtokens = len(self.gpt2.tokenizer(cleanedtxt)["input_ids"])
        generateout = generatecustom(self, numtokens=numtokens, receivedmessage=cleanedtxt)
        formatted = self.formatmessage(outputtext=generateout)
        return formatted

    def formatmessage(self, outputtext):
        outputlist = []
        noclones = []
        link = []

        for i, text in enumerate(outputtext):
            outputlist = str(text).split("\r\n")

        if self.custommsg:
            self.custommsg = False
            for i in outputlist:
                if i not in self.oldmsg:
                    linkcheck = re.search(lists.link, i)
                    if linkcheck is None:
                        noclones.append(i)
            try:
                last = noclones[0:1]
            except:
                last = noclones[:-1]
        else:
            for i in outputlist:
                if i not in self.oldmsg:
                    linkcheck = re.search(lists.link, i)
                    if linkcheck is None:
                        noclones.append(i)
                    else:
                        link.append(i + "\r\n")
            c = random.randint(-int(self.maxlines), -2)
            try:
                last = noclones[c:-1]
            except:
                last = noclones[0:3]
            if self.debug == 1:
                print("Num Lines:", flush=True)
                print(c, flush=True)
                print(" ", flush=True)

        if self.debug == 1:
            print("==============================DEBUG==============================", flush=True)
            print(f"Output ({len(outputlist)}): " + str(outputlist), flush=True)
            print(f"Noclones({len(noclones)}): " + str(noclones), flush=True)
            print(f"Cleaned ({len(last)}): " + str(last), flush=True)
            print("============================CLONE-LOG============================", flush=True)

        formatted = ""

        final = []
        for i in last:
            b = random.randint(0, 20)
            for key, value in lists.replacements.items():
                i = i.replace(key, value)
            for p in lists.punctuation:
                if i.endswith(p):
                    final.append(str(i).capitalize() + " ")
                    break
                if p == ']':
                    final.append((str(i).capitalize()) + lists.endinglist[b])

        done = []

        for msg in final:
            # "context" now becomes a big string containing the content only of the last n messages, line-by-line
            if msg.startswith("!") or msg.startswith("e!") or msg.startswith("$") or msg.startswith(self.prefix):
                continue
            done.append(str(msg))

        if 0 < len(link) <= 1:
            for saved in link:
                done.append(str(saved))
        else:
            done = final

        for f in done:
            formatted += str(f)
        
        if self.debug == 1:
            print("==============================DEBUG==============================", flush=True)
            print(f"Final ({len(final)}): " + str(final), flush=True)
            print(f"Links ({len(link)}): " + str(link), flush=True)
            print(f"Done ({len(done)}): " + str(done), flush=True)
            print("==========================Final and Last=========================", flush=True)
        
        print(" ", flush=True)
        print("============================+RESPONSE+===========================", flush=True)
        print(formatted, flush=True)
        return formatted