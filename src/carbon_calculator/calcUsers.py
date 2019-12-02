from .models import CalcUser

def QueryCalcUsers(args):
    pass

def CreateCalcUser(args):

    try:
        first_name = args.get("first_name","")
        last_name = args.get("last_name","")
        email = args.get("email","")
        locality = args.get("locality","")
        groups = args.get("groups",[])
        minimum_age = args.get("minimum_age",False)
        accepts_tnc = args.get("accepts_terms_and_conditions", False)
        event = args.get("eventName","")

        newUser = CalcUser.objects.filter(email=email).first()
        if newUser:
            if first_name!="":
                newUser.first_name = first_name
            if last_name != "":
                newUser.last_name = last_name
            if locality != "":
                newUser.locality = locality
            newUser.minimum_age = minimum_age
            newUser.accepts_tnc = accepts_tnc

            newUser.save()

            if eventName != "":
                event = Event.objects.filter(name=eventName).first()
                if event:
                    newUser.event = event
                    event.attendees.add(newUser)

            newUser.save()

            if groups != []:
                for group in groups:
                    group1 = Group.objects.filter(name=group)
                    if group1:
                        newUser.groups.add(group1)

        else:
            newUser = CalcUser(first_name=first_name,
                            last_name = last_name,
                            email =email, 
                            locality = locality,
                            #groups = ""groups"",
                            minimum_age = minimum_age,
                            accepts_terms_and_conditions = accepts_tnc)
        newUser.save()
        return {"id":newUser.id,"email":newUser.email}
    except:
        print("Exception!")
        error = {"success":False}

        return error

#   first_name = models.CharField(max_length=SHORT_STR_LEN, null=True)
#    last_name = models.CharField(max_length=SHORT_STR_LEN, null=True)
#    email = models.EmailField(max_length=SHORT_STR_LEN, 
#      unique=True, db_index=True)
#    locality = models.CharField(max_length=SHORT_STR_LEN, null=True)
#    groups = models.ManyToManyField(Group, blank=True)
#    minimum_age = models.BooleanField(default=False, blank=True)
#    accepts_terms_and_conditions = models.BooleanField(default=False, blank=True)