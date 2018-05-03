import json
import sys
import operator
from pprint import pprint
from collections import defaultdict
resultString=""

def openJSONFile():
   print("Loading the JSON File")
   data=json.load(open('hmmmodel.txt'))
   with open("hmmoutput.txt",'w',encoding='utf-8') as file:
   		file.truncate()
   return data


def writeToFile(resultString):
    with open("hmmoutput.txt",'a',encoding='utf-8') as file:
        file.write(resultString)


def findBackPointers(dictionary_keywords,words):

    resultString=""

    for i,word in enumerate(reversed(words)):
        if(i==0):
            maxValue=-1
            for uniqueTag in dictionary_keywords:
                for currentTag in dictionary_keywords[uniqueTag]:
                    tuple = dictionary_keywords[uniqueTag][currentTag]

                    currentValue=tuple[0]
                    previousTag=tuple[1]
                    currentWord=tuple[2]
                    if(uniqueTag==len(words)-i):
                        #print("current val" +str(currentValue))
                        if(currentValue>=maxValue):
                            maxValue=currentValue
                            tagForWord=currentTag
                            backPointer=previousTag
            #print("assigning tag for word" + word +"and tag is"+ tagForWord)
            #exit()

            #print("backpointer is" + backPointer)
            resultString+=word+"/"+tagForWord+" "
        else:
            for uniqueTag in dictionary_keywords:
               # print("unique tag"+str(uniqueTag))
                for currentTag in dictionary_keywords[uniqueTag]:
                    #print("curent tag" +currentTag)
                    tuple=dictionary_keywords[uniqueTag][currentTag]
                    #print(tuple)
                    previousTag=tuple[1]
                    currentWord=tuple[2]
                    if(currentTag==backPointer and uniqueTag==len(words)-i):
                        prevTag=previousTag
                        #print("prev now" + prevTag)
            resultString+=word+"/"+backPointer+" "
            backPointer=prevTag
    finalString=resultString.split()
    finalString.reverse()
    #print(finalString)
    finalString=" ".join(finalString)+"\n"
    writeToFile(finalString)

def parseTestData(data):
    f = open(sys.argv[1], 'r', encoding="utf-8")
    max_start_value=0
    max_value=0
    chosen_tag=""
    tag_list=[]
    prev_state_values=[]
    starting_tag_list=[]
    joint_dict=dict()
    max_of_lists=[[]]
    max_val_prev=0
    lastIndexTagList=[]  #to calculate stop probabilites.
    lastIndexValueList=[]

    prev_tag_list=[]
    for sentence in f:
        dictionary_keywords=defaultdict(dict)
        tag_list=[]
        words=sentence.split()
        i=0
        max_start_value = 0
        starting_tag_list=[]
        prev_val_list=[]
        prev_state_values=[]
        lastIndexTagList=[]
        lastIndexValueList=[]
        lastWordFlag=0
        uniqueCounter=0
        j=0
        for j,each_word in enumerate(words):
            uniqueCounter+=1
            #print("for the word" + each_word)
            max_value=0
            if(j!=0):
                prev_word=words[j-1]
            if(each_word in data["emission"]):
                tag_values= data["emission"][each_word] #get the corresponding tag values.
                max_value=0
                maxtag=""
                index=0
            else: #change after smoothing.
                #print("Encountered new word!")
                data["emission"][each_word]={}
                #print(data["uniquetags"])
                for alltags in data["uniquetags"]:
                    data["emission"][each_word][alltags]=1
                tag_values=data["emission"][each_word]
            #print("tag values for the word" + each_word +"is" + str(tag_values))
            for tag in tag_values:
                #print("current chosen tag is" + tag)
                joint_dict={}
                if(i==0):
                    if(tag in data["transition"]["start"] and tag in data["emission"][each_word]):
                        start_val=data["transition"]["start"][tag] * data["emission"][each_word][tag]
                        starting_tag_list.append(tag) #refresh for every word.
                        dictionary_keywords[uniqueCounter][tag]=(start_val,"start",each_word)
                        prev_state_values.append(start_val)
                        prev_tag_list=starting_tag_list
                        prev_val_list=prev_state_values
                        #print("dictionary keywords..." +str(dictionary_keywords))
                        continue
                        
                    else:
                        start_val= 0
                        starting_tag_list.append(tag)  #refresh for every word.
                        prev_state_values.append(start_val)
                        prev_tag_list = starting_tag_list
                        prev_val_list = prev_state_values
                        dictionary_keywords[uniqueCounter][tag]=(0,"start",each_word)
                        continue

                else:
                    for every_start_tag,every_prev_value in zip(starting_tag_list,prev_state_values):
                       if(tag in data["transition"][every_start_tag] and tag in data["emission"][each_word]):
                            #print(data["transition"][every_start_tag][tag])
                            #print(data["emission"][each_word][tag])
                            prob_val=float(data["transition"][every_start_tag][tag]* data["emission"][each_word][tag]*every_prev_value)
                            #print("prob val!!!" + str(prob_val))
                            if(i==len(words)-1):
                                #print("last word!")
                                prob_val*=data["transition"]["stop"][tag]
                                #print(data["transition"]["stop"][tag])
                                #print("prob val now" + str(prob_val))

                       elif(tag not in data["transition"][every_start_tag] or tag not in data["transition"][each_word]):
                           prob_val=0

                       if(max_value<=prob_val):
                            max_value=prob_val
                            maxtag=every_start_tag
                            joint_dict.update({maxtag:max_value})
                            maxx_value=max_value
                       max_value=0
                    every_start_tag=max(joint_dict.items(), key = lambda x: x[1])[0]
                    dictionary_keywords[uniqueCounter][tag]=(joint_dict[every_start_tag],every_start_tag,each_word)
                    #print("dict keywords.." + str(dictionary_keywords))

                    k=0
                    prev_tag_list.append(tag)
                    prev_val_list.append(max(joint_dict.values()))
                max_val_prev=0
                max_val_prev=0

                if (i == len(words) - 1):
                    lastIndexTagList.append(tag)
                    lastWordFlag=1
                    lastIndexValueList.append(prob_val)

            max_last_value=0

            starting_tag_list=prev_tag_list
            prev_state_values=prev_val_list

            max_start=0

            #handling sentences with a single word.
            if(len(words)==1):
                for first_tag,first_value in zip(starting_tag_list,prev_state_values):
                    if(first_value>=max_start):
                        max_start=first_value
                        max_first_tag=first_tag

            prev_tag_list=[]  #refresh
            prev_val_list=[]  #refresh
            i+=1
            if (lastWordFlag == 1): #take care of the stop states
                #print("Last state")
                max_last_value=0
                for last_tag, last_value in zip(lastIndexTagList, lastIndexValueList):
                    #print("last value" + str(last_value))
                    if (last_value >= max_last_value):
                        max_last_value = last_value
                        max_last_tag = last_tag
                        #print(max_last_tag)

                break
        findBackPointers(dictionary_keywords,words)


   
if __name__ == '__main__':
        data = openJSONFile()
        parseTestData(data)
        print("successfully done")