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
import requests
# from models import Image, History
from book.models import Image,History
from rest_framework.viewsets import ModelViewSet
from book.serializers import ImageSerializer, HistorySerializer
from rest_framework import generics


BASE1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY = ""
token = ""
URL = "https://api.thenextleg.io/v2/"
nameButton = 'U3'
webHookUrl = "https://feb3-185-107-56-156.eu.ngrok.io/image/"

def downloadImage(url):
    # input('Please enter image URL (string):')
    #url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-X4riREet5Vfcd6r39RXEaboh/user-ialq0uLckvMaQtaUh3EszH6z/img-woOfCmzHwb42KXWDTow3b4W6.png?st=2023-03-23T12%3A40%3A24Z&se=2023-03-23T14%3A40%3A24Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-03-23T12%3A53%3A23Z&ske=2023-03-24T12%3A53%3A23Z&sks=b&skv=2021-08-06&sig=9Z%2BbXGZUSNqduVZQ0iwiKu1lfA%2BEvSI4ZITcu0ChJVQ%3D"
    
    BASE2 = os.path.join(BASE1,  'images')
    file_name = wget.download(url, BASE2)
    print('Image Successfully Downloaded: ', file_name)
    
def generateImage(description, previousUrl=""):
    """cette fonction prend 2 parametres la premiere est le prompt dont on souhaite generer l'illustration 
    et le second est un parametre qui n'est pas obligatoire, c'est l'url d'une image qui est utilise avec le premier parametre
    pour generer une illustration.
    """
    print(str(previousUrl)+" is the next previous URL")
    # try:
    #     PROMPT = description +" dans un style fantaisiste tire des livres pour enfant"
    #     openai.api_key = os.getenv("OPENAI_API_KEY")
    #     openai.api_key = API_KEY
    #     nb = 1
    #     response = openai.Image.create(
    #         prompt=PROMPT,
    #         n=nb,
    #         size="1024x1024",
    #     )
    #     return response["data"][0]["url"]
    # except:
    #     return 'https://resize.elle.fr/original/var/plain_site/storage/images/loisirs/cinema/dossiers/dessin-anime-enfant/53838996-1-fre-FR/15-dessins-animes-cultes-a-re-voir-avec-ses-enfants.jpg'
    url = URL+"imagine"
    input = str(description) +"without any text, children’s story book, The disney cartoon, colorful , fantaisist style, 4k, on a white background"
    print('that is the input '+str(input))
    # imageLink = None
    # if previousText != "":
    #     while imageLink is None:
    #         print("\n")
    #         print("------> In the while <------")
    #         imageMidjourney = Image.objects.all()#.filter(originatingMessageId = "H06rqfzNjg2wKl0mDFP3")
    #         for d in imageMidjourney:
    #             if previousText in str(ImageSerializer(d).data["content"]):
    #                 if not nameButton in str(ImageSerializer(d).data["buttons"]):
    #                     imageLink = ImageSerializer(d).data["imageUrl"]
    payload = json.dumps({
    "cmd": "imagine",
    "msg": str(previousUrl)+ ' ' + input if previousUrl!="" else input,
    "ref": "",
    "webhookOverride": webHookUrl
    })
    headers = {
    'Authorization': 'Bearer '+str(token),
    'Content-Type': 'application/json'
    }
    # token : https://hook.eu1.make.com/20r1hloyjc991zcbrgqd5jn4fon4hfxs
    response = requests.request("POST", url, headers=headers, data=payload)
    #find text wich content text
    imageLink = None
    while imageLink is None:
        # print("\n")
        # print("------> In the while <------")
        imageMidjourney = Image.objects.all()#.filter(originatingMessageId = "H06rqfzNjg2wKl0mDFP3")
        for d in imageMidjourney:
            if description in str(ImageSerializer(d).data["content"]):
                if not nameButton in ImageSerializer(d).data["buttons"]:
                    print("\n")
                    print("image "+str(ImageSerializer(d).data["imageUrl"])+" Found")
                    print(":)")
                    imageLink = ImageSerializer(d).data["imageUrl"]
    
    return imageLink



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
    #http_method_names = ['get','head','put','delete']
    
    # def get(self,request,*args,**kwargs):
    #     images=Image.objects.all()
    #     ImageSerialize=ImageSerializer(images)
    #     print("voici le serializer")
    #     print(ImageSerialize.data)
    #     return Response(ImageSerialize.data)
        
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
                                        le JSON DOIT ETRE sous la forme {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]. pour que tu comprennes, l'attribut 'title' correspond au titre du livre ou d'un chapitre (celui d'un chapitre se fait en seul mot); l'attribut 'resumeHistory' est le resume de l'histoire en seule phrase\
                                           un chapitre est subdivise en paragraphes et chaque paragraphe est un element l'attribut paragraphs, qui est un tableau \
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
            {"role": "user", "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {title:..,resumeHistory:..,chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]; j'insiste, l'histoire devra parler de ["+str(input)+"] en minimum 10 chapitres et chaque chapitre doit avoir minimum 5 paragraphes. Le contenu de chaque paragraphes devra etre une narration detaillee de plus de 1000 mots avec un vocabulaire émotif et dans ta reponse je ne veux voir que l'histoire au format JSON tout respectant les specifications que j'ai donne rien d'autre et les titres des chapitres qui doivent etre des mots ne doivent pas etre numerotes. "})
            
        print("---|>")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
            messages=message_history,
            temperature=0.3,
            max_tokens=4000,
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
        print("\n")
        print("\n")
        print("histoire avant ajout des images")
        print(history)
        print("\n")
        print("\n")
        print("\n")
        
        try:
            history["resumeImage"] = generateImage(history["resumeHistory"])
            for index, chapter in enumerate(history["chapter"]):
                print(history["chapter"][index])
                history["chapter"][index]["image"] = generateImage(chapter["resume"], history["resumeImage"])
                history["chapter"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','')
                for ind, paragraph in enumerate(chapter["paragraphs"]):
                    print('that is text '+str(history["chapter"][index]["paragraphs"][ind]["text"]))
                    if ind == 0:
                        paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["illustration"], chapter["image"])
                    else:
                        paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["illustration"], chapter["paragraphs"][ind-1]["illustration"])
                    # try:
                    #     paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])
                    # except : 
                    #     print('\n')
                    #     print('sleep :(')
                    #     print('\n')
                    #     time.sleep(63)
                    #     paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])
                    
        except : #case which we have chapters instead of chapter
            for index, chapter in enumerate(history["chapters"]):
                print(history["chapters"][index])
                history["chapters"][index]["image"] = generateImage(chapter["resume"], history["resumeHistory"])
                history["chapters"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','') 
                for ind, paragraph in enumerate(chapter["paragraphs"]):
                    
                    print('that is text '+str(history["chapters"][index]["paragraphs"][ind]["text"]))
                    if ind == 0:
                        paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["illustration"], chapter["image"])
                    else:
                        paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["illustration"], chapter["paragraphs"][ind-1]["illustration"])
                    
                    # try:
                    #     paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])
                    # except : 
                    #     print('\n')
                    #     print('sleep :(')
                    #     print('\n')
                    #     time.sleep(63)
                    #     paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])
                    
        # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
        responseChat = [(message_history[i]["content"], message_history[i+1]["content"])
                    for i in range(5, len(message_history)-1, 2)]  # convert to tuples of list  Hayao Miyazaki's cartoon
        
        new_history= History.objects.create(content = str(history))
        new_history.save()
        
        
        print("\n")
        print("\n")
        print("histoire apres ajout des images :)")
        print(history)
        print("\n")
        print("\n")
        print("\n")
        print(history)
        
        
        
        return Response(history, status=status.HTTP_200_OK)

class GenerateImageMidjourney(generics.ListAPIView):
    def get(self, request):
        url = URL+"imagine"
        input = str(request.data['content']) +" "+"without any text, children’s story book, The little prince cartoon, colorful , fantaisist style, 4k, on a white background"
        print('that is the input '+str(input))
        payload = json.dumps({
        "cmd": "imagine",
        "msg": input,
        "ref": "",
        "webhookOverride": webHookUrl
        })
        headers = {
        'Authorization': 'Bearer '+str(token),
        'Content-Type': 'application/json'
        }
        # token : https://hook.eu1.make.com/20r1hloyjc991zcbrgqd5jn4fon4hfxs
        response = requests.request("POST", url, headers=headers, data=payload)
        return Response(response, status=status.HTTP_200_OK)
        # return Response(ImageSerializer(imageMidjourney, many=True).data)
        
        
        
        # history = request.data
        # history["resumeImage"] = generateImage(history["resumeHistory"])
        # for index, chapter in enumerate(history["chapters"]):
        #         print(history["chapters"][index])
        #         history["chapters"][index]["image"] = generateImage(chapter["resume"], history["resumeHistory"])
        #         history["chapters"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','') 
        #         for ind, paragraph in enumerate(chapter["paragraphs"]):
                    
        #             print('that is text '+str(history["chapters"][index]["paragraphs"][ind]["text"]))
        #             if ind == 0:
        #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"], chapter["image"])
        #             else:
        #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"], chapter["paragraphs"][ind-1]["illustration"])
                           
        # return history
    
    def post(self, request):
        webHookData = None
        print("Donnee recu de thenextleg")
        print(request.data)
        print('\n')
        print('\n')
        print('\n')
        print('\n')
        print('that is image')
        url = URL+"button"
        webHookData = request.data
        print(webHookData)
        new_image = None
        if not 'U1' in webHookData["buttons"]:
            new_image= Image.objects.create(buttons = webHookData["buttons"],
                                            imageUrl = webHookData["imageUrl"],
                                            buttonMessageId = webHookData["buttonMessageId"],
                                            originatingMessageId = webHookData["originatingMessageId"],
                                            content = webHookData["content"]
                                            )
            
            new_image.save()
 
        serializer=ImageSerializer(new_image)
        #request for get the image for specific button
        if 'U1' in webHookData["buttons"] or 'U2' in webHookData["buttons"] or 'U3' in webHookData["buttons"]or 'U4' in webHookData["buttons"] :
            print("\n")
            print("---->")
            payload = json.dumps({
            "button": nameButton,
            "buttonMessageId": webHookData["buttonMessageId"],
            "ref": "",
            "webhookOverride": webHookUrl
            })
            headers = {
            'Authorization': 'Bearer '+str(token),
            'Content-Type': 'application/json'
            }
            # token : https://hook.eu1.make.com/20r1hloyjc991zcbrgqd5jn4fon4hfxs
            response = requests.request("POST", url, headers=headers, data=payload)
            new_image= Image.objects.create(buttons = webHookData["buttons"],
                                            imageUrl = webHookData["imageUrl"],
                                            buttonMessageId = webHookData["buttonMessageId"],
                                            originatingMessageId = webHookData["originatingMessageId"],
                                            content = webHookData["content"],
                                            )
            
            new_image.save()
        return Response(webHookData["imageUrl"], status=status.HTTP_200_OK)

def index(request) :
    return render(request, 'index.html')

class GeneratePDF(APIView) :
    def get(self, request, *args, **kwargs) :
        pdf = render_to_pdf('sample.html')
        return HttpResponse(pdf, content_type='application/pdf')