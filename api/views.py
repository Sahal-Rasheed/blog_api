from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status

from .models import Comments, Blogs
from .serializers import CommentSerializer, BlogSerializer, UserSerializer
from . utils import Pagination
from .helpers import upload_image_to_s3, delete_image_from_s3

# Create your views here.

class UserRegistrationView(ViewSet):
    def create(self,request,*args,**kwrags):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():  
            serializer.save()
            return Response({"status":201, "message":"User created"}, status=status.HTTP_201_CREATED)
        
        return Response({"status":400, "message":"Validation error", "data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Blogs CRUD
class BlogView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Pagination

    def create(self,request,*args,**kwrags):
        user = request.user
        serializer = BlogSerializer(data=request.data, context={'user':user})
        if serializer.is_valid():  
            image_file = request.FILES.get('image')

            image_key = f"blog_post_{serializer.validated_data['title']}.jpg"
            upload_image_to_s3(image_file, image_key)
            serializer.validated_data['image'] = image_key

            serializer.save()
            return Response({"status":201, "message":"Blog created"}, status=status.HTTP_201_CREATED)
        
        return Response({"status":400, "message":"Validation error", "data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self,request,*args,**kwargs):
        blogs = Blogs.objects.all()

        # Pagination
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(blogs, request)
        serializer = BlogSerializer(result_page, many=True)

        response = paginator.get_paginated_response(serializer.data)
        response.data["limit"] = paginator.page_size
        response.data["page_no"] = paginator.page.number
        return response     
    
    def retrieve(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        try:
            blog = Blogs.objects.get(id=id)
            serializer = BlogSerializer(blog)
            return Response({"status":200, "message":"Success", "data":serializer.data}, status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response({"status":404, "message":"Blog Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
    def update(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        try:
            blog = Blogs.objects.get(id=id,user_id=request.user)
            serializer = BlogSerializer(data=request.data, instance=blog)
            if serializer.is_valid():
                old_image_key = blog.image.name
                delete_image_from_s3(old_image_key)

                image_file = request.FILES.get('image')
                image_key = f"blog_post_{blog.id}.jpg"
                upload_image_to_s3(image_file, image_key)

                serializer.validated_data['image'] = image_key
                serializer.save()
                return Response({"status":200, "message":"Success", "data":serializer.data}, status=status.HTTP_200_OK)
            
            return Response({"status":400, "message":"Validation error", "data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
        except Blogs.DoesNotExist:
            return Response({"status":404, "message":"Blog Not Found"}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        user_id = request.user.id
        try:
            blog = Blogs.objects.get(id=id,user_id=user_id)
            image_key = blog.image.name
            delete_image_from_s3(image_key)
            blog.delete()
            return Response({"status":200, "message":"Blog Deleted"}, status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response({"status":404, "message":"Blog Not Found"}, status=status.HTTP_404_NOT_FOUND)


# Comments CRUD
class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Pagination

    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        try:
            blog = Blogs.objects.get(id=id)
            comments = Comments.objects.filter(blog_id=blog.id)
            if comments:
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(comments, request)
                serializer = CommentSerializer(result_page, many=True)
                
                response = paginator.get_paginated_response(serializer.data)
                response.data["limit"] = paginator.page_size
                response.data["page_no"] = paginator.page.number
                return response       
             
            return Response({"status":404, "message":"Comments Not Found"}, status=status.HTTP_404_NOT_FOUND)
             
        except Blogs.DoesNotExist:
            return Response({"status":404, "message":"Comments Not Found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        try:
            blog = Blogs.objects.get(id=id)
            user = request.user
            serializer = CommentSerializer(data=request.data, context={'blog':blog, 'user':user})
            if serializer.is_valid():  
                serializer.save()
                return Response({"status":201, "message":"Comment added"}, status=status.HTTP_201_CREATED)
            
            return Response({"status":400, "message":"Validation error", "data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
               
        except Blogs.DoesNotExist:   
            return Response({"status":404, "message":"Blog not found"}, status=status.HTTP_404_NOT_FOUND)
    

class CommentUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        try:
            comment = Comments.objects.get(id=id,user_id=request.user.id)
            serializer = CommentSerializer(data=request.data, instance=comment)
            if serializer.is_valid():
                serializer.save()
                return Response({"status":200, "message":"Success", "data":serializer.data}, status=status.HTTP_200_OK)
            
            return Response({"status":400, "message":"Validation error", "data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
        except Comments.DoesNotExist:
            return Response({"status":404, "message":"Comment Not Found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        user_id = request.user.id
        try:
            comments = Comments.objects.get(id=id,user_id=user_id)
            comments.delete()
            return Response({"status":200, "message":"Comment Deleted"}, status=status.HTTP_200_OK)
        except Comments.DoesNotExist:
            return Response({"status":404, "message":"Comment Not Found"}, status=status.HTTP_404_NOT_FOUND)

















    


    
        
