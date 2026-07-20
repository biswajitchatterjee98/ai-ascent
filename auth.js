(function (global) {
  var SESSION_KEY = 'ai-ascent-session';

  var LOCAL_USERS = [
    { username: 'admin', password: 'Admin@123', role: 'admin', name: 'Admin User' },
    { username: 'learner01', password: 'Learn@101', role: 'learner', name: 'Learner One' },
    { username: 'learner02', password: 'Learn@102', role: 'learner', name: 'Learner Two' },
    { username: 'learner03', password: 'Learn@103', role: 'learner', name: 'Learner Three' },
    { username: 'trainer', password: 'Train@2026', role: 'learner', name: 'Trainer Desk' },
    { username: 'guest', password: 'Guest@2026', role: 'learner', name: 'Guest Access' },
    { username: 'opslead', password: 'Ops@2026', role: 'learner', name: 'Ops Lead' },
    { username: 'analyst', password: 'Data@2026', role: 'learner', name: 'Analyst' },
    { username: 'hrdesk', password: 'HR@2026', role: 'learner', name: 'HR Desk' },
    { username: 'demo', password: 'Demo@2026', role: 'learner', name: 'Demo Account' }
  ];

  function readSession() {
    try {
      var raw = sessionStorage.getItem(SESSION_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (err) {
      return null;
    }
  }

  function writeSession(data) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(data));
  }

  function clearSession() {
    sessionStorage.removeItem(SESSION_KEY);
  }

  function currentUser() {
    var session = readSession();
    return session && session.username ? session.username : null;
  }

  function currentName() {
    var session = readSession();
    if (!session) return null;
    if (session.name) return session.name;
    return session.username || null;
  }

  function currentRole() {
    var session = readSession();
    if (session && session.role) return session.role;
    if (session && session.username === 'admin') return 'admin';
    return 'learner';
  }

  function currentToken() {
    var session = readSession();
    return session && session.token ? session.token : null;
  }

  function isLoggedIn() {
    return Boolean(currentToken() && currentUser());
  }

  function isAdmin() {
    return currentUser() === 'admin' && currentRole() === 'admin';
  }

  function loginLocalFallback(username, password) {
    // ponytail: offline/demo fallback when API_URL is not set yet.
    var u = String(username || '').trim();
    var p = String(password || '').trim();
    for (var i = 0; i < LOCAL_USERS.length; i += 1) {
      if (LOCAL_USERS[i].username === u && LOCAL_USERS[i].password === p) {
        writeSession({
          username: LOCAL_USERS[i].username,
          name: LOCAL_USERS[i].name,
          role: LOCAL_USERS[i].role,
          token: 'local-' + LOCAL_USERS[i].username,
          expires_at: new Date(Date.now() + 86400000).toISOString()
        });
        return Promise.resolve({
          ok: true,
          username: LOCAL_USERS[i].username,
          role: LOCAL_USERS[i].role
        });
      }
    }
    return Promise.resolve({ ok: false, error: 'Invalid username or password.' });
  }

  function login(username, password) {
    if (!global.AscentApi || !global.AscentApi.configured()) {
      return loginLocalFallback(username, password);
    }
    return global.AscentApi.login(username, password).then(function (result) {
      if (!result.ok) return result;
      var local = LOCAL_USERS.filter(function (u) { return u.username === result.username; })[0];
      writeSession({
        username: result.username,
        name: local ? local.name : result.username,
        role: result.role,
        token: result.token,
        expires_at: result.expires_at
      });
      return result;
    });
  }

  function logout() {
    clearSession();
    location.href = 'login.html';
  }

  function requireAuth(loginPage) {
    if (isLoggedIn()) return true;
    var next = location.pathname.split('/').pop() || 'index.html';
    if (location.search) next += location.search;
    if (location.hash) next += location.hash;
    location.replace((loginPage || 'login.html') + '?next=' + encodeURIComponent(next));
    return false;
  }

  function requireGuest() {
    if (!isLoggedIn()) return true;
    var params = new URLSearchParams(location.search);
    var next = params.get('next') || 'index.html';
    if (!/^[A-Za-z0-9._-]+\.html$/.test(next)) next = 'index.html';
    location.replace(next);
    return false;
  }

  function requireAdmin(loginPage) {
    requireAuth(loginPage);
    if (!isAdmin()) location.replace('index.html');
  }

  function fillUserChrome() {
    var name = currentName();
    var user = currentUser();
    if (!user) return;
    document.querySelectorAll('[data-auth-name]').forEach(function (el) {
      el.textContent = name || user;
    });
    document.querySelectorAll('[data-auth-user]').forEach(function (el) {
      el.textContent = user;
    });
  }

  global.AscentAuth = {
    USERS: LOCAL_USERS,
    login: login,
    logout: logout,
    getSession: readSession,
    isLoggedIn: isLoggedIn,
    isAdmin: isAdmin,
    currentUser: currentUser,
    currentRole: currentRole,
    currentToken: currentToken,
    requireAuth: requireAuth,
    requireGuest: requireGuest,
    requireAdmin: requireAdmin,
    fillUserChrome: fillUserChrome
  };
})(window);
