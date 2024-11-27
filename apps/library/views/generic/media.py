from django.views.generic import View

class MediaAuthChecker(View):
    """
        all my requests are login protected by default,
        but you can add more permission classes if you want.
    """

    def get(self, request, *args, **kwargs):
        file_path = request.get_full_path()[1:] #get requested file
        folders = file_path.split("/")[1:] #remove media initial folder and split into individual folders

        #is user permitted to view file? ### insert own auth methods here ###

        if folders[0] == "employees" and not request.user.check_groups("Employee"):
            return Response({'msg': "You are not authorized to view this resource."}, status=status.HTTP_403_FORBIDDEN)

        if folders[0] == "group" and not request.user.check_groups("Rental Manager"):
            return Response({'msg': "You are not authorized to view this resource."}, status=status.HTTP_403_FORBIDDEN)

        absolute_path = BASE_DIR / Path(file_path)
        try: #open and send file to frontend
            if os.path.exists(absolute_path):
                mime = MimeTypes()
                content_type, encoding = mime.guess_type(absolute_path)

                if content_type is None:
                    content_type = 'application/octet-stream'  # A default content type

                response = FileResponse(open(absolute_path, 'rb'), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(absolute_path)}"'
                return response
            else:
                return Response({'msg': "File not found."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'msg': "Error Processing File"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
