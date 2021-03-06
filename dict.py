import firebase_admin, json, datetime, os, sys
from firebase_admin import credentials, firestore
from jsondiff import diff

path = '/home/qniff/de/Scripts/dict'
path_off = path + '/add/dict.json'
path_db = path + '/add/dict.db'
path_cred = path + '/add/cred.json'

def main():
  doc_off = json.load(open(path_off, 'r'))
  counter = len(doc_off)
  sync = ''
  goal = ''
  new = ''

  try:
    if sys.argv[1] == '-l' or sys.argv[1] == '-ll':
      goal = sys.argv[1]
    if sys.argv[1] == '-s':
      goal = sys.argv[2]
    if sys.argv[1][0] != '-':
      new = sys.argv[1]
      
  except:
    None

  try:
    # connection
    cred = credentials.Certificate(path_cred)
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    doc_ref = db.collection(u'phrases').document(u'main')

    # docs + difference
    doc_on = doc_ref.get().to_dict()
    difference = diff(doc_on, doc_off)

    # device is ahead
    if len(doc_on) < counter:
      sync = 'db'
      counter = len(doc_on)
      while counter < len(doc_off):
        updateOn(doc_ref, difference[str(counter)], counter)
        counter += 1

    # db is ahead
    elif len(doc_on) > counter:
      sync = 'device'
      syncOff(doc_on)
      counter += len(difference)
    
    # info
    if sync != '': print('^ Synchronized ' + sync)
    
    # functionalities
    work(goal, new, doc_ref, counter)

    storeSize(doc_on)
      
  except:
    print('^ Warning: no internet\n')
    # proceed
    work(goal, new, doc_ref, counter)
  

def getData():
  phrase = input('Phrase: ')
  if(wordExists(phrase)):
    print('This word already exists')
  else:
    return getMeaning(phrase, 'Meaning')
  
def getMeaning(phrase, text):
  meaning = input(text + ': ')
  now = datetime.datetime.now()
  date_entry = '{}/{}/{} {}:{}'.format(now.day, now.month, now.year, now.hour, now.minute)
  new_data = {
    'meaning': meaning,
    'date': date_entry,
    'phrase': phrase,
  }
  return new_data

def work(goal, new, doc_ref, counter):
  if goal == '':

    if new == '':
      # Usual case, add new phrase
      new_data = getData()
      updateOn(doc_ref, new_data, counter)
      updateOff(new_data, counter)
    else:
      # Phrase is parameter, add new phrase
      if wordExists(new):
        print('This word already exists')
      else:
        new_data = getMeaning(new, 'Meaning for ' + new)
        updateOn(doc_ref, new_data, counter)
        updateOff(new_data, counter)
      
  else:
    # Other funcionalities, print smth
    print(getDict(goal))


def updateOn(doc_ref, new_data, counter):
  doc_ref.update({
    str(counter):new_data
  })

def updateOff(new_data, counter):
  with open(path_off, 'r') as f:
    obj = json.load(f)
    obj[counter] = new_data
  
  with open(path_off, 'w') as f:
    json.dump(obj, f)

def syncOff(new_version):
  with open(path_off, 'w') as f:
    json.dump(new_version, f)

def wordExists(newWord):
  doc = retrieveDict()
  i = 0
  while len(doc) > i:
    current = doc[str(i)]
    if(current['phrase'] == newWord):
      return True
    i += 1
  return False

def retrieveDict():
  return json.load(open(path_off, 'r')) 

def getDict(goal):
  doc_off = retrieveDict()
  i = 0
  limit = 0
  toPrint = ''
  while len(doc_off) > i:
    obj = doc_off[str(i)]
    if goal == '-l':
      toPrint += str("\n"+ obj['phrase']) + " <- means -> " + str(obj['meaning'])
    elif goal == '-ll':
      if limit == 0:
        limit += 1
        toPrint += str(len(doc_off))
    else:
      if goal in str(obj['phrase']) or goal in str(obj['meaning']):
        toPrint += str("\n"+ obj['phrase']) + " <- means -> " + str(obj['meaning'])
    i += 1
  return toPrint


def storeSize(doc_on):
  with open(path_db, 'w') as f:
    f.write(str(len(doc_on)))


# def lastCounter():
#   with open(path_db, 'r') as f:
#     return int(f.readline())



main()










# TO_DO
# 1. If device is ahead check for last version of db
#     if last version differences from relevant -> generate counter form relevant
#     and append difference between local and last into relevant
#     sync local version
#
# 2. If db is ahead check for last version of db
#     If last version differences from local -> generate counter from relevant
#     and append difference between local and last into relevant
#     sync local version