# Fantasy Baseball Pitcher Streamer

Simple Streamlit app for finding likely starting pitchers over the next 7 days and ranking them as streaming options using live MLB probable starters. Yahoo league free-agent filtering works in local development with a `yahoo_oauth` JSON file and in deployment with Streamlit secrets or environment variables.

## Project Structure

```text
fantasy-baseball-app/
|-- app.py
|-- clients/
|   |-- __init__.py
|   |-- mlb.py
|   `-- yahoo.py
|-- requirements.txt
|-- README.md
|-- data/
|   |-- __init__.py
|   `-- reference.py
`-- services/
    |-- __init__.py
    |-- probable_starters.py
    `-- scoring.py
```

## Run Locally

1. Open PowerShell in this folder:

   ```powershell
   cd C:\Users\donse\OneDrive\Desktop\fantasy-baseball-app
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

3. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Start Streamlit:

   ```powershell
   streamlit run app.py
   ```

6. Open the local URL shown in the terminal, usually:

   [http://localhost:8501](http://localhost:8501)

## Yahoo Setup

Yahoo filtering is optional.

### Local Development

If you want the app to show only free-agent starters in your league while developing locally:

1. Create a Yahoo developer app:

   [Yahoo Fantasy Sports API docs](https://developer.yahoo.com/fantasysports/guide/?source=post_page---------------------------)

2. Follow the Yahoo OAuth 2.0 guide:

   [Yahoo OAuth 2.0 guide](https://developer.yahoo.com/oauth2/guide/)

3. Create an OAuth JSON file for `yahoo_oauth` and place it at:

   ```text
   secrets/yahoo_oauth.json
   ```

4. Launch the app and enter:

   - your Yahoo league key, for example `456.l.12345`
   - your local OAuth file path, for example `secrets/yahoo_oauth.json`

5. Check `Filter to Yahoo free agents` in the sidebar.

### Streamlit Community Cloud Deployment

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app that points to this repo and `app.py`.
3. In the app settings, open `Secrets` and add the Yahoo values.
4. Deploy the app.
5. In Yahoo Developer, set your app's redirect URI to the exact deployed HTTPS URL you plan to use.

Recommended deployment order:

1. Push the app to GitHub.
2. Create the app in Streamlit Community Cloud and choose a final app URL.
3. Set `YAHOO_CALLBACK_URI` to that final HTTPS app URL.
4. Update the Yahoo developer app to use the same redirect URI.
5. Re-run Yahoo OAuth so you have a refresh token created for that production redirect URI.
6. Paste the production secrets into Streamlit Community Cloud.
7. Redeploy or reboot the app.

Example `secrets.toml`:

```toml
[yahoo]
consumer_key = "your-yahoo-consumer-key"
consumer_secret = "your-yahoo-consumer-secret"
refresh_token = "your-yahoo-refresh-token"
callback_uri = "https://your-app-name.streamlit.app/"

# Optional convenience default for the sidebar.
league_key = "456.l.12345"

# Optional. If omitted, the app will refresh from refresh_token.
access_token = "optional-current-access-token"
token_type = "bearer"
token_time = 0
```

The app also supports environment variables instead of Streamlit secrets.

### Exactly Which Secrets You Need When Deployed

Required:

- `YAHOO_CONSUMER_KEY`
- `YAHOO_CONSUMER_SECRET`
- `YAHOO_REFRESH_TOKEN`
- `YAHOO_CALLBACK_URI`

Optional:

- `YAHOO_LEAGUE_KEY`
- `YAHOO_ACCESS_TOKEN`
- `YAHOO_TOKEN_TYPE`
- `YAHOO_TOKEN_TIME`

If you use nested Streamlit secrets, these map to:

- `yahoo.consumer_key`
- `yahoo.consumer_secret`
- `yahoo.refresh_token`
- `yahoo.callback_uri`
- `yahoo.league_key`
- `yahoo.access_token`
- `yahoo.token_type`
- `yahoo.token_time`

### Redirect URI Notes

- Local development can keep using the local JSON file you already have.
- Deployment should use an HTTPS redirect URI such as `https://your-app-name.streamlit.app/`.
- The app reads the redirect URI from `YAHOO_CALLBACK_URI`, so you can switch from a local/testing callback to a production HTTPS callback without code changes.
- If your existing refresh token was created for a different redirect URI, create a fresh Yahoo refresh token after you switch to the production HTTPS callback.

## Release Checklist

### 1. Push To GitHub

1. Create a new empty repository on GitHub.
2. In PowerShell, open this project folder:

   ```powershell
   cd C:\Users\donse\OneDrive\Desktop\fantasy-baseball-app
   ```

3. Initialize git if needed:

   ```powershell
   git init
   ```

4. Rename the default branch to `main`:

   ```powershell
   git branch -M main
   ```

5. Add all files except ignored local secrets and the virtual environment:

   ```powershell
   git add .
   ```

6. Create the first commit:

   ```powershell
   git commit -m "Prepare Streamlit app for cloud deployment"
   ```

7. Connect the GitHub repo:

   ```powershell
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
   ```

8. Push:

   ```powershell
   git push -u origin main
   ```

### 2. Deploy On Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Sign in and connect the same GitHub account that owns the repo.
3. Click `Create app`.
4. Choose `Yup, I have an app`.
5. Select:

   - Repository: your GitHub repo
   - Branch: `main`
   - File path: `app.py`

6. Optional but recommended: set a custom app URL so the final public address is easy to remember from your phone.
7. Open `Advanced settings`.
8. Set Python to `3.12` unless you have a reason to choose another supported version.
9. Paste your secrets into the `Secrets` box.
10. Click `Deploy`.

### 3. Add The Required Secrets

Use one of these formats in Streamlit Community Cloud.

Nested `secrets.toml` format:

```toml
[yahoo]
consumer_key = "your-yahoo-consumer-key"
consumer_secret = "your-yahoo-consumer-secret"
refresh_token = "your-yahoo-refresh-token"
callback_uri = "https://your-app-name.streamlit.app/"
league_key = "456.l.12345"
```

Flat format:

```toml
YAHOO_CONSUMER_KEY = "your-yahoo-consumer-key"
YAHOO_CONSUMER_SECRET = "your-yahoo-consumer-secret"
YAHOO_REFRESH_TOKEN = "your-yahoo-refresh-token"
YAHOO_CALLBACK_URI = "https://your-app-name.streamlit.app/"
YAHOO_LEAGUE_KEY = "456.l.12345"
```

Minimum required values:

- `YAHOO_CONSUMER_KEY`
- `YAHOO_CONSUMER_SECRET`
- `YAHOO_REFRESH_TOKEN`
- `YAHOO_CALLBACK_URI`

Strongly recommended:

- `YAHOO_LEAGUE_KEY`

Optional:

- `YAHOO_ACCESS_TOKEN`
- `YAHOO_TOKEN_TYPE`
- `YAHOO_TOKEN_TIME`

### 4. Set The Correct `YAHOO_CALLBACK_URI`

1. Decide your final Streamlit app URL first.
2. Use that exact HTTPS URL as `YAHOO_CALLBACK_URI`.
3. Use the same exact URL in your Yahoo developer app redirect URI setting.
4. Keep the value consistent everywhere:

   - Streamlit Community Cloud secrets
   - Yahoo developer app settings
   - any production OAuth re-auth you perform

Example:

```text
https://your-app-name.streamlit.app/
```

### 5. Complete Yahoo Auth For Production

The deployed app needs a valid Yahoo refresh token that matches your production redirect URI.

If you already have a local `secrets/yahoo_oauth.json`:

1. Open it and copy out:

   - `consumer_key`
   - `consumer_secret`
   - `refresh_token`
   - optionally `access_token`, `token_type`, and `token_time`

2. If that file was created using a different callback flow, update your Yahoo app redirect URI first and then create a fresh production token.

Recommended clean production flow:

1. In Yahoo Developer, set the redirect URI to your deployed Streamlit HTTPS URL.
2. Create a fresh OAuth JSON file locally using that same callback configuration.
3. Complete the Yahoo consent flow once.
4. Copy the resulting `consumer_key`, `consumer_secret`, `refresh_token`, and optionally the other token fields into Streamlit secrets.
5. Restart or redeploy the Streamlit app.

Result:

- Your code stays in GitHub.
- Your secrets stay out of GitHub.
- The deployed app works from your phone at the Streamlit URL.

## Notes

- MLB probable starters come from the public MLB Stats API schedule endpoint.
- Opponent strength and ballpark factors are simple local heuristics for now.
- Yahoo free-agent filtering uses `yahoo_oauth` and `yahoo_fantasy_api`.
- For deployment, no local OAuth file path is required.
