Zeabur Deploy (Dockerfile)
1. Push this repo to GitHub
2. In Zeabur: New Project -> Deploy from Git -> Use Dockerfile
3. Set Environment Variables in Zeabur:
  - (Zeabur provides) PORT
  - Your model keys (example placeholders):
    - OPENAI_API_KEY or GOOGLE_API_KEY etc.
4. Deploy
Open Studio:
- http://localhost:8700/studio (or PORT=xxxx)
Stop:
```
bash scripts/dev_down.sh
```
Zeabur Deploy (Dockerfile)
1. Push this repo to GitHub
2. In Zeabur: New Project -> Deploy from Git -> Use Dockerfile
3. Set Environment Variables in Zeabur:
  - (Zeabur provides) PORT
  - Your model keys (example placeholders):
    - OPENAI_API_KEY or GOOGLE_API_KEY etc.
4. Deploy
Open Studio:
- https://<your-zeabur-domain>/studio
Security
- Never commit real secrets.
- Use .env.example for keys placeholders.
- Put real keys in:
  - Local .env (ignored by git)
  - Zeabur Environment Variables
Pack Schema
- schemas/bookclub_pack_v1.schema.json
Note: JSON Schema allows daily arrays 1..21; Publisher enforces strict length == cycle_days at runtime.
Demo
Use docs/demo_input_case.md to run a consistent demo for regression & video recording.

---

## 8) 一键启动命令总结

### 本地一键启动
```bash
bash scripts/dev_up.sh
本地一键停止
bash scripts/dev_down.sh
Zeabur
- 直接部署 Dockerfile（启动由 CMD 自动完成），不需要你再点命令


