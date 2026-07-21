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
    location.href = 'index.html';
  }

  function b64urlDecode(str) {
    var b64 = String(str || '').replace(/-/g, '+').replace(/_/g, '/');
    while (b64.length % 4) b64 += '=';
    return decodeURIComponent(escape(atob(b64)));
  }

  function softSign(message, secret) {
    var s = String(secret || '') + '|' + String(message || '');
    var h = 2166136261;
    for (var i = 0; i < s.length; i += 1) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(16);
  }

  function verifyHubToken(token, secret) {
    var parts = String(token || '').split('.');
    if (parts.length !== 2) return null;
    if (softSign(parts[0], secret) !== parts[1]) return null;
    try {
      var payload = JSON.parse(b64urlDecode(parts[0]));
      if (!payload || !payload.u || !payload.exp) return null;
      if (Number(payload.exp) <= Date.now()) return null;
      return { username: String(payload.u), role: String(payload.role || 'learner'), exp: Number(payload.exp) };
    } catch (err) {
      return null;
    }
  }

  function consumeHubTokenFromUrl() {
    // ponytail: soft cohort SSO from traininglobe-hub — secret lives in static config.js.
    var params = new URLSearchParams(location.search);
    var token = params.get('hub_token');
    if (!token) return false;
    var secret = (global.AscentConfig && global.AscentConfig.HUB_SSO_SECRET) || '';
    var payload = verifyHubToken(token, secret);
    if (!payload) return false;
    writeSession({
      username: payload.username,
      name: payload.username,
      role: payload.role === 'admin' ? 'learner' : payload.role,
      token: 'hub-' + payload.username,
      expires_at: new Date(payload.exp).toISOString()
    });
    params.delete('hub_token');
    var qs = params.toString();
    var clean = location.pathname + (qs ? '?' + qs : '') + location.hash;
    if (global.history && history.replaceState) history.replaceState(null, '', clean);
    return true;
  }

  function requireAuth(loginPage) {
    // ponytail: hub owns login — handbooks are open after cohort entry.
    consumeHubTokenFromUrl();
    return true;
  }

  function requireGuest() {
    // Login page retired: send everyone to the handbook.
    location.replace('index.html');
    return false;
  }

  function requireAdmin(loginPage) {
    // Admin UI still needs a local session; without one, bounce to index (open content).
    consumeHubTokenFromUrl();
    if (!isAdmin()) location.replace('index.html');
  }

  function fillUserChrome() {
    var name = currentName();
    var user = currentUser();
    document.querySelectorAll('.toc-user').forEach(function (el) {
      el.hidden = !user;
    });
    if (!user) return;
    document.querySelectorAll('[data-auth-name]').forEach(function (el) {
      el.textContent = name || user;
    });
    document.querySelectorAll('[data-auth-user]').forEach(function (el) {
      el.textContent = user;
    });
  }

  // Consume hub SSO as soon as auth.js loads (pages no longer gate via requireAuth).
  consumeHubTokenFromUrl();

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
