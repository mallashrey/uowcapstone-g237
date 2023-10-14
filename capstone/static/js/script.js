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
    
    let $ = document;

    const notifications = $.querySelector(".notifications"),
    buttons = $.querySelectorAll(".buttons .btn");

    const toastDetails = {
        timer: 500000,
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
        if (toast.timeoutId) clearTimeout(toast.timeoutId); // Clearing the timeout for the toast
        setTimeout(() => toast.remove(), 500) // Removing the toast after 500ms
    }

    const createToast = (id) => {
        // Getting the icon and text for the toast based on the id passed
        const { icon, text } = toastDetails[id];
        console.log(id)
        const toast = $.createElement("li"); // Creating a new 'li' element for the toast
        toast.className = `toast ${id}` // Setting the classes for the toast
        // Setting the inner HTML for the toast
        toast.innerHTML = `<div class="column">
                                <i class="fa-solid ${icon}"></i>
                                <span>${text}</span>
                            </div><i class="fa-solid fa-xmark" onclick="removeToast(this.parentElement)"></i>`
        notifications.appendChild(toast); // Append the toast to the notification ul
        // Setting a timeout to remove the toast after the specified duration
        toast.timeoutId = setTimeout(() => removeToast(toast), toastDetails.timer)
    }

    // Adding a click event listener to each button to create a toast when clicked
    buttons.forEach(btn => {
        btn.addEventListener("click", () => createToast(btn.id))
    });

    getRealTimeNotif();

    greetingMsg();

    realtimeClock();
    setInterval(realtimeClock, 1000)
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
                toastMixin.fire({
                    animation: true,
                    title: 'You got a new message'
                });
            }
        }

    }
}

function getNotification(userId) {
    fetch(`/async_notification/${userId}`)
        .then(response => response.json())
        .then(data => {
            totalNotif = document.querySelector('.notification-number');
            notifContainer = document.querySelector('.notif-list');
            notifContainer.innerHTML = "";
            totalNotif.innerHTML = data.length
            
            var divElement = document.createElement("div")
            divElement.style.height = "100%";
            divElement.style.maxHeight = "315px";
            divElement.style.overflowY = "scroll";

            for (let notif of data) {

                var imgRequester = ""
                if (notif.ticket.requester.img_profile) {
                    imgRequester = `/static/${notif.ticket.requester.img_profile}`
                } else {
                    imgRequester = `/static/images/user-icon.png`
                }

                divElement.innerHTML += `<a href="/ticket_detail/${notif.slug}" class="notif-row dflex gap20">
                                            <div> <img width="42" class="rounded-circle" src="${imgRequester}" alt=""> </div>
                                            <div class="dflex" style="flex-direction: column;">
                                                <div class="mb5">
                                                    <span>New task has been created. ${notif.ticket.ticket_title}</span>
                                                </div>
                                                <div class="dflex gap10">
                                                    <span><i class="fa-solid fa-clock"></i></span>
                                                    <span>time</span>
                                                </div>
                                            </div>
                                        </a>`
            }
            notifContainer.appendChild(divElement)
        })
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

// function selectAssignee() {
//     $('#assigneeModal').modal('show');
// }
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

        test123 = `<button class="btn btn-primary" id="proceed">Next</button>`

        reqRole.insertAdjacentHTML("beforeend", test123)
    })
})

$(document).on('click', '#proceed', function(event) {
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
                                <table class="table" id="user_score" style="background: #3d4e58;">
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
                                                <td>${val.score}</td>
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
    selectedUser = $(this).data('name');
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
    watchers = $("select[name='watchers[]']").val();
    // assignees = $("input[name='assigned_to[]']").val();
    assignees = $('input[name="assigned_to[]"]').map(function () {
        return this.value;
    }).get()
    dueDate = $("#due-date").val();
    console.log(assignees)

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

function getSelectedCell() {
    const table = document.getElementById('myTable');
    const rows = table.getElementsByTagName('tr');

    // Add click event listeners to table rows
    for (let i = 0; i < rows.length; i++) {
        rows[i].addEventListener('click', function() {
            // Handle row selection event here
            // You can access the row's data, e.g., cells[i].textContent
            console.log(`Row ${i + 1} selected: ${this.cells[0].textContent}, ${this.cells[1].textContent}`);
        });
    }
}

// function selectRole() {
//     fetch(`/get_role`)
//         .then(response => response.json())
//         .then(data => {
//             console.log(data)
//         })
// }



function selectRequirement() {
    alert("bbb")
}

function showHideNotification() {

    const notifBtn = document.querySelector('.notification');

    notifBtn.addEventListener("click", () => {
        let notifActive = document.querySelector(".notif-container");
        if (notifActive.classList.contains('active')) {
            showHideNotif(true)
        } else {
            showHideNotif(false)
        }
    })

    window.addEventListener("click", function (e) {
        if (e.target.closest(".notification") === null) {
            showHideNotif(true)
        }
    });
}

function showHideNotif(show) {
    const notifContainer = document.querySelector('.notif-container');

    if (show) {
        notifContainer.classList.remove('active')
    } else {
        notifContainer.classList.add('active')
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

