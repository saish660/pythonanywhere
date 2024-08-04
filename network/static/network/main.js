document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = getCookie('csrftoken');
    post_edit_buttons = document.querySelectorAll(".post-edit-button");
    post_edit_buttons.forEach((edit_button)=>{
        edit_button.onclick = () => {
            post = edit_button.closest(".post-card");
            post_id = post.dataset.id;
            message_div = post.querySelector(".post-message");
            original_message = message_div.innerHTML;
            message_div.innerHTML = `
            <textarea class="post-textarea" rows="3" cols="60">${original_message}</textarea>
            <button class="save-post-btn">Save</button>
            `;
            save_btn = post.querySelector(".save-post-btn");

            save_btn.onclick = () => {
                new_message = message_div.firstElementChild.value;
                save_post(post_id, new_message, message_div, csrfToken);
                message_div.innerHTML = `<i style="color: grey;">Saving changes...</i>`;
            }
            
        }
    });

    post_like_buttons = document.querySelectorAll(".like-button");
    post_like_buttons.forEach((like_button) => {
        like_button.onclick = () => {
            post = like_button.closest(".post-card");
            post_id = post.dataset.id;
            fetch("/toggle_like", {
                method: "POST",
                body: JSON.stringify({
                    post_id: post_id
                }),
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                }
            })
            .then((response) => response.json())
            .then((data) => {
                string = (data.action === "liked" ? "❤️ " : "🩶 ") + data.like_count;
                post.querySelector(".like-count").innerHTML = string;
            })
        }
    });

});


function save_post(post_id, new_message, message_div, csrfToken) {
    fetch("/edit_post", {
        method: "PUT",
        body: JSON.stringify({
            post_id: post_id,
            new_message: new_message,
        }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        }
    }).then(response => {
        if (response.ok) {
            message_div.innerHTML = new_message;
        }
        else{
            message_div.firstElementChild.innerHTML = "An unexpected error occured";
        }
    })
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


