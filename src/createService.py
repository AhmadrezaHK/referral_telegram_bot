from google import createService

service = createService('credentials.json', 'drive',
                        'v3', ['https://www.googleapis.com/auth/drive'])
