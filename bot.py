import os
from os import environ
import telebot
import requests
import json
import csv

# TODO: 1.1 Add Request HTTP URL of the API

NUTRITIONIX_API_KEY = environ['NUTRITIONIX_API_KEY']
NUTRITIONIX_APP_ID = environ['NUTRITIONIX_APP_ID']
HTTP_API = environ['http_api']
url = 'https://trackapi.nutritionix.com/v2/natural/'


headers = {'Content-Type': 'application/json' ,
           'x-app-id': NUTRITIONIX_APP_ID, 'x-app-key': NUTRITIONIX_API_KEY}
user = {'name': None, 'gender': None,
        'weight': None, 'height': None, 'age': None}
bot = telebot.TeleBot(HTTP_API)


@bot.message_handler(commands=['start', 'hello'])
def greet(message):
    global botRunning
    botRunning = True
    # TODO: 3.1 Add CSV file creation
    csvFile_N = open('Nutrition_Report.csv','w')
    csvFile_E = open('Exercise_Report.csv', 'w')
    csvFile_N.close()
    csvFile_E.close()
    bot.reply_to(
        message, 'Hello! I am TeleFit. Use me to monitor your health'+'\N{grinning face with smiling eyes}'+'\nYou can use the command \"/help\" to know more about me.')


@bot.message_handler(commands=['stop', 'bye'])
def goodbye(message):
    global botRunning
    botRunning = False
    bot.reply_to(message, 'Bye!\nStay Healthy'+'\N{flexed biceps}')


@bot.message_handler(func=lambda message: botRunning, commands=['help'])
def helpProvider(message):
    bot.reply_to(message, '1.0 You can use \"/nutrition Units Quantity-Type Food-Name\" command to get the nutrients of a particular food. For eg: \"/nutrition 1 piece chapati\"\n\n2.1 For using the bot to get details about an exercise you need to first set the user data using the command \"/user Name, Gender, Weight(in Kg), Height (in cm), Age\". For eg: \"/user Akshat, Male, 70, 6, 19\n\n2.2 Then you can use the command \"/execise Duration-amount Duration-unit Exercise-name\" to get data about an exercise. For eg: \"/exercise 40 minutes push-ups\"\n\n3.0. You can use the command \"/reports Report-name\" to get the reports in CSV Format. For eg: \"/reports nutrition\" to get nutrition report and \"/reports exercise\" to get exercise reports or use the command \"/reports nutrition, exercise\" to get both nutrition and exercise reports\n\n4.0. You can use the command \"/stop\" or the command \"/bye\" to stop the bot.')


@bot.message_handler(func=lambda message: botRunning, commands=['user'])
def setUser(message):
    global user
    usr_input = message.text[6:]
    
    # TODO: 2.1 Set user data
    letter = ''
    user_info = []
    for i in range(len(usr_input)) :
        if usr_input[i] == ',' :
            continue
        else :
            letter += usr_input[i]

    letter += ' ' 
    word = ''
    for j in range(len(letter)) :
        if letter[j] != " " :
            word += letter[j]
        else :
            user_info.append(word)
            word = ''
            
    user['name'] = user_info[0]
    user['gender'] = user_info[1]
    user['weight'] = user_info[2]
    user['height'] = user_info[3]
    user['age'] = user_info[4]
    bot.reply_to(message, 'User set!')
    reply = 'Name -> '+str(user['name'])+'\nGender -> '+str(user['gender'])+'\nWeight -> '+str(user['weight'])+'\nHeight -> '+str(user['height'])+'\nAge -> '+str(user['age'])
    # TODO: 2.2 Display user details in the telegram chat
    bot.send_message(message.chat.id, reply)


@bot.message_handler(func=lambda message: botRunning, commands=['nutrition'])
def getNutrition(message):
    bot.reply_to(message, 'Getting nutrition info...')
    # TODO: 1.2 Get nutrition information from the API
    global url, headers
    url = url + 'nutrients'
    query ={"query":str(message.text)[11:]}
    response = requests.post(url, headers=headers, json=query)
    content = json.loads(response.text)
    prefix = content['foods'][0]
    calories = prefix['nf_calories']
    total_fat = prefix['nf_total_fat']
    cholestrol = prefix['nf_cholesterol']
    sodium = prefix['nf_sodium']
    potassium = prefix['nf_potassium']
    total_carbohydrate =  prefix['nf_total_carbohydrate']
    proteins = prefix['nf_protein']        
    
    # TODO: 1.3 Display nutrition data in the telegram chat
    bot.send_message(message.chat.id, "Calories-> "+str(calories).rjust(14)+'g\nFats-> '+str(total_fat).rjust(19)+'g\nCholestrol-> '+str(cholestrol).rjust(6)+'g\nSodium-> '+str(sodium).rjust(15)+'g\nPotassium-> '+str(potassium).rjust(9)+'g\nCarbohydrate-> '+str(total_carbohydrate).rjust(2)+'g\nProteins-> '+str(proteins).rjust(12)+'g')

    # TODO: 3.2 Dump data in a CSV file
    
    csvFile_N = open('Nutrition_Report.csv','w')
    csvWriter = csv.DictWriter(csvFile_N,['Calories','Fats','Cholesterol','Sodium','Potassium','Carbohydrate','Proteins'] )
    csvWriter.writeheader()
    csvWriter.writerow({'Calories':calories, 'Fats': total_fat, 'Cholesterol' : cholestrol, 'Potassium': potassium, 'Carbohydrate': total_carbohydrate, 'Proteins': proteins})
    csvFile_N.close()
@bot.message_handler(func=lambda message: botRunning, commands=['exercise'])
def getCaloriesBurn(message):
    bot.reply_to(message, 'Estimating calories burned...')
    # TODO: 2.3 Get exercise data from the API
    global url, headers
    url = url + 'exercise'                                
    query ={"query":str(message.text)[10:],
    "gender":user['gender'],
    "weight_kg":user['weight'],
    "height_cm":user['height'],
    "age":user['age']
    }   
    
    response = requests.post(url, headers=headers, json=query)
    content = json.loads(response.text)
    prefix = content['exercises'][0]
    calories_burnt = prefix['nf_calories']    
    
    # TODO: 2.4 Display exercise data in the telegram chat
    bot.send_message(message.chat.id, 'Calories Burnt\N{fire} '+str(calories_burnt)+'Kcal')
    
    # TODO: 3.3 Dump data in a CSV file
    
    csvFile_E = open('Nutrition_Report.csv','w')  
    csvWriter = csv.DictWriter(csvFile_E,['Calories Burnt'])
    csvWriter.writeheader()
    csvWriter.writerow({'Calories Burnt':calories_burnt}) 
    csvFile_E.close()
@bot.message_handler(func=lambda message: botRunning, commands=['reports'])
def getCaloriesBurn(message):
    bot.reply_to(message, 'Generating report...')
    # TODO: 3.4 Send downlodable CSV file to telegram chat
    
    txt = str(message.text)[10:]
    letter = ''
    txt = txt + ' '
    req = []
    for i in range(len(txt)):
        if txt[i] != ' ' :
            letter += txt[i]
        else : 
            req.append(letter)
            letter = ''
    if len(req) == 2 :
        doc_N = open('Nutrition_Report.csv', 'rb')
        doc_E = open('Exercise_Report.csv', 'rb')
        bot.send_document(message.chat.id, doc_N)
        bot.send_document(message.chat.id, doc_E)
        file_id_N = 'Nutrition Report'
        file_id_E = 'Exercise Report'
        bot.send_document(message.chat.id, file_id_N)
        bot.send_document(message.chat.id, file_id_E)
        doc_N.close()
        doc_E.close()
    elif len(req) == 1 :
        if req[0] == 'nutrition' :
            doc_N = open("Nutrition_Report.csv","rb")
            c_id = message.chat.id
            bot.send_document(c_id,doc_N)
            file_id_N = 'Nutrition Report'
            bot.send_document(message.chat.id, file_id_N)
            doc_N.close()
        else :
            doc_E = open('Exercise_Report.csv', 'rb')
            bot.send_document(message.chat.id, doc_E)
            file_id_E = 'Exercise Report'
            bot.send_document(message.chat.id, file_id_E)
            doc_E.close()
    else :
        bot.send_message(message.chat.id, "Exceeding inputs received\n Max No.of Reports = 2")


@bot.message_handler(func=lambda message: botRunning)
def default(message):
    bot.reply_to(message, 'I did not understand '+'\N{confused face}')


bot.infinity_polling()
