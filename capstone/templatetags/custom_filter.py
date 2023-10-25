from django.template import Library
from capstone.models import ROLE

register = Library()

priority = {
  1: "low-pr",
  2: "medium-pr",
  3: "high-pr",
  4: "very-high-pr",
  5: "urgent-pr",
}

status = {
    0: ["open", "bg-pill-open"],
    1: ["in progress", "bg-pill-progress"],
    2: ["in review", "bg-pill-waiting"],
    3: ["done", "bg-pill-done"],
}

progress = {
    0: 0,
    1: 33.33,
    2: 66.66,
    3: 100
}


mbtiPersonalities = {
    "istj": "Responsible, sincere, analytical, reserved, realistic, systematic, hardworking, with sound practical judgment.",
    "istp": "Action-oriented, logical, analytical, spontaneous, reserved, independent and skilled at understanding how mechanical things work.",
    "estp": "Outgoing, realistic, action-oriented-curious, spontaneous. Pragmatic problem solver and skilful negotiator.",
    "estj": "Efficient, outgoing, analytical, systematic, dependable, realistic. Likes to run the show and get things done in an orderly fashion.",
    "isfj": "Warm, considerate, responsible, pragmatic, thorough. Devoted caretakers who enjoy being helpful to others.",
    "isfp": "Gentle, sensitive, nurturing, helpful, flexible, realistic. Seeks to create a personal environment that is practical.",
    "esfp": "Enthusiastic, friendly, spontaneous, tactful, flexible. Has common sense, enjoys helping people in tangible ways.",
    "esfj": "Friendly, outgoing, reliable, conscientious, organized, practical. Seeks to be helpful and please others.",
    "infj": "Idealistic, organized, insightful, dependable, compassionate, gentle. Seeks cooperation and intellectual stimulation.",
    "infp": "Sensitive. creative, idealistic, perceptive, caring, loyal. Values inner harmony and personal growth, focusing on dreams and possibilities.",
    "enfp": "Enthusiastic, creative, spontaneous, optimistic, supportive, playful. Values inspiration and sees potential in others.",
    "enfj": "Caring, enthusiastic, idealistic, organized, diplomatic, responsible. Skilled communicators.",
    "intj": "Innovative, independent, strategic, logical, reserved, insightful. Driven by their own original ideas to achieve improvements.",
    "intp": "Intellectual, logical, precise, reserved, flexible, imaginative. Enjoys speculation and creative problem solving.",
    "entp": "Inventive, enthusiastic, strategic, enterprising, inquisitive, versatile. Enjoys new ideas and challenges, value inspiration.",
    "entj": "Strategic, logical, efficient, outgoing, ambitious, independent. Effective organizers of people."
}

@register.filter
def getPriority(value):
    value = priority.get(value) 
    return value

@register.filter
def removeHypens(value):
    newValue = priority.get(value)
    return newValue.replace("-", " ").replace("pr", "")

@register.filter
def getStatus(value):
    return status.get(value)[0]

@register.filter
def getCSSStatus(value):
    return status.get(value)[1]

@register.filter
def showProgress(value):
    return progress.get(value)

@register.filter
def roleType(value):
    return dict(ROLE).get(value)

@register.filter
def mbtiType(value):
    return mbtiPersonalities.get(value.lower())
    # for key, val in ROLE:
    #     if key == value:
    #         return val
            