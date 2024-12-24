// globalScript.js

// Global logout function
function logout() {
  localStorage.clear(); // Clear all data from localStorage
  window.location.href = "logins/signin.html"; // Redirect to Sign In page
}

// Attach logout to a logout button (if needed)
document.getElementById("logout-btn")?.addEventListener("click", logout);
