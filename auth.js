/* Demo gate for AI Ascent (static site). Not for real security. */
(function (global) {
  var KEY = "ai-ascent-session";

  var USERS = [
    { username: "admin", password: "Admin@123", name: "Admin User" },
    { username: "learner01", password: "Learn@101", name: "Learner One" },
    { username: "learner02", password: "Learn@102", name: "Learner Two" },
    { username: "learner03", password: "Learn@103", name: "Learner Three" },
    { username: "trainer", password: "Train@2026", name: "Trainer Desk" },
    { username: "guest", password: "Guest@2026", name: "Guest Access" },
    { username: "opslead", password: "Ops@2026", name: "Ops Lead" },
    { username: "analyst", password: "Data@2026", name: "Analyst" },
    { username: "hrdesk", password: "HR@2026", name: "HR Desk" },
    { username: "demo", password: "Demo@2026", name: "Demo Account" }
  ];

  function getSession() {
    try {
      var raw = sessionStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setSession(user) {
    sessionStorage.setItem(
      KEY,
      JSON.stringify({
        username: user.username,
        name: user.name,
        at: Date.now()
      })
    );
  }

  function clearSession() {
    sessionStorage.removeItem(KEY);
  }

  function login(username, password) {
    var u = String(username || "").trim();
    var p = String(password || "");
    for (var i = 0; i < USERS.length; i++) {
      if (USERS[i].username === u && USERS[i].password === p) {
        setSession(USERS[i]);
        return { ok: true, user: USERS[i] };
      }
    }
    return { ok: false, error: "Invalid username or password." };
  }

  function logout() {
    clearSession();
    location.href = "login.html";
  }

  function currentPage() {
    var parts = location.pathname.split("/");
    return parts[parts.length - 1] || "index.html";
  }

  function requireAuth() {
    if (getSession()) return true;
    var next = currentPage();
    if (next === "login.html") next = "index.html";
    location.replace("login.html?next=" + encodeURIComponent(next));
    return false;
  }

  function requireGuest() {
    if (!getSession()) return true;
    var params = new URLSearchParams(location.search);
    var next = params.get("next") || "index.html";
    if (!/^[A-Za-z0-9._-]+\.html$/.test(next)) next = "index.html";
    location.replace(next);
    return false;
  }

  function fillUserChrome() {
    var session = getSession();
    if (!session) return;
    document.querySelectorAll("[data-auth-name]").forEach(function (el) {
      el.textContent = session.name || session.username;
    });
    document.querySelectorAll("[data-auth-user]").forEach(function (el) {
      el.textContent = session.username;
    });
  }

  global.AscentAuth = {
    USERS: USERS,
    login: login,
    logout: logout,
    getSession: getSession,
    requireAuth: requireAuth,
    requireGuest: requireGuest,
    fillUserChrome: fillUserChrome
  };
})(window);
