$(document).ready(function() {
    document.getElementById('googleSignIn').addEventListener('click', function() { alert("Google Sign-In clicked!"); });
    document.getElementById('facebookSignIn').addEventListener('click', function() { alert("Facebook Sign-In clicked!"); });
    document.getElementById('githubSignIn').addEventListener('click', function() { window.location.href ='/login_with_git_hub' });
});
