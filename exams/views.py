from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from note.models import Lesson
from .serializers import CreateExamSerializer, ExamSerializer
import google.generativeai as genai
import json

genai.configure(api_key=settings.GEMINI_API_KEY)


class ExamViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        multiple_choices = [
            {
                "question": "Which tense describes actions happening now?",
                "choices": {
                    "A": "Present Tense",
                    "B": "Future Tense",
                    "C": "Present Perfect",
                    "D": "Past Continuous",
                },
                "answer": "A",
            }
        ]

        blank_space = [
            {"question": "________ is the capital city of France", "answer": "Paris"}
        ]

        true_or_false = [
            {
                "question": "Ethiopia was never colonized by a European power.",
                "answer": "True",
            },
        ]

        serializer = CreateExamSerializer(
            data=request.data, context={"user_id": request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        lesson_id = serializer.validated_data.get("lesson_id")
        question_type = serializer.get_question_type_display()
        lesson = Lesson.objects.get(id=lesson_id).content

        if len(lesson) < 300:
            return Response(status=400, data={"message": "Lesson is too short"})
        convo = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "You are a Test Question Generator. Your task is to generate multiple-choice, blank space or true or false questions based on the given notes.",
                        "Provide the question and answer pairs in JSON format as follows: [{data 1}, {data 2}, {data 3}], using double quotes instead of single quotes. Avoid adding markdown like ```json [{data 1}, {data 2}, {data 3}]```."
                        "Ensure that the number of questions exceeds 5, and if the input indicates a surplus of notes, increase the question count accordingly."
                        f"The questions in the format of multiple-choice. Examples: {multiple_choices}",
                        f"The questions in the format of blank-space. Examples: {blank_space}",
                        f"The questions in the format of true or false. Examples: {true_or_false}",
                        f"The question type is {question_type}",
                    ],
                }
            ]
        )
        convo.send_message(lesson)
        questions = json.loads(convo.last.text)
        serializer = ExamSerializer(questions, many=True)
        return Response(serializer.data)
