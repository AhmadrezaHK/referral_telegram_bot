from position import getPositionList
from createService import service
position_type = ['Technical', 'Business']

FOLDER_LIST = {}


def getFolderList(parent=None, folderName=None):
    page_token = None
    drive_folder_list = {}
    query = "mimeType='application/vnd.google-apps.folder' and trashed = false"
    if folderName:
        query = query + " and name='" + folderName + "'"
    if parent:
        query = query + " and '" + parent + "' in parents"
    while True:
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            drive_folder_list[file['name']] = file['id']
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return drive_folder_list


def createFolder(name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    file = service.files().create(body=file_metadata,
                                  fields='id').execute()
    return file['id']


c_folder = getFolderList(folderName='Candidates')
if(c_folder):
    FOLDER_LIST['Candidates'] = c_folder['Candidates']
else:
    FOLDER_LIST['Candidates'] = createFolder('Candidates')


b_folder = getFolderList(parent=FOLDER_LIST['Candidates'])
if('Technical' in b_folder):
    FOLDER_LIST['Technical'] = b_folder['Technical']
else:
    FOLDER_LIST['Technical'] = createFolder(
        'Technical', parent_id=FOLDER_LIST['Candidates'])
if('Business' in b_folder):
    FOLDER_LIST['Business'] = b_folder['Business']
else:
    FOLDER_LIST['Business'] = createFolder(
        'Business', parent_id=FOLDER_LIST['Candidates'])


positionList = getPositionList()
b = getFolderList(parent=FOLDER_LIST['Business'])
t = getFolderList(parent=FOLDER_LIST['Technical'])
pf = {'Business': b,
      'Technical': t}
for p in positionList:
    if(p['name'] in pf[p['type']]):
        FOLDER_LIST[p['name']] = pf[p['type']][p['name']]
    else:
        FOLDER_LIST[p['name']] = createFolder(
            p['name'], parent_id=FOLDER_LIST[p["type"]])
