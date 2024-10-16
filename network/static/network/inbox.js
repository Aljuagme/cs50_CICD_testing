console.log("Is the script loaded?");

function send_email(event) {
    // event.preventDefault()
    console.log("AM I HERE======?")

    const body = document.getElementById("compose-body").value
    console.log(body)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch("/compose", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({body: body})
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
        })
}

function handlerLike(button) {
    const postId = button.dataset.postId;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = `/toggle_like/${postId}`

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data["liked"]) {
                button.textContent = "Unlike";
            } else {
                button.textContent= "Like"
            }
            const likeCountSpan = button.nextElementSibling;
            likeCountSpan.textContent = `${data["like_count"]} likes`;
        })
        .catch(error => console.log("Error", error));
}

function editPost(postId) {
    const postBody = document.getElementById(`body-${postId}`)
    const currentBody = postBody.innerText;

    const textarea = document.createElement("textarea");
    textarea.value = currentBody;
    textarea.id = `edit-body-${postId}`

    const saveButton = document.createElement("button");
    saveButton.innerText = "Save";
    saveButton.onclick = function () {savePost(postId)}

    postBody.innerHTML = "";
    postBody.appendChild(textarea);
    postBody.appendChild(saveButton);
}

function savePost(postId) {
    const updatedBody = document.getElementById(`edit-body-${postId}`).value;
    const url = `/edit_post/${parseInt(postId)}`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(url, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            body: updatedBody
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error when updating a post");
            }
            return response.json()
        })
        .then(data => {
            if (data.Success) {
                const postBodyElement = document.getElementById(`body-${postId}`);
                postBodyElement.innerHTML = updatedBody;

            } else {
                console.log(data.message);
            }
        })
}



function handleFollowers(userId, action) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;


    fetch(`/follow/${parseInt(userId)}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            action: action
        })
    })
    .then(response => response.json())
    .then(result => {
        // Handle success or error response here
        if (result.success) {
            // Reload the page or update the button dynamically
            window.location.reload();
        } else {
            alert(result.error);
        }
    })
    .catch(error => console.log("Error:", error));
}

function show_emails() {
    const url = `/emails`

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to show emails");
            }
            return response.json()
    }).then(data => {
        data.forEach()
    })
}



