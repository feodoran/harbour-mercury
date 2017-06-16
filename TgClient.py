#    Copyright (C) 2017 Christian Stemmle
#
#    This file is part of Mercury.
#
#    Mercury is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Mercury is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Mercury. If not, see <http://www.gnu.org/licenses/>.

import os
import pyotherside
import telethon

SESSION_ID = 'mercury'
LOCAL_DIR = '.local/share/harbour-mercury/'
TIMEFORMAT = '%H:%M'
PROXY = None
DC_IP = None
DC_IP = '149.154.167.51'
TEST = 0

#DC_IP = '149.154.167.40'   # testing
#DC_IP = '149.154.167.50'   # production

if not os.path.isdir(LOCAL_DIR):
    os.makedirs(LOCAL_DIR)

os.chdir(LOCAL_DIR)    

class Client(telethon.TelegramClient):
    
    def __init__(self, session_user_id, api_id, api_hash, proxy=None):

        print('Initializing interactive example...')
        super().__init__(session_user_id, api_id, api_hash, proxy)
        self.entities = {}

    ###############
    ###  login  ###
    ###############
    
    # login code
    def request_code(self, phonenumber=None):
        if phonenumber:
            self.phonenumber = phonenumber
        self.send_code_request(self.phonenumber)

    def send_code(self, code):
        try:
            success = self.sign_in(phone_number=self.phonenumber, code=code)
        # Two-step verification may be enabled
        except telethon.errors.RPCError as e:
            if e.password_required:
                return 'pass_required'
            else:
                raise
        return success

    # Two-step verification
    def send_pass(self, password):
        return self.sign_in(password=password)

    #######################
    ###  requeste data  ###
    #######################

    def request_dialogs(self):
        dialogs, entities = self.get_dialogs(limit=0)
        dialogs_model = []
        
        for entity in entities:
            
            if isinstance(entity, telethon.tl.types.User):
                entity_type = 'user'
            elif isinstance(entity, telethon.tl.types.Chat):
                entity_type = 'chat'
            elif isinstance(entity, telethon.tl.types.Channel):
                entity_type = 'channel'
            else:
                raise ValueError('unkown type')
            
            dialogdict = {}
            dialogdict['name'] = telethon.utils.get_display_name(entity)
            dialogdict['entity_id'] = '{}_{}'.format(entity_type, entity.id)
            
            self.entities[dialogdict['entity_id']] = entity
            dialogs_model.append(dialogdict)
            
        pyotherside.send('update_dialogs', dialogs_model)
        
    def request_messages(self, ID):
        entity = self.get_entity(ID)            
        total_count, messages, senders = self.get_message_history(entity)
        
        # Iterate over all (in reverse order so the latest appear last)
        messages_model = []
        for msg, sender in zip(reversed(messages), reversed(senders)):
            msgdict = {}
            msgdict['name'] = sender.first_name if sender else '???'
            msgdict['time'] = msg.date.strftime(TIMEFORMAT)
            
            if hasattr(msg, 'action'):
                msgdict['message'] = msg.action
            elif msg.media:
                msgdict['message'] = '<media file>'
            elif msg.message:
                msgdict['message'] = msg.message
            else:
                # Unknown message, simply print its class name
                msgdict['message'] = msg.__class__.__name__
        
            messages_model.append(msgdict)
            
        pyotherside.send('update_messages', messages_model)
    
    ############################
    ###  internal functions  ###
    ############################
    
    def get_entity(self, ID):
        
        if ID in self.entities:
            return self.entities[ID]
        
        entity_type, entity_id = ID.split('_')
        if entity_type == 'chat':
            entity = self.invoke(telethon.tl.functions.messages.GetChatsRequest([entity_id,])).chats[0]
        elif entity_type == 'user':
            entity = self.invoke(telethon.tl.functions.users.GetUsersRequest([entity_id,])).users[0]
        elif entity_type == 'channel':
            raise NotImplementedError
        else:
            raise ValueError('Unkown type {}'.format(entity_type))
        
client = None
def connect():
    global client
    
    if TEST:
        import Test
        client = Test.TestClient()
        return Test.connect_state
    
    # load apikey
    if not os.path.isfile('apikey'):
        if not os.path.isfile('apikey.example'):
            with open('apikey.example', 'w') as fd:
                fd.write('api_id <ID>\napi_hash <HASH>\n')
        pyotherside.send('log', 'missing_apikey')
        return False
    else:
        with open('apikey') as fd:
            tmp = fd.readlines()
            api_id = int(tmp[0].split()[1])
            api_hash = tmp[1].split()[1]
    
    client = Client(
        SESSION_ID,
        api_id = api_id,
        api_hash = api_hash,
        proxy = PROXY
    )
    
    pyotherside.send('log', ''.join(('Telethon Client Version: ', client.__version__)))
    
    if DC_IP:
        client.session.server_address = DC_IP
        
    pyotherside.send('log', 'Connecting to Telegram servers...')
    if not client.connect():
        pyotherside.send('log', 'Initial connection failed. Retrying...')
        if not client.connect():
            pyotherside.send('log', 'Could not connect to Telegram servers.')
            return False
        
    if not client.is_user_authorized():
        return 'enter_number'
    
    return True

def call(method, args):
    getattr(client, method)(*args)
    