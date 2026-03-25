const inputType = document.getElementById("inputType");
const textInput = document.getElementById("textInput");
const fileInput = document.getElementById("fileInput");
const youtubeInput = document.getElementById("youtubeInput");
const resultBox = document.getElementById("result");

// 🔄 SWITCH INPUT TYPE UI
inputType.addEventListener("change", () => {
  textInput.style.display = "none";
  fileInput.style.display = "none";
  youtubeInput.style.display = "none";

  if (inputType.value === "text") {
    textInput.style.display = "block";
  } 
  else if (inputType.value === "pdf") {
    fileInput.style.display = "block";
  } 
  else if (inputType.value === "youtube") {
    youtubeInput.style.display = "block";
  }
});

// default visible
textInput.style.display = "block";

// 🚀 MAIN FUNCTION
async function submitData() {
  const type = inputType.value;
  const mode = document.getElementById("mode").value;

  resultBox.innerHTML = "⏳ Processing... Please wait";

  try {
    let response;

    // 📄 TEXT INPUT
    if (type === "text") {
      const textValue = textInput.value.trim();

      if (!textValue) {
        resultBox.innerHTML = "⚠️ Please enter some text!";
        return;
      }

      response = await fetch("/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          type: "text",
          mode: mode,
          content: textValue
        })
      });
    }

    // 🎥 YOUTUBE INPUT
    else if (type === "youtube") {
      const ytLink = youtubeInput.value.trim();

      if (!ytLink) {
        resultBox.innerHTML = "⚠️ Please paste YouTube link!";
        return;
      }

      response = await fetch("/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          type: "youtube",
          mode: mode,
          content: ytLink
        })
      });
    }

    // 📁 FILE INPUT (PDF/DOCX)
    else if (type === "pdf") {
      if (!fileInput.files.length) {
        resultBox.innerHTML = "⚠️ Please upload a file!";
        return;
      }

      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("mode", mode);

      response = await fetch("/process", {
        method: "POST",
        body: formData
      });
    }

    // 🔍 HANDLE RESPONSE
    const result = await response.json();

    if (!result.output) {
      resultBox.innerHTML = "❌ No response from server!";
      return;
    }

    // ✨ CLEAN OUTPUT DISPLAY
    resultBox.innerHTML = `
      <div style="white-space: pre-wrap; line-height: 1.6;">
        ${result.output}
      </div>
    `;

    // 📥 DOWNLOAD BUTTONS
    if (result.pdf && result.docx) {
      resultBox.innerHTML += `
        <br><br>
        <b>Download:</b><br>
        <a href="${result.pdf}" target="_blank">📄 Download PDF</a><br>
        <a href="${result.docx}" target="_blank">📝 Download DOCX</a>
      `;
    }

  } catch (error) {
    console.error(error);
    resultBox.innerHTML = "❌ Error connecting to backend!";
  }
}