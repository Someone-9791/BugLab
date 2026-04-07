# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, **please do not open a public issue**. Instead:

1. **Email**: Contact the maintainers privately at [security contact]
2. **Provide**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

3. **Timeline**: We aim to respond within 48 hours and provide fixes within 7 days

## Supported Versions

| Version | Status | Security Updates |
|---------|--------|------------------|
| 0.1.0+ | Active | Yes |

## Security Considerations

### Known Issues
- Uses `exec()` for code execution in sandboxed namespace (acceptable for hackathon environment)
- No multi-user isolation (single-user assumption)
- API has no authentication (development/hackathon use only)

### Best Practices for Users

1. **Never expose this to untrusted networks** without authentication
2. **Sandbox execution** is isolated but not cryptographically secure
3. **Use in controlled environments** only
4. **Environment variables** (API_KEY, HF_TOKEN) should be secured
5. **Docker deployment** is recommended for isolation

## Security Scanning

We recommend:
- Running `ruff` for Python code quality
- Using `pip audit` to check dependencies
- Regular dependency updates

## Dependencies

All dependencies are from reputable sources:
- `fastapi`: HTTP framework
- `pydantic`: Data validation
- `openai`: LLM API client
- `openenv-core`: OpenEnv specification

## License

This security policy is available under the same license as the project.
