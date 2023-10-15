from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q, Max, F

from datetime import datetime

from .models import *
from .constant import *
from .mbti_functions import *

import json
import pandas as pd
import tensorflow as tf

from transformers import TFBertModel, BertTokenizer
from keras.models import load_model
from keras.utils import pad_sequences
# Create your views here.

@login_required
def index(request):
    allTicket = 0
    outstanding = 0
    resolved = 0
    dueToday = 0
    overdue = 0

    userId = request.user.id

    try:
        user = User.objects.get(pk=userId)
    except User.DoesNotExist:
        user = ""

    if user.is_manager:
        tickets = getTickets("outstanding", True)
        allTicket = getTickets("all", True)
        resolved = getTickets("resolved", True)
        dueToday = getTickets("due_today", True)
        overdue = getTickets("overdue", True)
    else:
        tickets = getTickets("outstanding", False, userId)
        allTicket = getTickets("all", False, userId)
        resolved = getTickets("resolved", False, userId)
        dueToday = getTickets("due_today", False, userId)
        overdue = getTickets("overdue", False, userId)

    outstanding = len(tickets)
    mbtiRes = MBTIResult.objects.filter(user=request.user.id).order_by('-create_date')[:3]

    notifications = Notification.objects.filter(send_to=userId)
    return render(request, "capstone/dashboard/index.html", {
        "personalities": mbtiRes,
        "tickets": tickets.order_by('-create_date'),
        "priority": "aaa",
        "allTicket" : len(allTicket),
        "outstanding" : outstanding,
        "resolved" : len(resolved),
        "dueToday" : len(dueToday),
        "overdue" : len(overdue),
        "notifications": notifications,
        "iconTitle": ICONS[0],
        "titleHeader": "Dashboard",
        "subTitleHeader": "This dasboard is intended to show the tickets progress and personality."
    })

@login_required
def category(request):
    categories = Category.objects.all().order_by('name')
    
    return render(request, "capstone/category/index.html", {
        "categories": categories,
        "iconTitle": ICONS[1],
        "titleHeader": "Category",
        "subTitleHeader": "Shows all categories"
    })

@login_required
def addCategory(request):
    if request.method == "POST":
        category = request.POST["category"].lstrip()

        data = Category(
            name = category,
            slug = category.replace(" ", "-")
        )
        data.save()

        # array_values = request.POST.getlist('category[]')
        # print(array_values)
        
        messages.success(request, "New category has been saved successfully")
        return HttpResponseRedirect(reverse("category"))
    else:
        return render(request, "capstone/category/create.html", {
            "titleHeader": "Add Category",
            "subTitleHeader": "This page is used to create new category"
        })
    
@login_required
def editCategory(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        category = ""

    if request.method == "POST":
        if category:
            category.name = request.POST["category"].lstrip()
            category.slug = request.POST["category"].replace(" ", "-")
            category.save()

            messages.info(request, "Category has been updated successfully")
            return HttpResponseRedirect(reverse("category"))
    else:
        return render(request, "capstone/category/edit.html", {
            "category": category,
            "titleHeader": "Edit Category",
            "subTitleHeader": "This page is used to edit category name."
        })
    
@login_required
def deleteCategory(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    try:
        cat = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        cat = ""

    if cat != "":
        cat.delete()
        return JsonResponse({
            "message": "Data has been deleted successfully"
        }, status=200)
    else:
        return JsonResponse({
            "message": "There is a mistaken when deleting data!"
        }, status=400)

# def ticket(request):
#     tickets = Ticket.objects.all()
#     return render(request, "capstone/ticket/index.html", {
#         "tickets": tickets
#     })

def saveNotification(notif, ticketId, requester):

    if notif == 1:
        users = User.objects.filter(is_manager=True)
        for u in users:
            notification = Notification(
                notification = notif,
                ticket_id = ticketId,
                send_to_id = u.id,
                creator_id = requester
            )
            notification.save()

    return

@login_required
def createTicket(request):
        priority = PRIORITY
        softSkills = SOFTSKILLS
        categories = Category.objects.all()
        users = User.objects.filter(is_staff=0)
        categoryRoles = CategoryRole.objects.all()
        watchers = User.objects.filter(dept=1)
        requesters = User.objects.all()
        
        return render(request, "capstone/ticket/create_ticket.html", {
            "categories": categories,
            "users": users,
            "priority": priority,
            "softSkills": softSkills,
            "categoryRoles": categoryRoles,
            "watchers": watchers,
            "requesters": requesters,
            "iconTitle": ICONS[2],
            "titleHeader": "Create New Ticket",
            "subTitleHeader": "This page is intended to create a ticket for all users."
        })
    
@login_required
def ticketDetail(request, ticket_id, ticket_name):
    ticketName = ticket_name.replace('-', ' ')
    ticketDetail = Ticket.objects.get(pk=ticket_id)
    categories = Category.objects.all()
    categoryRoles = CategoryRole.objects.all()
    watchers = User.objects.filter(dept=1)

    watcherIds = ', '.join([str(watcher.id) for watcher in ticketDetail.watcher.all()])
    assignees = ', '.join([assignee.username for assignee in ticketDetail.assigned_to.all()])
    
    return render(request, "capstone/ticket/ticket_detail.html", {
        "ticketDetail": ticketDetail,
        "categories": categories,
        "priority": PRIORITY,
        "status": STATUS,
        "categoryRoles": categoryRoles,
        "watchers": watchers,
        "watcherIds": watcherIds,
        "assignees": assignees.split(', '),
        "titleHeader": "Ticket Detail" ,
        "subTitleHeader": "You can update and view the ticket detail that has been created."
    })
    
@login_required
def saveTicket(request):
    data = json.loads(request.body)
    ticketId = data["id"]
    if ticketId == 0:
        ticket = Ticket(
            ticket_title = data["title"],
            description = data["desc"],
            category_id = data["category"],
            priority = data["priority"],
            requester_id = request.user.id,
            due_date = data["dueDate"]
        )

        ticket.save()

        if "watchers" in data and "assignees" in data:
            watchers = data["watchers"]
            assignees = data["assignees"]
            if watchers:
                watcherTicket = Ticket.objects.get(id=ticket.id)
                watcherTicket.watcher.add(*watchers)

            if assignees:
                assigneeTicket = Ticket.objects.get(id=ticket.id)
                assignees = [val.lower() for val in assignees]
                userId = User.objects.filter(username__in=(assignees)).values_list('id', flat=True)
                assigneeTicket.assigned_to.add(*list(userId))

        saveNotification(1, ticket.id, request.user.id)
        
        return JsonResponse({
            "msg": "success",
            "status": 200
        }, status=200)
    else:
        
        try:
            updateTicket = Ticket.objects.get(id=ticketId)
        except Ticket.DoesNotExist:
            updateTicket = ""
        
        if updateTicket:
            updateTicket.ticket_title = data["title"]
            updateTicket.description = data["desc"]
            updateTicket.category_id = data["category"]
            updateTicket.priority = data["priority"]
            updateTicket.due_date = data["dueDate"]
            updateTicket.save()

            if "watchers" in data and "assignees" in data:
                updateTicket.watcher.set(data["watchers"])
                assignees = [User.objects.get(username__icontains=user) for user in data['assignees']]
                updateTicket.assigned_to.set(assignees)

            return JsonResponse({
                "msg": "update success",
                "status": 200
            }, status=200)
        else:
            return JsonResponse({
                "msg": "ticket is not found",
                "status": 404
            }, status=404)


@login_required
def mbtiResult(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = ""

    if user:
        roles = Role.objects.filter(user=user).order_by('-create_date')[:3]
        mbtiRes = MBTIResult.objects.filter(user=request.user.id).order_by('-create_date')[:3]

        return render(request, "capstone/mbti/mbti_result.html", {
            "personalities": mbtiRes,
            "roles": roles,
            "iconTitle": ICONS[5],
            "titleHeader": "MBTI Result" ,
            "subTitleHeader": "This page is intended to show your MBTI personality."
        })
    else:
        return render(request, "capstone/mbti/mbti_result.html")

@login_required
def ticketList(request, ticket_name):
    userId = request.user.id
    
    try:
        user = User.objects.get(pk=userId)
    except User.DoesNotExist:
        user = ""

    if user:
        if user.is_manager:
            tickets = getTickets(ticket_name, True).order_by('-due_date')
            outstanding = getTickets("outstanding", True)
            allTicket = getTickets("all", True)
            resolved = getTickets("resolved", True)
            dueToday = getTickets("due_today", True)
            overdue = getTickets("overdue", True)
        else:
            tickets = getTickets(ticket_name, False, userId).order_by('-due_date')
            outstanding = getTickets("outstanding", False, True)
            allTicket = getTickets("all", False, userId)
            resolved = getTickets("resolved", False, userId)
            dueToday = getTickets("due_today", False, userId)
            overdue = getTickets("overdue", False, userId)

    return render(request, "capstone/ticket/ticket_list.html", {
        "titleHeader": ticket_name.replace("_", " "),
        "tickets": tickets,
        "allTicket" : len(allTicket),
        "outstanding" : len(outstanding),
        "resolved" : len(resolved),
        "dueToday" : len(dueToday),
        "overdue" : len(overdue),
        "iconTitle": ICONS[3],
        "titleHeader": ticket_name.replace("_", " ").capitalize() + " Tickets" ,
        "subTitleHeader": "This page shows status of all tickets that has been created."
    })

def getTickets(ticket_name, is_manager=False, userId=""):
    today = datetime.now().date()

    if ticket_name == "all":
        if is_manager == True:
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(Q(requester=userId) | Q(assigned_to__in=[userId]) | Q(watcher=userId)).distinct()
    if ticket_name == "outstanding":
        if is_manager == True:
            tickets = Ticket.objects.all().exclude(status=3, is_finished=1)
        else:
            tickets = Ticket.objects.filter(Q(requester=userId) | Q(assigned_to__in=[userId]) | Q(watcher=userId)).exclude(status=3, is_finished=1).distinct()
    if ticket_name == "resolved":
        if is_manager == True:
            tickets = Ticket.objects.filter(status=3, is_finished=1)
        else:
            tickets = Ticket.objects.filter((Q(requester=userId) | Q(assigned_to__in=[userId]) | Q(watcher=userId)), status=3, is_finished=1).distinct()
    if ticket_name == "due_today":
        if is_manager == True:
            tickets = Ticket.objects.filter(due_date = today).exclude(status=3, is_finished=1)
        else:
            tickets = Ticket.objects.filter((Q(requester=userId) | Q(assigned_to__in=[userId]) | Q(watcher=userId)), due_date = today).exclude(status=3, is_finished=1).distinct()
    if ticket_name == "overdue":
        if is_manager == True:
            tickets = Ticket.objects.filter(due_date__lt = today).exclude(status=3, is_finished=1)
        else:
            tickets = Ticket.objects.filter((Q(requester=userId) | Q(assigned_to__in=[userId]) | Q(watcher=userId)), due_date__lt = today).exclude(status=3, is_finished=1).distinct()

    return tickets

@login_required
def users(request):
    return render(request, "capstone/users/index.html")

@login_required
def questionnaire(request, username):
    return render(request, "capstone/mbti/questionnaire.html", {
        "iconTitle": ICONS[4],
        "titleHeader": "Questionnaire" ,
        "subTitleHeader": "This page is used to know your personality according to MBTI test."
    })

@login_required
def profile(request):
    return render(request, "capstone/profile/index.html", {
        "titleHeader": "Profile" ,
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
    })

@login_required
def notification(request):
    userId = request.user.id
    notifications = Notification.objects.filter(send_to=userId).order_by('-create_date')
    return render(request, "capstone/notification/index.html", {
        "notifications": notifications,
        "titleHeader": "Notifications" ,
        "subTitleHeader": "This page is intended to show you all incoming notifications."
    })


@login_required
def saveQuestionnaire(request):
    q1 = request.POST["q1"]
    q2 = request.POST["q2"]
    q3 = request.POST["q3"]
    q4 = request.POST["q4"]
    ess1 = request.POST["ess1"]
    ess2 = request.POST["ess2"]

    
    newQ1 = MBTI_QUESTIONNAIRE_VALUE[1][0] if q1 in ('1', '2') else MBTI_QUESTIONNAIRE_VALUE[1][1]
    newQ2 = MBTI_QUESTIONNAIRE_VALUE[2][0] if q2 in ('1', '2') else MBTI_QUESTIONNAIRE_VALUE[2][1]
    newQ3 = MBTI_QUESTIONNAIRE_VALUE[3][0] if q3 in ('1', '2') else MBTI_QUESTIONNAIRE_VALUE[3][1]
    newQ4 = MBTI_QUESTIONNAIRE_VALUE[4][0] if q4 in ('1', '2') else MBTI_QUESTIONNAIRE_VALUE[4][1]

    sentences = ess1 + " " + ess2 + " " + newQ1 + " " + newQ2 + " " + newQ3 + " " + newQ4
    mbtiTraitValues = execMBTIModel(sentences)

    userScore = sortUserScore(mbtiTraitValues)

    # Save MBTI Score to DB
    for mbtiVal in mbtiTraitValues:
        mbti = MBTIResult(mbti_type=mbtiVal[0], value=round(mbtiVal[1] * 100, 2), user_id = request.user.id)
        mbti.save()

    # Save suitable role to DB
    for val in userScore:
        role = Role(user_id=request.user.id, role_type_id=val['id'], is_best=val['is_best'])
        role.save()

    messages.success(request, "You have submitted the questionnaire", extra_tags="MBTI Questionnaire")
    return HttpResponseRedirect(reverse('mbti_result', args=[request.user.username]))

def execMBTIModel(sentences):
    cols = ['INTJ', 'INTP', 'ISFJ', 'ISFP', 'ISTJ', 'ISTP', 'ENFJ', 'ENFP', 'ENTJ', 'ENTP', 'ESFJ', 'ESFP', 'ESTJ', 'ESTP', 'INFJ', 'INFP']

    colnames = ['sentence']
    colnames = colnames+cols

    with tf.keras.utils.custom_object_scope({"TFBertModel": TFBertModel}):
        model = load_model("capstone/ml_model/bert_uncased_model_new_10.h5")
    
    bert_model_name = 'bert-base-uncased'
    max_token = 512
    tokenizer = BertTokenizer.from_pretrained(bert_model_name, do_lower_case=True)
    
    df_predict = pd.DataFrame(columns = colnames)
    sentence = sentences

    df_predict.loc[0, 'sentence'] = sentence

    sentences = pd.Series(sentence)
        
    sentence_inputs = tokenize_sentences(df_predict['sentence'], tokenizer, max_token)
    sentence_inputs = pad_sequences(sentence_inputs, maxlen=max_token, dtype="long", value=0, truncating="post", padding="post")
    prediction = model.predict(sentence_inputs)
    
    df_predict.loc[0, cols] = prediction
    data = df_predict.loc[0, cols]
    
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    top_3_values = sorted_data[:3]
    
    return top_3_values


def sortUserScore(mbtiTraitValues):
    mbti_results = {key: round(value* 100, 2) for key, value in mbtiTraitValues}
    scores = {}
    for role, preferences in ROLE_PREFERENCES.items():
        scores[role] = calculateScore(preferences, mbti_results)

    # Sort the roles based on scores
    sortedRoles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    userRole = []
    categoryRoles = CategoryRole.objects.all()

    for cRole in categoryRoles:
        for val in sortedRoles:
            if val[0].lower() in cRole.role_name.lower():
                role = {'id': cRole.id, 'score': val[1]}
                userRole.append(role)

    sortedUserRole = sorted(userRole, key=lambda x: x['score'], reverse=True)

    for index, val in enumerate(sortedUserRole):
        if index == 0:
            val['is_best'] = 1
        else:
            val['is_best'] = 0
    
    return sortedUserRole[:3]


def calculateScore(role_preferences, mbti_results):
    score = 0
    for mbti_type, percentage in mbti_results.items():
        for trait in mbti_type:
            score += role_preferences.get(trait, 0) * percentage
    return score


def getTaskReq(roleId):
    roleId = int(roleId)

    if roleId == 1:
        role_tasks_req = ANALYST_TASKS_REQ
    elif roleId == 2:
        role_tasks_req = DESIGNER_TASKS_REQ
    elif roleId == 3:
        role_tasks_req = PROGRAMMER_TASKS_REQ
    elif roleId == 4:
        role_tasks_req = TESTER_TASKS_REQ
    elif roleId == 5:
        role_tasks_req = MAINTAINER_TASKS_REQ

    return role_tasks_req

def getRole(request, roleId):
    # Convert into integer value
    roleId = int(roleId)

    if roleId == 1:
        role_tasks_desc = ANALYST_TASKS_DESC
    elif roleId == 2:
        role_tasks_desc = DESIGNER_TASKS_DESC
    elif roleId == 3:
        role_tasks_desc = PROGRAMMER_TASKS_DESC
    elif roleId == 4:
        role_tasks_desc = TESTER_TASKS_DESC
    elif roleId == 5:
        role_tasks_desc = MAINTAINER_TASKS_DESC

    # return role_tasks_desc
    return JsonResponse(role_tasks_desc)

def getSuitableUsers(request):
    data = json.loads(request.body)
    all_selected_skills = []

    roleTaskReq = getTaskReq(1)

    for val in data["selectedValues"]: 
        all_selected_skills.extend(roleTaskReq.get(int(val), []))

    total_skills = len(all_selected_skills)
    skill_count = {}
    for skill in all_selected_skills:
        skill_count[skill] = skill_count.get(skill, 0) + 1

    skill_weightages = {skill: (count / total_skills) * 100 for skill, count in skill_count.items()}

    # Score calculation for each candidate
    candidates_score = []

    # Get MBTI values
    userMBTIVal = MBTIResult.objects.raw('SELECT m.id, m.mbti_type, m.user_id, u.username FROM capstone_mbtiresult m JOIN capstone_user u on m.user_id = u.id WHERE (m.value, m.user_id) IN (SELECT MAX(value) AS max_value, user_id FROM capstone_mbtiresult GROUP BY user_id)')

    for userVal in userMBTIVal:
        userDetail = {
            'uid': userVal.user_id,
            'name': userVal.username,
            'score': calculate_candidate_score(userVal.mbti_type, skill_weightages, SKILL_TO_MBTI),
            'totalTask': Ticket.objects.filter(assigned_to=userVal.user_id).count()
        }
        candidates_score.append(userDetail)

    sorted_candidates = sorted(candidates_score, key=lambda x: (-x['score'], -x['totalTask']))

    return JsonResponse(sorted_candidates, safe=False)

# Function to calculate the score based on MBTI mapping and skill weights.
def calculate_candidate_score(mbti_trait, skill_weightages, skills_to_mbti):
    score = 0
    for skill, weight in skill_weightages.items():
      for mbti_ele in mbti_trait:
        skill_match = skills_to_mbti.get(skill)
        if mbti_ele == skill_match:
            score += weight
    return score

def asyncNotification(request, userId):
    notifications = Notification.objects.filter(send_to=userId).order_by('-create_date')
    return JsonResponse([notif.serialize() for notif in notifications], safe=False)

def loginView(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "capstone/auth/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "capstone/auth/login.html")

def registerView(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        firstName = request.POST["first_name"]
        lastName = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmPassword = request.POST["confirm_password"]
        if password != confirmPassword:
            return render(request, "capstone/auth/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User(
                username = username,
                email = email,
                first_name = firstName,
                last_name = lastName,
                password = make_password(password)
            )
            user.save()
        except User.DoesNotExist:
            return render(request, "capstone/auth/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "capstone/auth/register.html")
    

def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# def mbti(request, username):
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         user = ""

#     questionnaire = Questionnaire.objects.filter(user=user.id)

#     if questionnaire:
#         # data_list = [
#         #     {'mbti_type': 'test', 'value': 50, 'user_id': 2},
#         #     {'mbti_type': 'test2', 'value': 23, 'user_id': 2},
#         #     {'mbti_type': 'test3', 'value': 10, 'user_id': 2}
#         # ]

#         # for data in data_list:
#         #     key_value_instance = MBTIResult(**data)
#         #     key_value_instance.save()
#         mbtiRes = MBTIResult.objects.filter(user=request.user.id)
#         print(mbtiRes)
#         return render(request, "capstone/mbti_result.html", {
#             "mbtiRes": mbtiRes
#         })
#     else:
#         return render(request, "capstone/questionnaire.html")

# data_list = [
#     {'mbti_type': 'test', 'value': 50, 'user_id': 2},
#     {'mbti_type': 'test2', 'value': 23, 'user_id': 2},
#     {'mbti_type': 'test3', 'value': 10, 'user_id': 2}
# ]