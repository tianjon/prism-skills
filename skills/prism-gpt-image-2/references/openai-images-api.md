# OpenAI-Compatible Images API — Reference

This skill targets two endpoints under the resolved base URL. Both Anspire (`https://open-gateway.anspire.ai/v6`) and OpenAI (`https://api.openai.com/v1`) expose the same shape.

## Authentication

```
Authorization: Bearer <api_key>
Accept: */*
```

## POST /images/generations  (JSON body)

Minimum payload:

```json
{
  "model": "gpt-image-2",
  "prompt": "A cute baby sea otter",
  "n": 1,
  "size": "1024x1024"
}
```

Optional fields the CLI forwards when the user passes the matching flag:

| Field             | CLI flag             | Notes |
|-------------------|----------------------|-------|
| `quality`         | `--quality`          | `low` / `medium` / `high` / `auto` |
| `background`      | `--background`       | `opaque` / `transparent` / `auto` |
| `response_format` | `--response-format`  | `b64_json` / `url`. Servers may ignore this for gpt-image-1/2. |

Response shape:

```json
{
  "created": 1700000000,
  "data": [
    { "b64_json": "<base64-png>" }
  ]
}
```

The CLI accepts both `b64_json` and `url` entries. When both are missing, it raises an error with the offending entry inline.

## POST /images/edits  (multipart/form-data body)

Form fields:

- `model` (required)
- `prompt` (required)
- `n` (required, integer-as-string)
- `size` (optional)
- `quality` (optional)
- `image` — one input image. For multiple images, repeat `image[]`.
- `mask` — optional PNG; transparent pixels mark regions to edit.

The CLI sends `image` for a single image and `image[]` for multiple, matching what current OpenAI-compatible providers accept.

## Curl baseline (Anspire example)

```bash
curl --location --request POST "$ANS_BASE_URL/images/generations" \
  --header "Authorization: Bearer $ANS_API_KEY" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "model": "gpt-image-2",
    "prompt": "A cute baby sea otter",
    "n": 1,
    "size": "1024x1024"
  }'
```

When `ANS_BASE_URL=https://open-gateway.anspire.ai/v6`, the CLI hits `https://open-gateway.anspire.ai/v6/images/generations` with the same headers and body shape.
