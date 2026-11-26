from django.shortcuts import get_object_or_404
from django.utils.cache import patch_vary_headers
from rest_framework import permissions, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from .ai_guide import GuideUnavailable, generate_answer
from .models import Lesson
from .permissions import can_access_lesson


class GuideInput(serializers.Serializer):
    lesson_id = serializers.IntegerField(min_value=1)
    question = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)
    language = serializers.ChoiceField(choices=['ru', 'kk', 'en'], default='ru')


class GuideThrottle(UserRateThrottle):
    scope = 'ai_guide'
    rate = '12/min'


class AIGuideView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GuideThrottle]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        patch_vary_headers(response, ['Authorization', 'Cookie'])
        return response

    def post(self, request):
        serializer = GuideInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=data['lesson_id'])
        if not can_access_lesson(request.user, lesson):
            raise PermissionDenied('No access to this lesson.')
        try:
            answer = generate_answer(lesson, data['question'], data['language'])
        except GuideUnavailable as error:
            return Response({'code': error.code}, status=error.status)
        return Response({'answer': answer})
