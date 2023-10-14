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

import json
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
    mbtiRes = MBTIResult.objects.filter(user=request.user.id)

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
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
    })

def testChannel(request):
    return render(request, "capstone/testchannel.html")

@login_required
def category(request):
    categories = Category.objects.all().order_by('name')
    
    return render(request, "capstone/category/index.html", {
        "categories": categories,
        "iconTitle": ICONS[1],
        "titleHeader": "Category",
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
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
            "subTitleHeader": "This is an example dashboard created using build-in elements and components."
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
            "subTitleHeader": "This is an example dashboard created using build-in elements and components."
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

@login_required
def saveNotification(notif, ticketId, requester):

    # if notif == 1:
    #     objs = [
    #         Notification(
    #             notification = notif,
    #             ticket_id = ticketId,
    #             user_id = u.id
    #         )
    #         for u in User.objects.filter(is_manager=True)
    #     ]

    #     notif = Notification.objects.bulk_create(objs)

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
    if request.method == "POST":

        requester = request.user.id

        if request.user.is_manager:
            # array_values = request.POST.getlist('watchers[]')
            # print(array_values)
            categoryRole = request.POST["category_role"].strip()
            selected_requirements = request.POST["requirement"].strip().split(", ")
            # role = getRole(categoryRole)
            role = "a"

            # Calculate the weightage of each skill dynamically
            all_selected_skills = []
            for req in selected_requirements:
                all_selected_skills.extend(role.get(req, []))

            total_skills = len(all_selected_skills)
            skill_count = {}
            for skill in all_selected_skills:
                skill_count[skill] = skill_count.get(skill, 0) + 1

            skill_weightages = {skill: (count / total_skills) * 100 for skill, count in skill_count.items()}

            # Score calculation for each candidate
            candidates_score = {}

            # Get MBTI values
            userMBTIVal = MBTIResult.objects.raw('SELECT m.id, m.mbti_type, m.user_id, u.username FROM capstone_mbtiresult m JOIN capstone_user u on m.user_id = u.id WHERE (m.value, m.user_id) IN (SELECT MAX(value) AS max_value, user_id FROM capstone_mbtiresult GROUP BY user_id)')

            for userVal in userMBTIVal:
                candidates_score[userVal.username] = calculate_candidate_score(userVal.mbti_type, skill_weightages, SKILL_TO_MBTI)

            sorted_candidates = sorted(candidates_score.items(), key=lambda x: x[1], reverse=True)

            # Output sorted candidates and their scores
            for candidate, score in sorted_candidates:
                print(f"{candidate}: {score:.2f}")


        ticket = Ticket(
            ticket_title = request.POST["ticket_title"].strip(),
            description = request.POST["ticket_description"].strip(),
            category_id = request.POST["category"].strip(),
            priority = request.POST["priority"].strip(),
            requester_id = requester,
            due_date = request.POST["due-date"].strip()
        )
        ticket.save()

        saveNotification(1, ticket.id, requester)

        # =============  Django Channel notification does not work with create_bulk =============
        # task_title = request.POST["task_title"]
        # task_desc = request.POST["description"]
        # task_cat = request.POST["category"]
        # task_priority = request.POST["priority"]
        # task_soft_skill = "".join(request.POST.getlist("soft_skill"))
        # user = request.POST["user"]

        # print(f"title: {task_title}, desc: {task_desc}, cat: {task_cat}")
        # task = Task(
        #     = request.POST[""]
        # )
        # ============= End of Django Channel notification does not work with create_bulk =============
        
        
        return HttpResponseRedirect(reverse("create_ticket"))
    else:
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
            "subTitleHeader": "This is an example dashboard created using build-in elements and components."
        })
    
@login_required
def ticketDetail(request, ticket_name):
    ticketName = ticket_name.replace('-', ' ')
    ticketDetail = Ticket.objects.get(ticket_title__icontains=ticketName)
    categories = Category.objects.all()
    categoryRoles = CategoryRole.objects.all()
    watchers = User.objects.filter(dept=1)

    watcherIds = ', '.join([str(watcher.id) for watcher in ticketDetail.watcher.all()])
    print(watcherIds)

    print(ticketDetail.watcher)
    if 0 in STATUS:
        print("yes")
    else:
        print("no")
    
    return render(request, "capstone/ticket/ticket_detail.html", {
        "ticketDetail": ticketDetail,
        "categories": categories,
        "priority": PRIORITY,
        "status": STATUS,
        "categoryRoles": categoryRoles,
        "watchers": watchers,
        "watcherIds": watcherIds,
        "titleHeader": "Ticket Detail" ,
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
    })
    
@login_required
def saveTicket(request):
    data = json.loads(request.body)

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
    
    return JsonResponse({
        "msg": "success",
        "status": 200
    }, status=200)

@login_required
def mbtiResult(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = ""

    if user:
        roles = Role.objects.filter(user=user).order_by('-is_best')
        mbtiRes = MBTIResult.objects.filter(user=request.user.id)

        return render(request, "capstone/mbti/mbti_result.html", {
            "personalities": mbtiRes,
            "roles": roles,
            "iconTitle": ICONS[5],
            "titleHeader": "MBTI Result" ,
            "subTitleHeader": "This is an example dashboard created using build-in elements and components."
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
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
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
        "titleHeader": "Questionnaire" ,
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
    })

@login_required
def profile(request):
    return render(request, "capstone/profile/index.html", {
        "titleHeader": "Profile" ,
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
    })

@login_required
def saveQuestionnaire(request):
    q1 = request.POST["q1"]
    q2 = request.POST["q2"]
    q3 = request.POST["q3"]
    q4 = request.POST["q4"]
    ess1 = request.POST["ess1"]
    ess2 = request.POST["ess2"]

    questionnaire = Questionnaire(
        opt_ans1 = q1,
        opt_ans2 = q2,
        opt_ans3 = q3,
        opt_ans4 = q4,
        txt_ans1 = ess1,
        txt_ans2 = ess2,
        user_id = request.user.id
    )
    questionnaire.save()

    messages.success(request, "You have submitted the questionnaire", extra_tags="MBTI Questionnaire")
    return HttpResponseRedirect(reverse('mbti', args=[request.user.username]))

@login_required
def notification(request):
    userId = request.user.id
    notifications = Notification.objects.filter(send_to=userId).order_by('-create_date')
    return render(request, "capstone/notification/index.html", {
        "notifications": notifications,
        "titleHeader": "Notifications" ,
        "subTitleHeader": "This is an example dashboard created using build-in elements and components."
    })

# Depending on the role, fetch the role's ticket requirements dictionary
# def getRole(role):

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

    # val = ess1 + " " + ess2
    # predicted_class, predicted_score = mbtiModel(val)

    # return render(request, "capstone/mbti_result.html", {
    #     "predicted_class": PERSONAlITY_TYPES.get(predicted_class),
    #     "predicted_score": round(predicted_score *100 ,2)
    # })

    # def mbtiResult1(request):

    #     mbti_values = mbtiVal1("qqq")
    #     dict_mbti = []
        
    #     for val in mbti_values:
    #         dict_mbti.append({
    #             "class": val[0],
    #             "score": math.ceil(val[1] * 100) / 100
    #         })


    #     return render(request, "capstone/mbti_result.html", {
    #         "values": dict_mbti
    #     })



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
    

# def editTask(request, id):
#     try:
#         task = Ticket.objects.get(pk=id)
#     except Ticket.DoesNotExist:
#         task = ""

#     if request.method == "POST":
#         if task:
#             task.task_title = request.POST["task_title"].lstrip()
#             task.save()

#             messages.info(request, "Task has been updated successfully")
#             return HttpResponseRedirect(reverse("task"))
#     else:
#         categories = Category.objects.all()
#         users = User.objects.all()
#         return render(request, "capstone/ticket/edit.html", {
#             "categories": categories,
#             "users": users,
#             "task": task
#         })

# def deleteTask(request, id):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST method request is required"})
    
#     try:
#         task = Ticket.objects.get(pk=id)
#     except Ticket.DoesNotExist:
#         task = ""
    
#     if task:
#         task.delete()
#         return JsonResponse({
#             "message": "Data has been deleted successfully"
#         }, status=200)
#     else:
#         return JsonResponse({
#             "message": "There is a mistaken when deleting data"
#         }, status=400)