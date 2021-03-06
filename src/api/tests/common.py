import jwt
from http.cookies import SimpleCookie
from datetime import datetime
from _main_.settings import SECRET_KEY
from database.models import UserProfile
from carbon_calculator.models import CalcDefault
import requests
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def setupCC(client):
    cq = CalcDefault.objects.all()
    num = cq.count()
    if num<=0:
        client.post('/cc/import',
            {   "Confirm": "Yes",
                "Actions":"carbon_calculator/content/Actions.csv",
                "Questions":"carbon_calculator/content/Questions.csv",
                "Stations":"carbon_calculator/content/Stations.csv",
                "Groups":"carbon_calculator/content/Groups.csv",
                "Organizations":"carbon_calculator/content/Organizations.csv",
                "Events":"carbon_calculator/content/Events.csv",
                "Defaults":"carbon_calculator/content/Defaults.csv"
                })

def signinAs(client, user):

    if user:
      print("Sign in as " + user.full_name)
      dt = datetime.now()
      dt.microsecond

      payload = {
          "user_id": str(user.id), 
          "email": user.email,
          "is_super_admin": user.is_super_admin, 
          "is_community_admin": user.is_community_admin,
          "iat": dt.microsecond,
          "exp": dt.microsecond+1000000000,
      }

      the_token = jwt.encode(
          payload, 
          SECRET_KEY, 
          algorithm='HS256'
      ).decode('utf-8')

      client.cookies = SimpleCookie({'token': the_token})

    else:
      print("No user signed in")
      client.cookies = SimpleCookie({'token': ""})

def createUsers():

    user, _ = UserProfile.objects.get_or_create(full_name="Regular User",email="user@test.com")

    cadmin, _ = UserProfile.objects.get_or_create(full_name="Community Admin",email="cadmin@test.com",is_community_admin=True)

    sadmin, _ = UserProfile.objects.get_or_create(full_name="Super Admin",email="sadmin@test.com", is_super_admin=True)

    return user, cadmin, sadmin

def createImage(picURL=None):

    # this may break if that picture goes away.  Ha ha - keep you on your toes!
    if not picURL:
        picURL = "https://www.whitehouse.gov/wp-content/uploads/2021/04/P20210303AS-1901-cropped.jpg"

    resp = requests.get(picURL)
    if resp.status_code != requests.codes.ok:
        # Error handling here3
        print("ERROR: Unable to import action photo from "+picURL)
        image_file = None
    else:
        image = resp.content
        file_name =  picURL.split("/")[-1]
        file_type_ext = file_name.split(".")[-1]

        content_type = 'image/jpeg'
        if len(file_type_ext)>0 and file_type_ext.lower() == 'png':
            content_type = 'image/png'

        # Create a new Django file-like object to be used in models as ImageField using
        # InMemoryUploadedFile.  If you look at the source in Django, a
        # SimpleUploadedFile is essentially instantiated similarly to what is shown here
        img_io = BytesIO(image)
        image_file = InMemoryUploadedFile(img_io, None, file_name, content_type, None, None)

    return image_file