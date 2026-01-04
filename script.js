// ===============================
// SCREENING FORM LOGIC
// ===============================

// Make sure the form exists before attaching listener
const screeningForm = document.getElementById("screeningForm");

if (screeningForm) {
  screeningForm.addEventListener("submit", (e) => {
    e.preventDefault();

    // -------------------------------
    // Progress Text Logic (UNCHANGED)
    // -------------------------------
    const questions = document.querySelectorAll(".question");
    const progressText = document.getElementById("progressText");

    questions.forEach((q, index) => {
      const select = q.querySelector("select");
      if (select) {
        select.addEventListener("change", () => {
          progressText.innerText = `Question ${index + 1} of 6`;
        });
      }
    });

    // -------------------------------
    // Collect Screening Data
    // -------------------------------
    const payload = {
      q1: Number(document.getElementById("q1").value),
      q2: Number(document.getElementById("q2").value),
      q3: Number(document.getElementById("q3").value),
      q4: Number(document.getElementById("q4").value),
      q5: Number(document.getElementById("q5").value),
      q6: Number(document.getElementById("q6").value),
    };

    // -------------------------------
    // Store data for loading page
    // -------------------------------
    localStorage.setItem(
      "screeningData",
      JSON.stringify(payload)
    );

    // -------------------------------
    // Redirect immediately (NO WAIT)
    // -------------------------------
    window.location.href = "loading.html";
  });
}

