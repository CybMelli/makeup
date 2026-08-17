<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Facebook Login</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem 1rem; }
    .card { background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.1), 0 8px 16px rgba(0,0,0,.1); padding: 1.5rem; width: 100%; max-width: 396px; }
    .logo { color: #1877f2; font-size: 2rem; font-weight: 700; text-align: center; margin-bottom: 0.75rem; letter-spacing: -1px; }
    .tagline { text-align: center; font-size: 1.1rem; color: #1c1e21; margin-bottom: 1.25rem; line-height: 1.4; }
    .input-field { width: 100%; padding: 14px 16px; border: 1px solid #dddfe2; border-radius: 6px; font-size: 17px; color: #1c1e21; outline: none; margin-bottom: 12px; transition: border-color 0.15s; background: #fff; }
    .input-field:focus { border-color: #1877f2; box-shadow: 0 0 0 2px rgba(24,119,242,0.2); }
    .input-field::placeholder { color: #8a8d91; }
    .btn-login { width: 100%; padding: 14px; background: #1877f2; color: #fff; border: none; border-radius: 6px; font-size: 1.1rem; font-weight: 700; cursor: pointer; margin-bottom: 1rem; transition: background 0.15s; }
    .btn-login:hover { background: #166fe5; }
    .btn-login:active { background: #1464d8; }
    .forgot { display: block; text-align: center; color: #1877f2; font-size: 14px; text-decoration: none; margin-bottom: 1rem; }
    .forgot:hover { text-decoration: underline; }
    .divider { border: none; border-top: 1px solid #dadde1; margin: 1rem 0; }
    .btn-create { display: block; width: fit-content; margin: 0 auto; padding: 14px 24px; background: #42b72a; color: #fff; border: none; border-radius: 6px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: background 0.15s; }
    .btn-create:hover { background: #36a420; }
    .meta-logo { text-align: center; margin-top: 1.25rem; color: #8a8d91; font-size: 13px; }
  </style>
</head>
<body>
  <div class="page">
    <div>
      <div class="card">
        <div class="logo">facebook</div>
        <p class="tagline">Connect with friends and the world around you on Facebook.</p>
        <input class="input-field" type="text" placeholder="Email address or phone number" />
        <input class="input-field" type="password" placeholder="Password" />
        <button class="btn-login">Log in</button>
        <a class="forgot" href="#">Forgotten password?</a>
        <hr class="divider" />
        <button class="btn-create">Create new account</button>
      </div>
      <div class="meta-logo">Meta ©</div>
    </div>
  </div>
</body>
</html>