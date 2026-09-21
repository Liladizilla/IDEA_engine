# Security

Done
- Secrets only in backend env. The Flutter app knows a base URL and nothing else.
- Passwords: argon2id. Tokens: JWT with `typ` claim (access 15 min, refresh 30 days with `jti` for revocation). A refresh token cannot be used as an access token.
- `get_settings` refuses to start in production without a 32+ character `JWT_SECRET`.
- Input validation via pydantic. Scores are bounded 0 to 100.

To do before launch
- Auth routes, refresh rotation and revocation table.
- Rate limiting (slowapi or a gateway), tighter CORS, audit log table.
- Encrypt stored third-party credentials if users connect accounts.
- Authorization checks on every user-scoped route.
- Store the Android release keystore and `key.properties` outside git (already in `.gitignore`).
