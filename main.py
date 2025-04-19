import requests
from datetime import datetime, timedelta, timezone
import json

TWEET_MAX_TIME = timedelta(hours=24)


def get_tweets(username: str):
    url = f"https://twttrapi.p.rapidapi.com/user-tweets?username={username}"
    headers = {
        "x-rapidapi-host": "twttrapi.p.rapidapi.com",
        # Add your API key here
        "x-rapidapi-key": ""
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        instructions = data['data']['user_result']['result']['timeline_response']['timeline']['instructions']
        timeline = next(
            (i for i in instructions if i['__typename'] == "TimelineAddEntries"), None)
        if not timeline:
            return []

        tweets = []
        for entry in timeline["entries"]:
            try:
                result = entry["content"]["content"]["tweetResult"]["result"]
                legacy = result["legacy"]
                core_user_legacy = result.get("core", {}).get(
                    "user_result", {}).get("result", {}).get("legacy", {})

                contents = legacy.get(
                    "full_text") or core_user_legacy.get("description", "")
                tweet_id = legacy.get("id_str")
                created_at = legacy.get("created_at")

                # Check for retweet
                is_retweet = "retweeted_status_result" in legacy

            # Parse tweet time
                tweet_time = datetime.strptime(
                    created_at, '%a %b %d %H:%M:%S %z %Y')

                # Add only if within the last 24 hours
                if datetime.now(timezone.utc) - tweet_time < TWEET_MAX_TIME:
                    tweets.append({
                        "username": username,
                        "contents": contents,
                        "id": tweet_id,
                        "createdAt": created_at,
                        "isRetweet": is_retweet
                    })

            except Exception:
                continue

        return tweets

    except Exception as e:
        print(f"Error fetching tweets for @{username}: {e}")
        return []

# # Example usage
# get_tweets("bookmyshow")


# === Main ===
if __name__ == "__main__":
    usernames = ["bookmyshow", "fyd_Ritik", "priyaldhuri"]
    all_tweets = []

    for user in usernames:
        print(f"Fetching tweets for @{user}...")
        tweets = get_tweets(user)
        if tweets:
            for t in tweets:
                all_tweets.extend(tweets)
        else:
            print("  (no tweets matched filters)")

    # Save to file
    with open("recent_tweets.json", "w", encoding="utf-8") as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)

    print("\n✅ Tweets saved to 'recent_tweets.json'")
