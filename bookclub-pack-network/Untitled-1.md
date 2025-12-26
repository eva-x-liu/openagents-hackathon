curl https://inference.do-ai.run/v1/chat/completions \
  -H "Authorization: Bearer $READYMOJO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic-claude-4.5-sonnet",
    "messages": [{"role":"user","content":"ping"}],
    "max_tokens": 20
  }'