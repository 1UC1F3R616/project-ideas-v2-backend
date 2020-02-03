from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from app.serializers import ( 
    CommentSerializer,
    IdeaSerializer
)

from .models import (
    Idea,
    Comment,
    Vote
)


# View for both upvoting and downvoting
class VoteView(APIView):
    
    def post(self, request):

        # Getting data from request
        idea_keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        keys = {"UPVOTE":1, "DOWNVOTE":-1}
        req_data = request.data
        user = request.user

        # Checking if the idea with idea_id exists
        try:
            idea = Idea.objects.get(id=req_data["idea_id"])
        except Idea.DoesNotExist:
            return Response({"message":"Invalid Idea Id"}, status=status.HTTP_400_BAD_REQUEST)

        # Checking if the ida with idea_id can be voted or not
        if idea.is_reviewed==idea_keys["PENDING"] or idea.is_reviewed==idea_keys["REJECTED"]:
            return Response({"message":"Idea cannot be voted"}, status=status.HTTP_400_BAD_REQUEST)

        # Voting idea
        try:
            # Checking if the user has voted earlier (also was it upvote or downvote)
            vote = Vote.objects.get(user_id=user.id, idea_id=req_data["idea_id"])
            check1 = (vote.vote_type==keys["UPVOTE"] and int(req_data['vote_type'])==keys["UPVOTE"])
            check2 = (vote.vote_type==keys["DOWNVOTE"] and int(req_data['vote_type'])==keys["DOWNVOTE"])

            if check1 or check2:
                return Response({"message":"User has already Voted"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Updating votes in idea as well as vote object
                idea.votes = idea.votes + int(req_data['vote_type'])
                idea.save()
                vote.vote_type = req_data["vote_type"]
                vote.save()
                idea_serializer = IdeaSerializer(idea)
                return Response({"message":"Voted Successfully", "idea":idea_serializer.data}, status=status.HTTP_200_OK)

        except Vote.DoesNotExist:
            # Updating Votes for idea and creating a new idea object
            idea.votes = idea.votes + int(req_data['vote_type'])
            idea.save()
            vote = Vote()
            vote.user_id = user
            vote.idea_id = idea
            vote.vote_type = req_data["vote_type"]
            vote.save()
            idea_serializer = IdeaSerializer(idea)
            return Response({"message":"Voted Successfully", "idea":idea_serializer.data}, status=status.HTTP_200_OK)


# View for posting a comment for an idea and also getting comments for idea
class CommentView(APIView):

    def get(self, request, pk):
        # Getting all comments
        comments = list(Comment.objects.filter(idea_id=pk))
        response = []
        if len(comments)==0:
            return Response({"message":"There are no comments"}, status=status.HTTP_204_NO_CONTENT)
        else:
            # Adding parent comment for each thread
            comments = list(Comment.objects.filter(parent_comment_id=None, idea_id=pk))
            serializer = CommentSerializer(comments, many=True)
            response = serializer.data

            # Adding child comment for each thread
            for resp in response:
                resp['child_comments'] = None
                child_comments = list(Comment.objects.filter(parent_comment_id=resp['id'], idea_id=pk))
                child_comment_serializer = CommentSerializer(child_comments, many=True)
                resp['child_comments'] = child_comment_serializer.data
        
            return Response({"message":response}, status=status.HTTP_200_OK)


    def post(self, request):
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        request.data['user_id'] = request.user.id
        
        # Checking if an idea with idea_id exists
        try:
            idea = Idea.objects.get(id=(request.data)['idea_id'], is_reviewed=keys["PUBLISHED"])
        except:
            return Response({"message":"Invalid Idea Id"}, status=status.HTTP_400_BAD_REQUEST) 

        # Validating and saving comment for that idea   
        comment = CommentSerializer(data=request.data)        
        if comment.is_valid():
            comment.save()
            return Response({"message":comment.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":comment.errors}, status=status.HTTP_400_BAD_REQUEST)