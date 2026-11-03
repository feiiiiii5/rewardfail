# Sanitization note

- 58 text files were sanitized during the copy: 743 replacements of local paths and token/email/phone-like strings.
- Placeholders: WORKSPACE, REWARDfail_LOCAL, LOCAL_USER, REDACTED_TOKEN, EMAIL, PHONE.
- The two raw rows.jsonl files were copied byte-for-byte; they contain no /Users/ path and no token-like string.
- Numeric scores, labels, timestamps and row ids were not changed.
- Original local records were not modified.
- Hash caveat: manifest-all.json and some verification fields may refer to pre-sanitization originals. The P1 summary was regenerated after sanitization. Do not treat a path-only hash difference as a data change.
- No passwords, API tokens, private keys, .env files or full home directory are included.
- The repository is public. If raw responses or internal planning notes need to stay private, move this archive to a private repository or remove context/.
