$(document).ready(function () {
    


    // const wrapper = document.querySelector(".wrapper"),
    // selectBtn = wrapper.querySelector(".select-btn"),
    // svgElement = selectBtn.querySelector(".arrow")

    // selectBtn.addEventListener("click", () => {
    //     wrapper.classList.toggle("active")
    //     // Check if the "rotated" class is already present on the SVG element
    //     if (svgElement.classList.contains("rotated")) {
    //         // If it is present, remove the "rotated" class
    //         svgElement.classList.remove("rotated");
    //     } else {
    //         // If it is not present, add the "rotated" class
    //         svgElement.classList.add("rotated");
    //     }
    // })
    
    getRealTimeNotif();

    greetingMsg();

    realtimeClock();
    setInterval(realtimeClock, 1000)
})

const toastDetails = {
    timer: 5000,
    success: {
        icon: "fa-circle-check",
        text: "Success: This is a success toast."
    },
    error: {
        icon: "fa-circle-xmark",
        text: "Error: This is an error toast."
    },
    warning: {
        icon: "fa-circle-exclamation",
        text: "Warning: This is a warning toast."
    },
    info: {
        icon: "fa-circle-info",
        text: "Info: This is an information toast."
    }
}

const removeToast = (toast) => {
    toast.classList.add("hide")
    if (toast.timeoutId) clearTimeout(toast.timeoutId); 
    setTimeout(() => toast.remove(), 500)
}

const generateToast = (id, msg) => {
    const notifications = document.querySelector(".notifications");
    
    const icon = toastDetails[id];
    
    const toast = document.createElement("li");
    toast.className = `toast ${id}`
    
    toast.innerHTML = `<div class="column">
                            <i class="fa-solid ${icon.icon}"></i>
                            <span>${msg}</span>
                        </div>
                        <i class="fa-solid fa-xmark close-notif"></i>`
    notifications.appendChild(toast);
    
    toast.timeoutId = setTimeout(() => removeToast(toast), toastDetails.timer)
}

$(document).on('click', '.close-notif', function(e) {
    removeToast(this.parentElement)
})

const addAssignee = document.querySelector('#add_assignee');
if (addAssignee !== null) {
    addAssignee.addEventListener("click", () => {
        var assignedToInput = document.querySelectorAll('input[name="assigned_to[]"]');
    
        hasValue = true;
        
        assignedToInput.forEach(function(el) {
            var elValue = el.value;
    
            if (elValue === null || elValue === "") {
                hasValue = false;
            }
        })
    
        if (hasValue) {
            var assignedToDiv = document.querySelector('#assigned_to');
            var newAssigneeInput = '<input type="text" name="assigned_to[]" class="form-caps form-input assigned-input" placeholder="Select Assigned to" autocomplete="off" required></input>'
    
            assignedToDiv.insertAdjacentHTML("beforeend", newAssigneeInput)
        } else {
            alert("You must choose assignee first before add more column")
        }
        
    })
}


function greetingMsg() {
    const presentTime = new Date().getHours();

    var greeting = "Hi, Good Evening";

    if (presentTime >= 5 && presentTime < 12) {
        greeting = "Hi, Good Morning";
    }
    if (presentTime >= 12 && presentTime < 17) {
        greeting = "Hi, Good Afternoon";
    }

    var greetMsg = document.querySelector('.greeting-msg')
    if (greetMsg !== null) {
        greetMsg.innerHTML = greeting
    }
}

function getRealTimeNotif () {
    getUserId = JSON.parse(document.getElementById('uid').innerText);
    
    let url = `ws://${window.location.host}/ws/socket-server/`

    const chatSocket = new WebSocket(url)
    
    chatSocket.onmessage = function(e) {
        
        let data = JSON.parse(e.data)
        if (data.hasOwnProperty("payload") && "receiver" in data["payload"]) {
            if (data.payload.receiver == getUserId) {
                getNotification(getUserId)
                generateToast("info", "New task has been added")
            }
        }

    }
}

function getNotification(userId) {
    fetch(`/async_notification/${userId}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            totalNotif = document.querySelector('.notification-number');
            notifContainer = document.querySelector('.notif-list');
            notifContainer.innerHTML = "";
            
            const unreadNotif = data.filter(item => item.is_read === false);
            totalNotif.innerHTML = unreadNotif.length

            var divElement = document.createElement("div")
            divElement.style.height = "100%";
            divElement.style.maxHeight = "315px";
            divElement.style.overflowY = "scroll";

            for (let notif of data) {

                var imgRequester = ""
                var isRead = ""
                var msg = ""
                if (notif.ticket.requester.img_profile) {
                    imgRequester = `/static/${notif.ticket.requester.img_profile}`
                } else {
                    imgRequester = `/static/images/user-icon.png`
                }

                if(!notif.is_read) {
                    isRead = `<span style="font-weight: 600; color: #f9fd44;">Unread!</span>`
                }

                msg = generateMsg(notif.notification)

                divElement.innerHTML += `<a href="/read_ticket/${notif.ticket.id}" class="notif-row dflex gap20">
                                            <div> <img width="42" class="rounded-circle" src="${imgRequester}" alt=""> </div>
                                            <div class="dflex" style="flex-direction: column;">
                                                <div class="mb5">
                                                    ${isRead}
                                                    <span>${msg}. <b style="color: #8eff4d;">${notif.ticket.ticket_title}</b></span>
                                                </div>
                                                <div class="dflex gap10">
                                                    <span><i class="fa-solid fa-clock"></i></span>
                                                    <span>${dateFormat(notif.create_date, 'long')}</span>
                                                </div>
                                            </div>
                                        </a>`
            }
            notifContainer.appendChild(divElement)
        })
}

function generateMsg(type) {

    var msgType = {
        1: "New task has been created",
        2: "You received new ticket!",
        3: "Ticket status has been changed to In Progress",
        4: "Ticket status has been changed to In Review",
        5: "Ticket is closed."
    };
    
    return msgType[type]
}

function realtimeClock() {
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    var time = new Date();
    var hours = startWithZero(time.getHours(), 2);
    var minutes = startWithZero(time.getMinutes(), 2);
    var seconds = startWithZero(time.getSeconds(), 2);
    var day = time.getDay();
    var date = time.getDate();
    var month = time.getMonth();
    var year = time.getFullYear();
    
    var clock = document.querySelector(".clock");
    var datetime = document.querySelector(".date");
    if (clock !== null && datetime !== null) {
        clock.innerHTML = hours + ":" + minutes + ":" + seconds
        datetime.innerHTML = `${days[day]}, ${startWithZero(date, 2)} 
                                                ${months[month]} ${startWithZero(year, 2)}`
    }
    
}

function startWithZero(val, digit) {
    return String(val).padStart(digit, '0');
}


$(document).on("click", ".input-holder", function(e) {
    const parentElement = $(e.target).closest(".search-wrapper");
    parentElement.addClass("active")
})

$(document).on("click", ".btn-search-close", function(e) {
    const searchWrapper = $(".search-wrapper.active");

    searchWrapper.removeClass("active")
});

$(document).on("click", ".search-wrapper.active > .input-holder > .search-icon", function(e) {
    searchTicket(e.target.value)
})

$(".search-input").on("change", function(e) {
    searchTicket(e.target.value)
})

function searchTicket(keyword) {
    window.location = `/tickets?search_keyword=${keyword}`
}

var inputActive = ""
var selectedUser = "";

var table = document.querySelector('#assignee-list')
var reqRole = document.querySelector('#requirements-role')


$(document).on('click', 'input[name="assigned_to[]"]', function(e) {
    $('#assigneeModal').modal('show');
    inputActive = $(this);
});

$(document).on('change', '#category_role', function(event) {
    roleId = event.target.value;
    table.innerHTML = ""
    if (roleId != 0) {
        fetch(`/get_role/${roleId}`)
        .then(response => response.json())
        .then(data => {
            reqRole = document.querySelector('#requirements-role')
            reqRole.innerHTML = ""
            for (let role in data) {
                reqRole.innerHTML += `<div class="form-check">
                <input class="form-check-input" name=reqRole[] value=${role} type="checkbox" id="flexCheckDefault">
                <label class="form-check-label" for="flexCheckDefault">
                ${data[role]}
                </label>
            </div>`
            }

            // test123 = `<button class="btn btn-primary" id="proceed">Next</button>`

            // reqRole.insertAdjacentHTML("beforeend", test123)
            $('#searchEmployeeBtn').removeClass('dnone')
            $('#searchEmployeeBtn').prop('disabled', true);
            $('#setAssignee').prop('disabled', true);
            $('#setAssignee').addClass('dnone')
        })
    } else {
        $('#searchEmployeeBtn').addClass('dnone')
        $('#setAssignee').prop('disabled', true);
        $('#setAssignee').addClass('dnone')
        table.innerHTML = ""
        reqRole.innerHTML = ""
    }
    
})

$(document).on('click', 'input[name="reqRole[]"]', function(event) {
    if ($('input[name="reqRole[]"]:checked').length > 0) {
        $('#searchEmployeeBtn').prop('disabled', false);
    } else {
        $('#searchEmployeeBtn').prop('disabled', true);
    }
});

$(document).on('click', '#searchEmployeeBtn', function(event) {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    var selectedValues = Array.from(document.querySelectorAll('input[name="reqRole[]"]:checked'))
    .map(function (checkbox) {
      return checkbox.value;
    });

    fetch(`/get_suitable_users`, {
        method: "POST",
        credentials: 'same-origin',
        headers: {
            "X-CSRFToken": token,
            "Content-Type": 'application/json'
        },
        body: JSON.stringify({
            'selectedValues': selectedValues
        })
    })
    .then(response => response.json())
    .then(data => {
        table.innerHTML = `<div class="app-card__body">
                                <table class="table table-hover" id="user_score" style="background: #3d4e58;">
                                    <thead>
                                        <tr>
                                            <th class="table-th-header" scope="col" style="width:35%;">User</th>
                                            <th class="table-th-header" scope="col">Score</th>
                                            <th class="table-th-header" scope="col">Total Tasks</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.map(val => `
                                            <tr data-name="${val.name}">
                                                <td>${val.name}</td>
                                                <td>${val.score.toFixed(2)}</td>
                                                <td>${val.totalTask}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>`
                        })

        var setAssigneeBtn = document.getElementById('setAssignee');
        setAssigneeBtn.disabled = false

})


$(document).on('click', '#user_score tbody tr', function(e) {
    $('#user_score tbody tr').removeClass('active-row');
    $(this).addClass('active-row')
    selectedUser = $(this).data('name');
    $('#setAssignee').prop('disabled', false);
    $('#setAssignee').removeClass('dnone')
})

$(document).on('click', '#setAssignee', function() {
    inputActive.val(capitalizeText(selectedUser))
    $('#assigneeModal').modal('hide');
    table.innerHTML = ""
    reqRole.innerHTML = ""
})

$(document).on('click', '#btn-save-ticket', function() {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    if ($("#ticketId").length > 0) {
        id = $("#ticketId").val()
    } else {
        id = 0
    }

    title = $("#ticket_title").val()
    desc = $("#ticket_desc").val()
    category = $("#ticket_category").val();
    priority = $("#ticket_priority").val();
    ticket_status = $("#ticket_status").val();
    watchers = $("select[name='watchers[]']").val();
    // assignees = $("input[name='assigned_to[]']").val();
    assignees = $('input[name="assigned_to[]"]').map(function () {
        return this.value;
    }).get()
    dueDate = $("#due-date").val();
    if (!ticket_status) {
        ticket_status = 0
    }

    fetch('/save_ticket', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': token,
            'Content-Type':  'application/json'
        },
        body: JSON.stringify({
            'id': id,
            'title': title,
            'desc': desc,
            'category': category,
            'priority': priority,
            'status': ticket_status,
            'watchers': watchers,
            'assignees': assignees,
            'dueDate': dueDate
        })
    })
    .then(response => response.json())
    .then(res => {
        if (res.status == 200) {
            if (id == 0) {
                showSwalMsg("New ticket has been created successfully")
            } else {
                showSwalMsg("You ticket has been created successfully")
            }
        } else {
            alert("Cannot save");
        }
    })
    .catch(err => {
        alert(err)
    })
})

$(document).on('click', '.btn-questionnaire', function(event) {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    const q1 = document.getElementsByName('q1')[0].value;
    const q2 = document.getElementsByName('q2')[0].value;
    const q3 = document.getElementsByName('q3')[0].value;
    const q4 = document.getElementsByName('q4')[0].value;
    const ess1 = document.getElementsByName('ess1')[0].value;
    const ess2 = document.getElementsByName('ess2')[0].value;
    const username = document.getElementsByName('username')[0].value;
    loading_spinner();

    fetch('/save_questionnaire', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'q1': q1,
            'q2': q2,
            'q3': q3,
            'q4': q4,
            'ess1': ess1,
            'ess2': ess2
        })
    })
    .then(response => response.json())
    .then(res => {
        if (res.status == 200) {
            progressCompletion(username)
        } else {
            alert("Cannot save");
        }
    })
    .catch(err => {
        alert(err)
    })
    
})

function loading_spinner() {
    Swal.fire({
        title: 'Please wait...',
        html: ` <div class="qwerty">Your MBTI result is being processing.</div>
                <div class="loading-spinner">
                    <div class="loading-spinner-dot"></div>
                    <div class="loading-spinner-dot"></div>
                    <div class="loading-spinner-dot"></div>
                    <div class="loading-spinner-dot"></div>
                    <div class="loading-spinner-dot"></div>
                    <div class="loading-spinner-dot"></div>
                </div>`,
        showConfirmButton: false,
        allowOutsideClick: false
      })
}

function progressCompletion(user) {
    Swal.fire({
        icon: 'success',
        title: 'Success',
        text: 'Your MBTI result has been released.'
    }).then((result) => {
        window.location.href = `/mbti_result/${user}`
    })
}

function showSwalMsg(msg) {
    Swal.fire({
        icon: 'success',
        title: 'Success',
        text: msg
    }).then((rslt) => {
        if (rslt.isConfirmed) {
            window.location.href = '/ticket_list/all'
        }
    })
}

function capitalizeText(str) {
    if (str.length === 0) return str;

    return str.charAt(0).toUpperCase() + str.slice(1);
  }

document.querySelector('.notification').addEventListener("click", (e) => {
    
    let notifActive = document.querySelector(".notif-container");
    if (notifActive.classList.contains('active')) {
        showHideDropdown(notifActive, true)
    } else {
        showHideDropdown(notifActive, false)
    }
    
})

document.querySelector('.widget-account').addEventListener("click", (e) => {
    
    let widgetActive = document.querySelector(".widget-account-header");
    if (widgetActive.classList.contains('active')) {
        showHideDropdown(widgetActive, true)
    } else {
        showHideDropdown(widgetActive, false)
    }
    
})

window.addEventListener("click", function (e) {
    let widgetActive = document.querySelector(".widget-account-header");
    if (e.target.closest(".widget-account") === null) {
        showHideDropdown(widgetActive, true)
    }

    let notifActive = document.querySelector(".notif-container");
    if (e.target.closest(".notification") === null) {
        showHideDropdown(notifActive, true)
    }
});

function showHideDropdown(elClass, show) {
    if (show) {
        elClass.classList.remove('active')
    } else {
        elClass.classList.add('active')
    }
}

function delete_data(type, id) {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;


    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/${type}/${id}`, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    "X-CSRFToken": token,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(res => {
                Swal.fire({
                    title: "Deleted!",
                    text: "Your file has been deleted.",
                    icon: "success"
                }).then((res) => {
                    location.reload();
                })
            })
            .catch((error) => {
                alert(error)
                location.reload()
            });
        }
    })
    
}
  