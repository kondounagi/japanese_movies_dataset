import unicodedata
import sys 

in_file = open("2018_movie_raw", "r")
year = 2018
month = 0
day = 0
for line in in_file.readlines():
    line = line.strip()
    if line[len(line) - 1] == '月':
        month = 0
        for i in range(len(line) - 1):
            month = month * 10 + int(line[i:i+1])
        
    elif line[len(line) - 1] == '日':
        day = 0
        for i in range(len(line) - 1):
            day = day * 10 + int(line[i:i+1])
        
    else:
        
        end = len(line)
        for i in range(len(line)):

            if (line[len(line) - i - 1] == '(' or line[len(line) - 1 - i] == '（'):
                end = len(line) - i - 1
                break
        
        line = line[0:end].strip()
        line = unicodedata.normalize('NFC', line)
        print(line, year, month, day)
                    
    




    

