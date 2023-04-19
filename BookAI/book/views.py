from django.shortcuts import render

# Create your views here.
from urllib import response
from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .utils import render_to_pdf
from django.http import HttpResponse
import openai
import wget
import replicate
import os
import json
from operator import attrgetter, itemgetter
from pathlib import Path
import time

BASE1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY = "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"
def downloadImage(url):
    # input('Please enter image URL (string):')
    #url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-X4riREet5Vfcd6r39RXEaboh/user-ialq0uLckvMaQtaUh3EszH6z/img-woOfCmzHwb42KXWDTow3b4W6.png?st=2023-03-23T12%3A40%3A24Z&se=2023-03-23T14%3A40%3A24Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-03-23T12%3A53%3A23Z&ske=2023-03-24T12%3A53%3A23Z&sks=b&skv=2021-08-06&sig=9Z%2BbXGZUSNqduVZQ0iwiKu1lfA%2BEvSI4ZITcu0ChJVQ%3D"
    
    BASE2 = os.path.join(BASE1,  'images')
    file_name = wget.download(url, BASE2)
    print('Image Successfully Downloaded: ', file_name)
    
def generateImage(description):
    PROMPT = description +" dans un style fantaisiste tire des livres pour enfant"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = API_KEY
    nb = 1
    response = openai.Image.create(
        prompt=PROMPT,
        n=nb,
        size="1024x1024",
    )
    return response["data"][0]["url"]

    # os.environ["REPLICATE_API_TOKEN"] = "r8_MswN94B3MKFIovKe8KXg1YNliBNZiNj1eCpid"

    # output = replicate.run(
    #     "prompthero/openjourney:9936c2001faa2194a261c01381f90e65261879985476014a0a37a334593a05eb",
    #     input={"prompt": f"mdjrny-v4 style description, {description} 4 k resolution, trending on artstation, masterpiece"}

    # )
    # return output


def extractJSON(value):
    firstIndex = 0
    lastIndex = 0
    for index, cha in enumerate(value):
        if cha == "{" and firstIndex == 0:
            firstIndex = index
        if (cha == "}"):
            lastIndex = index
    return value[firstIndex: lastIndex+1]

class WriteBook(APIView):
    def post(self, request):
        input = request.data['content']
        print(f"voici l'input {input}")
        print(Path(__file__).resolve(
        ).parent / "key.txt")
        # , "r").read().strip("\n")
        openai.api_key = API_KEY

        message_history = [{"role": "user", "content": "oublie toutes les instructions que tu as recu jusqu'a present"},
                        #                    {"role": "assistant", "content": f"OK"},
                        {"role": "user", "content": "maintenant tu es bot utilise pour ecrire des livres pour enfant,\
                                tu le fais comme un expert dans l'ecriture tu as deja eu a ecrire des best-seller\
                                .. ton but final sera obligatoirement  d'ecrire une seule histoire  au format JSON, JSON dans lequel \
                                    je dois avoir un champ pour le titre, un champ pour le libelle de chaque chapitre, un champ pour le contenu de chaque chapitre, un champ pour le resume du chapitre \
                                        le JSON DOIT ETRE sous la forme {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]. pour que tu comprennes, l'attribut 'title' correspond au titre du livre ou d'un chapitre; l'attribut 'resumeHistory' est le resume de l'histoire en seule phrase\
                                           un chapitre est subdivise en paragraphes et chaque paragraphe est un element l'attribut paragraphs, qui est un tableau ]\
                            si tu as compris ecris OK"},
                        {"role": "assistant", "content": "OK"},
                        #  {"role": "assistant", "content": "faites une description de votre livre"},
                        {"role": "assistant",
                            "content": "salut"},
                        {"role": "system",
                            "content": "presentes toi"},
                        ]


        # tokenize the new input sentence
        message_history.append(
            {"role": "user", "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {title:..,resumeHistory:..,chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]; j'insiste, l'histoire devra parler de ["+str(input)+"] en minimum 10 chapitres et chaque chapitre doit avoir minimum 5 paragraphes. Le contenu de chaque paragraphes devra etre une narration detaillee de plus de 1000 mots avec un vocabulaire émotif et dans ta reponse je ne veux voir que l'histoire au format JSON tout respectant les specifications que j'ai donne rien d'autre et ne numero pas les titres des chapitres. "})
            
        print("---|>")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
            messages=message_history,
            temperature=0.3,
            max_tokens=3000,
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=0
        )
        #Just the reply:
        # .replace('```python', '<pre>').replace('```', '</pre>')
        reply_content = completion.choices[0].message.content
        i = 0
        print(reply_content)#.split('\n')[-1])
        message_history.append(
            {"role": "assistant", "content": f"{reply_content}"})
        try :
            history = json.loads(reply_content)
        except:
            
            history = json.loads(extractJSON(reply_content))
            print("exception ici")
        #print(history)
        try:
            history["resumeImage"] = generateImage(history["resumeHistory"])
            for index, chapter in enumerate(history["chapter"]):
                print(history["chapter"][index])
                history["chapter"][index]["image"] = generateImage(chapter["resume"])
                history["chapter"][index]["title"] = history["chapter"][index]["title"].str.lower().replace('chapitre ','')
                for ind, paragraph in enumerate(chapter["paragraphs"]):
                    #history["chapters"][index]["paragraphs"]
                    # if i%6==0 and i!=0:
                    #     print('\n')
                    #     print('sleep :(')
                    #     print('\n')
                    #     time.sleep(63)
                    print('that is text '+str(history["chapter"][index]["paragraphs"][ind]["text"]))
                    try:
                        paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])
                    except : 
                        print('\n')
                        print('sleep :(')
                        print('\n')
                        time.sleep(63)
                        paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])
                    
        except :
            for index, chapter in enumerate(history["chapters"]):
                print(history["chapters"][index])
                history["chapters"][index]["image"] = generateImage(chapter["resume"])
                history["chapters"][index]["title"] = history["chapters"][index]["title"].str.lower().replace('chapitre ','') 
                for ind, paragraph in enumerate(chapter["paragraphs"]):
                    
                    print('that is text '+str(history["chapters"][index]["paragraphs"][ind]["text"]))
                    try:
                        paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])
                    except : 
                        print('\n')
                        print('sleep :(')
                        print('\n')
                        time.sleep(63)
                        paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])
                    
        # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
        responseChat = [(message_history[i]["content"], message_history[i+1]["content"])
                    for i in range(5, len(message_history)-1, 2)]  # convert to tuples of list
        #print(responseChat)
        #reply_content = reply_content.split('\n')
        print(history)
        return Response(history, status=status.HTTP_200_OK)
        

def index(request) :
    return render(request, 'index.html')

class GeneratePDF(APIView) :
    def get(self, request, *args, **kwargs) :
        pdf = render_to_pdf('sample.html')
        return HttpResponse(pdf, content_type='application/pdf')