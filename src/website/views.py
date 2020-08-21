from django.shortcuts import render
from _main_.utils.massenergize_response import MassenergizeResponse
from database.models import Deployment
from _main_.settings import IS_PROD, BASE_DIR
from sentry_sdk import capture_message
from _main_.utils.utils import load_json, load_text_contents

# Create your views here.
def home(request):
  deployments = Deployment.objects.all()[:3]
  build_info = load_json(BASE_DIR + "/_main_/config/build/deployConfig.json")
  deploy_notes = load_text_contents(BASE_DIR + "/_main_/config/build/deployNotes.txt")
  
  deployment = Deployment.objects.filter(version=build_info.get('BUILD_VERSION', "")).first()
  if deployment:
    if deployment.notes != deploy_notes:
      deployment.notes = deploy_notes
      deployment.save()
  else:
    deployment = Deployment.objects.create(
      version=build_info.get('BUILD_VERSION', ''),
      notes=deploy_notes
    )


  if IS_PROD:
    SITE_TITLE = 'MassEnergize-API'
    SITE_BACKGROUND_COLOR = '#310161'
    SITE_FONT_COLOR = 'white'
  else:
    SITE_TITLE = 'DEV: MassEnergize-API'
    SITE_BACKGROUND_COLOR = '#0b5466'
    SITE_FONT_COLOR = 'white'

  return render(request, 'index.html', {
      'deployments': deployments,
      "BUILD_INFO": build_info,
      "DEPLOY_NOTES": deploy_notes,
      'SITE_TITLE': SITE_TITLE,
      'SITE_BACKGROUND_COLOR': SITE_BACKGROUND_COLOR,
      'SITE_FONT_COLOR': SITE_FONT_COLOR
    }
  )

def handler400(request, exception):
  error_msg = "bad_request"
  return MassenergizeResponse(error=error_msg)

def handler403(request, exception):
  error_msg = "permission_denied"
  capture_message(error_msg, level="error")
  return MassenergizeResponse(error=error_msg)

def handler404(request, exception):
  error_msg = "page_not_found"
  capture_message(error_msg, level="error")
  return MassenergizeResponse(data=f"path: {request.build_absolute_uri()}", error=error_msg)

def handler500(request):
  error_msg = "server_error"
  capture_message(error_msg, level="error")
  return MassenergizeResponse(error=error_msg)
