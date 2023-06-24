import re

from django.contrib.auth.models import User

from rest_framework import serializers

from . models import Blogs, Comments


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = User
        fields = ("id","username","email","password")
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    def validate(self, data):
        username = data.get("username","")
        password = data.get("password","")
        username_validate_pattern = "^[A-Za-z]+$"

        if (len(username) <= 0) or (username=="") or (len(username) < 3):
            raise serializers.ValidationError("Please enter a valid Username")  
        
        if not re.match(username_validate_pattern, username):
            raise serializers.ValidationError("Username should not contain characters other then alphabets")   
        
        if (len(password) <= 0) or (password=="") or (len(password) <= 8):
            raise serializers.ValidationError("Password must be more than 8 characters")  
        
        return data


class BlogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.CharField(read_only=True)
    class Meta:
        model = Blogs
        fields = "__all__"
    
    def create(self, validated_data):
        user = self.context.get('user')    
        return user.blogs_set.create(**validated_data)
    
    def validate(self, data):
        title = data.get("title","")

        if (len(title) <= 0) or (title=="") or (len(title) <= 3):
            raise serializers.ValidationError("Please enter a valid Blog Title")  

        return data


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.CharField(read_only=True)
    blog = serializers.CharField(read_only=True)
    class Meta:
        model = Comments
        fields = "__all__"
    
    def create(self, validated_data):
        blog = self.context.get('blog')    
        user = self.context.get('user')    
        return Comments.objects.create(blog=blog,user=user,**validated_data)
    
    def validate(self, data):
        comment = data.get("comment","")

        if len(comment) <= 5:
            raise serializers.ValidationError("Please enter a valid Comment")  

        return data

