//check if the user is signed in or not
if (!localStorage.getItem("loggedIn") && window.location.pathname !== '/signin.html') {
  window.location.href = "signin.html";
}