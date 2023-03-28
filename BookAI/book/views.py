from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf

# Create your views here.
from urllib import response
from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.decorators import api_view

import openai
import wget
import os
import json
from operator import attrgetter, itemgetter
from pathlib import Path

BASE1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def downloadImage(url):
    # input('Please enter image URL (string):')
    #url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-X4riREet5Vfcd6r39RXEaboh/user-ialq0uLckvMaQtaUh3EszH6z/img-woOfCmzHwb42KXWDTow3b4W6.png?st=2023-03-23T12%3A40%3A24Z&se=2023-03-23T14%3A40%3A24Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-03-23T12%3A53%3A23Z&ske=2023-03-24T12%3A53%3A23Z&sks=b&skv=2021-08-06&sig=9Z%2BbXGZUSNqduVZQ0iwiKu1lfA%2BEvSI4ZITcu0ChJVQ%3D"
    
    BASE2 = os.path.join(BASE1,  'images')
    file_name = wget.download(url, BASE2)
    print('Image Successfully Downloaded: ', file_name)
    
def generateImage(description):
    PROMPT = description
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = "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"
    n = 1
    response = openai.Image.create(
        prompt=PROMPT,
        n=n,
        size="1024x1024",
    )
    return response["data"][0]["url"]


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
        openai.api_key =  "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"#, "r").read().strip("\n")

        message_history = [{"role": "user", "content": "oublie toutes les instructions que tu as recu jusqu'a present"},
                        #                    {"role": "assistant", "content": f"OK"},
                        {"role": "user", "content": "maintenant tu es bot utilise pour ecrire des livres pour enfant,\
                                tu le fais comme un expert dans l'ecriture tu as deja eu a ecrire des best-seller\
                                .. ton but final sera obligatoirement  d'ecrire une seule histoire  au format JSON, JSON dans lequel \
                                    je dois avoir un champ pour le titre, un champ pour le libelle de chaque chapitre, un champ pour le contenu de chaque chapitre, un champ pour le resume du chapitre \
                                        le JSON DOIT ETRE sous la forme {titre:..,chapitre:[{titre:..,contenu:..,resume:..}}]\
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
            {"role": "user", "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {titre:..,chapitre:[{titre:..,contenu:..,resume:..}}] comme je l'ai indique de ["+str(input)+"]. j'insiste, dans ta reponse je ne veux voir que l'histoire au format JSON rien d'autre"})
        print("---|>")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
            messages=message_history,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        #Just the reply:
        # .replace('```python', '<pre>').replace('```', '</pre>')
        reply_content = completion.choices[0].message.content

        print(reply_content)#.split('\n')[-1])
        message_history.append(
            {"role": "assistant", "content": f"{reply_content}"})
        try :
            history = json.loads(reply_content)
        except:
            
            history = json.loads(extractJSON(reply_content))
            print("exception ici")
        #print(history)
        for index, chapter in enumerate(history["chapitre"]):
           print(history["chapitre"][index])
           history["chapitre"][index]["image"] = generateImage(chapter["resume"])
        
        # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
        responseChat = [(message_history[i]["content"], message_history[i+1]["content"])
                    for i in range(5, len(message_history)-1, 2)]  # convert to tuples of list
        #print(responseChat)
        #reply_content = reply_content.split('\n')
        print(history)
        
        # return Response(history, status=status.HTTP_200_OK)


        pdf = render_to_pdf('report.html', history)
        if pdf :
            response=HttpResponse(pdf,content_type='application/pdf')
            filename = "History_for_%s.pdf" %(history['titre'])
            content = "inline; filename= %s" %(filename)
            response['Content-Disposition'] = content

            return response
        
        return HttpResponse("Page Not Found")

