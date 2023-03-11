from django.shortcuts import render
from django.http import HttpRequest
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .scrapper import Scrapper
from django.http import JsonResponse
from corsheaders.middleware import CorsMiddleware
from corsheaders.defaults import default_headers


class StudentAPIView(ViewSet):
    def login(self, request):
        if request.method == 'POST':
            username = request.data["username"]
            password = request.data["password"]
            scrapper = Scrapper(username, password)
            result = scrapper.login()
            response = JsonResponse(result)
            return CorsMiddleware(get_response=False).process_response(request, response)

    def courses(self, request):
        if request.method == 'POST':
            username = request.data["username"]
            password = request.data["password"]
            scrapper = Scrapper(username, password)
            courses, success = scrapper.get_courses_data()
            response = JsonResponse({'courses': courses, 'success': success})
            return CorsMiddleware(get_response=False).process_response(request, response)

    def gpa(self, request):
        if request.method == 'POST':
            username = request.data["username"]
            password = request.data["password"]
            scrapper = Scrapper(username, password)
            gpa, success = scrapper.get_gpa_please('2022-2023')
            response = JsonResponse({'gpa': gpa, 'success': success})
            return CorsMiddleware(get_response=False).process_response(request, response)

    def idname(self, request):
        if request.method == 'POST':
            username = request.data["username"]
            password = request.data["password"]
            scrapper = Scrapper(username, password)
            idName, success = scrapper.get_idname()
            response = JsonResponse(
                {'id': idName[0], 'name': idName[1], 'success': success})
            return CorsMiddleware(get_response=False).process_response(request, response)

    def transcript(self, request):
        if request.method == 'POST':
            username = request.data["username"]
            password = request.data["password"]
            year = request.data["year"]
            scrapper = Scrapper(username, password)
            transcript = scrapper.get_year_transcript(year)
            response = JsonResponse(transcript)
            return CorsMiddleware(get_response=False).process_response(request, response)

    # Override the `http_method_not_allowed` method to allow CORS preflight requests
    def http_method_not_allowed(self, request, *args, **kwargs):
        response = JsonResponse({'message': 'Method not allowed'})
        response['Allow'] = ','.join(self._allowed_methods())
        return CorsMiddleware(get_response=False).process_response(request, response)

    # Set the CORS headers on the response
    def options(self, request, *args, **kwargs):
        response = JsonResponse({'message': 'ok'})
        response['Access-Control-Allow-Origin'] = 'https://gucentrall.vercel.app'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = ','.join(default_headers)
        return response
