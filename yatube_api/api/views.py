from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from posts.models import Post, Group, User
from api.serializers import (PostSerializer, GroupSerializer,
                             CommentSerializer, FollowSerializer)
from api.permissions import IsAuthorOrReadOnly
from django.shortcuts import get_object_or_404


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(
            author=self.request.user,
            post=get_object_or_404(Post, id=post_id)
        )

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        new_queryset = post.comments.all()
        return new_queryset


class FollowViewSet(ModelViewSet):
    serializer_class = FollowSerializer
    filter_backends = (SearchFilter, )
    search_fields = ('following__username',)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        user = self.request.user
        username = self.request.data.get('following')
        following = get_object_or_404(User, username=username)
        serializer.save(user=user, following=following)
