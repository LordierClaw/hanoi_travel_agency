const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input #send-btn");
const attachmentBtn = document.querySelector(".chat-input #attachment-btn");
const fileInput = document.getElementById("image-upload");
const fileNameSpan = document.getElementById("file-name");

let userMessage = null; // Variable to store user's message
let imageUrl = null;
let imageFile = null;
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
  // Create a chat <li> element with passed message and className
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);
  let chatContent =
    className === "outgoing"
      ? `<p></p>`
      : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message;
  return chatLi; // return chat <li> element
};

const createChatLiHtml = (html, className) => {
  // Create a chat <li> element with passed message and className
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);
  let chatContent =
    className === "outgoing"
      ? `<p>${html}</p>`
      : `<span class="material-symbols-outlined">smart_toy</span><p>${html}</p>`;
  chatLi.innerHTML = chatContent;
  return chatLi; // return chat <li> element
};

const createChatLiImage = (imageUrl, className) => {
  // Create a chat <li> element with passed message and className
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);
  let chatContent =
    className === "outgoing"
      ? `<p></p>`
      : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector(
    "p"
  ).innerHTML = `<img src="${imageUrl}" alt="User uploaded image" style="max-width: 300px;">`;
  return chatLi; // return chat <li> element
};

const generateResponse = (chatElement) => {
  const API_URL = "/api/v1/chat";

  const formData = new FormData();

  if (!userMessage) return;
  formData.append("message", userMessage);
  if (imageFile) {
    formData.append("file", imageFile);
  }

  // Send POST request to API, get response and set the reponse as paragraph text
  fetch(API_URL, {
    method: "POST",
    body: formData,
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`API request failed with status ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      chatbox.removeChild(chatElement);
      if (!data.no_tour) {
        // Extract the response text from the "response" field
        const responseText = data.response;
        chatbox.appendChild(createChatLi(responseText, "incoming"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
      }
      // Check for additional response fields
      if (data.ocr_response) {
        chatbox.appendChild(createChatLi(data.ocr_response.trim(), "incoming"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
      }
      if (data.location_response) {
        const additionalResponse = `<a href="${data.location_response.google_map_url}">${data.location_response.name}, ${data.location_response.latitude}, ${data.location_response.longitude}</a>`;
        chatbox.appendChild(createChatLiHtml(additionalResponse, "incoming"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
      }
      if (data.no_tour) {
        chatbox.appendChild(createChatLi(data.no_tour.trim(), "incoming"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
      } else if (data.tour_detail) {
        let additionalResponse = "";
        // data.tour_detail.forEach((tour) => {
        //     additionalResponse += `<a ${tour.destination}, ${tour.price}</a><br>`;
        // });
        //sinh ra cac the a, bam vao goi ham showTourDetail(id)
        console.log(data.tour_detail);
        //additionalResponse += `<a detailTour idTour="${data.tour_detail.id}">${data.tour_detail.destination}, ${data.tour_detail.price}</a>`;
        data.tour_detail.forEach((tour) => {
          additionalResponse += `<a detailTour style="color:blue; text-decoration: underline;" idTour="${tour.id}"> ${tour.details}</a><br>`;
        });
        chatbox.appendChild(createChatLiHtml(additionalResponse, "incoming"));
        chatbox.scrollTo(0, chatbox.scrollHeight);
        SetClickForTourDetailInstantiate();
      }
    })
    .catch((error) => {
      chatbox.removeChild(chatElement);
      const errorMessage = createChatLi(
        "Oops! Something went wrong. Please try again.",
        "incoming"
      );
      errorMessage.classList.add("error");
      chatbox.appendChild(errorMessage);
      console.error("Error generating response:", error);
      chatbox.scrollTo(0, chatbox.scrollHeight);
    })
    .finally(() => {
      imageFile = null;
      imageUrl = null;
      fileNameSpan.textContent = "";
    });
};

const SetClickForTourDetailInstantiate = () => {
  const listButtonTour = document.querySelectorAll("[detailTour]");
  console.log(listButtonTour);
  listButtonTour.forEach((btn) => {
    //href = detail/id
    btn.addEventListener("click", (e) => {
      const id = e.target.getAttribute("idTour");
      console.log(id);
      showTourDetail(id);
    });
  });
};

const handleChat = () => {
  userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
  if (!userMessage) return;

  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the user's message to the chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);
  if (imageUrl) {
    chatbox.appendChild(createChatLiImage(imageUrl, "outgoing"));
  }
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // Display "Thinking..." message while waiting for the response
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi);
  }, 600);
};

chatInput.addEventListener("input", () => {
  // Adjust the height of the input textarea based on its content
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
  // If Enter key is pressed without Shift key and the window
  // width is greater than 800px, handle the chat
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

sendChatBtn.addEventListener("click", (e) => {
  e.preventDefault(); // Prevent default form submission
  handleChat();
});

attachmentBtn.addEventListener("click", function () {
  document.getElementById("image-upload").click();
});

fileInput.addEventListener("change", function () {
  const fileName = this.value.split("\\").pop(); // Extract filename
  const maxChars = 25;
  const displayedName =
    fileName.length > maxChars ? fileName.slice(0, maxChars) + "..." : fileName;
  fileNameSpan.textContent = displayedName ? `${displayedName}` : "";
  if (fileInput.files.length > 0) {
    imageUrl = URL.createObjectURL(fileInput.files[0]);
    imageFile = fileInput.files[0];
  }
});

closeBtn.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);

window.scrollTo({
  top: 0,
  behavior: "smooth",
});

//xử lý các nút chuyển trang và sinh dữ liệu
const allTourDiv = document.querySelectorAll(".listProduct");
console.log(allTourDiv);
showAllTours();

async function showAllTours() {
  //fetch data from api and display all tours
  await fetch("/api/v1/tours")
    .then((res) => res.json())
    .then((data) => {
      allTourDiv.forEach((div) => {
        tourDetail.innerHTML = "";
        div.innerHTML = "";
        console.log(data);
        data.forEach((tour) => {
          console.log(tour);
          const tourDiv = document.createElement("a");

          //target="_blank"
          tourDiv.addEventListener("click", (e) => {
            const id = tour.id;
            console.log(id);
            showTourDetail(id);
          });
          tourDiv.classList.add("col-md-4");
          tourDiv.innerHTML = `
          <div class="card tour-card">
              <img src="${tour.img_url}" style="height: 200px;" 
                  class="card-img-top" alt="Tour Image 1">
              <div class="card-body">
                  <h4 class="card-title">${tour.destination}</h4>
                  <p class="card-text" style="color: red;font-size:23px;">Giá: $${tour.price}</p>
                  <p class="card-text" style="color: green;font-size:23px;">${tour.duration.days} Ngày, ${tour.duration.nights} Đêm</p>
              </div>
          </div>
            `;
          div.appendChild(tourDiv);
        });
      });
    })
    .catch((err) => console.error(err));
}

const tourDetail = document.querySelector(".tourDetail");
console.log(tourDetail);

async function showTourDetail(id) {
  //fetch data from api and display all tours
  await fetch("/api/v1/tour_detail/" + id)
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      allTourDiv.forEach((div) => {
        div.innerHTML = "";
      });
      tourDetail.innerHTML = "";
      tourDetail.innerHTML = `
      <div class="tour-header">
      <h2>${data.destination}</h2>
  </div>

  <div class="tour-info">
      <div class="tour-info-left">
          <img src="${data.img_url}" alt="Tour Image" class="tour-info-img">
      </div>
      <div class="tour-info-right">
          <div class="row tour-details">
              <div class="col-md-12 departure">
                  <h3>Điểm xuất phát: ${data.departurePoint}</h3>
              </div>
              <div class="col-md-12 price">
                  <h3>Giá: $${data.price}</h3>
              </div>
              <div class="col-md-12 destination">
                  <h3>Điểm đến: ${data.destination}</h3>
              </div>
              <div class="col-md-12 duration">
                  <h3>Thời gian: ${data.duration.days} Ngày, ${data.duration.nights} Đêm</h3>
              </div>
          </div>
      </div>
  </div>`;

      // <div class="row">
      //     <div class="col-md-4 day-list">`;
      //     data.details.forEach((detail) => {
      //       tourDetail.innerHTML += `
      //       <h6>${detail.day} - ${detail.title}</h6>
      //       `;
      //     });
      var stringAdd = `
      <div class="row">
      <div class="col-md-4 day-list">
      `;
      data.details.forEach((detail) => {
        stringAdd += `
        <h6>${detail.day} - ${detail.title}</h6>
        `;
      });
      stringAdd += `
      </div>
      `;
      stringAdd += `
      <div class="col-md-8 day-content">
      `;
      data.details.forEach((detail) => {
        stringAdd += `
        <h6>${detail.day} - ${detail.title}</h6>
        <p>${detail.description}</p>
        `;
      });
      stringAdd += `
      </div>
      </div>
      `;
      tourDetail.innerHTML += stringAdd;
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    })
    .catch((err) => console.error(err));
}

const listButtonTour = document.querySelectorAll("[btnTour]");
console.log(listButtonTour);
listButtonTour.forEach((btn) => {
  //href = detail/id
  btn.addEventListener("click", (e) => {
    const id = e.target.getAttribute("idTour");
    console.log(id);
    showTourDetail(id);
  });
});

const btnHome = document.querySelector(".homeBtn");
btnHome.addEventListener("click", (e) => {
  showAllTours();
});

//xử lý filter
