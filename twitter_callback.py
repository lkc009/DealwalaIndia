#!/usr/bin/env python3
import json, sys, urllib.parse, urllib.request, os

if len(sys.argv) < 2:
    print("Usage: python3 twitter_callback.py <redirect_url>")
    sys.exit(1)

redirect_url = sys.argv[1]

with open("/tmp/twitter_oauth_state.json") as f:
    info = json.load(f)

CLIENT_ID = "WkVsZ21Mc1BBbzE5RFRZeFU0VS06MTpjaQ"
CLIENT_SECRET = "5-e7rQVbmYcA_wzyPParfuhIJfd90Iri1D7asmJveI1OcIyeZI"
code_verifier = info["code_verifier"]

parsed = urllib.parse.urlparse(redirect_url)
qs = urllib.parse.parse_qs(parsed.query)
auth_code = qs.get("code", [None])[0]

if not auth_code:
    print("No authorization code found in URL")
    sys.exit(1)

token_data = urllib.parse.urlencode({
    "code": auth_code,
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "http://127.0.0.1:8956/callback",
    "code_verifier": code_verifier,
}).encode()

req = urllib.request.Request(
    "https://api.twitter.com/2/oauth2/token",
    data=token_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
with urllib.request.urlopen(req) as resp:
    tokens = json.loads(resp.read())

print(f"Access: {tokens['access_token'][:30]}...")
print(f"Refresh: {tokens['refresh_token'][:30]}...")
print(f"Scope: {tokens['scope']}")

if "tweet.write" not in tokens["scope"]:
    print("ERROR: tweet.write scope missing! Re-authorize.")
    sys.exit(1)

creds_path = os.path.expanduser("~/.codex/twitter_dealwala.json")
with open(creds_path) as f:
    creds = json.load(f)
creds["oauth2_access_token"] = tokens["access_token"]
creds["oauth2_refresh_token"] = tokens["refresh_token"]
creds["oauth2_client_id"] = CLIENT_ID
creds["oauth2_client_secret"] = CLIENT_SECRET
creds["oauth2_scope"] = tokens["scope"]
with open(creds_path, "w") as f:
    json.dump(creds, f, indent=2)

print(f"Saved to {creds_path}")

# Test tweet
data = json.dumps({"text": "🔥 DealwalaIndia Twitter auto-poster is LIVE! Testing OAuth 2.0 🚀"}).encode()
req2 = urllib.request.Request(
    "https://api.twitter.com/2/tweets",
    data=data,
    headers={
        "Authorization": f"Bearer {tokens['access_token']}",
        "Content-Type": "application/json"
    }
)
with urllib.request.urlopen(req2) as resp2:
    result = json.loads(resp2.read())
    print(f"Test tweet posted! ID: {result['data']['id']}")

print("\nNow running post_deals.py will also post to Twitter!")
