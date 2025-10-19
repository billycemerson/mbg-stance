from googleapiclient.discovery import build
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)


# Get Video Details
def get_video_details(video_id):
    """Retrieve detailed statistics (views, likes, comments) for a specific video."""
    try:
        request = YOUTUBE.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()

        if response.get("items"):
            stats = response["items"][0]["statistics"]
            return {
                "viewCount": int(stats.get("viewCount", 0)),
                "likeCount": int(stats.get("likeCount", 0)),
                "commentCount": int(stats.get("commentCount", 0))
            }
        return {}
    except Exception as e:
        print(f"Error getting details for video {video_id}: {e}")
        return {}


# Get Replies to Comments
def get_replies(video_id, parent_id):
    """Retrieve replies to a specific top-level comment."""
    replies = []
    next_page = None

    try:
        while True:
            request = YOUTUBE.comments().list(
                part="snippet",
                parentId=parent_id,
                maxResults=100,
                pageToken=next_page,
                textFormat="plainText"
            )
            response = request.execute()

            for reply in response.get("items", []):
                reply_snippet = reply["snippet"]
                replies.append({
                    "video_id": video_id,
                    "comment_id": reply["id"],
                    "author": reply_snippet.get("authorDisplayName"),
                    "comment": reply_snippet.get("textDisplay"),
                    "like_count": reply_snippet.get("likeCount"),
                    "published_at": reply_snippet.get("publishedAt"),
                    "is_reply": True,
                    "parent_id": parent_id
                })

            next_page = response.get("nextPageToken")
            if not next_page:
                break

            time.sleep(0.5)

    except Exception as e:
        print(f"Error getting replies for comment {parent_id}: {e}")

    return replies


# Get All Comments (Top + Replies)
def get_comments(video_id):
    """Retrieve all comments (top-level + replies) for a given video."""
    comments = []
    next_page = None

    try:
        while True:
            request = YOUTUBE.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page,
                textFormat="plainText"
            )
            response = request.execute()

            for item in response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "video_id": video_id,
                    "comment_id": item["snippet"]["topLevelComment"]["id"],
                    "author": top_comment.get("authorDisplayName"),
                    "comment": top_comment.get("textDisplay"),
                    "like_count": top_comment.get("likeCount"),
                    "published_at": top_comment.get("publishedAt"),
                    "is_reply": False,
                    "parent_id": None
                })

                # Get replies if exist
                if item["snippet"].get("totalReplyCount", 0) > 0:
                    replies = get_replies(video_id, item["id"])
                    comments.extend(replies)

            next_page = response.get("nextPageToken")
            if not next_page:
                break

            time.sleep(1)  # avoid quota issues

    except Exception as e:
        print(f"Error getting comments for video {video_id}: {e}")

    return comments


# Search Videos (with pagination)
def search_videos(keyword, max_results=500):
    """Search for videos on YouTube based on a keyword with pagination."""
    videos = []
    next_page_token = None

    while len(videos) < max_results:
        try:
            request = YOUTUBE.search().list(
                q=keyword,
                part="snippet",
                type="video",
                maxResults=min(50, max_results - len(videos)),  # limit per request
                pageToken=next_page_token,
                relevanceLanguage="id"
            )
            response = request.execute()

            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                video_details = get_video_details(video_id)

                videos.append({
                    "video_id": video_id,
                    "comment_id": None,
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "channel": item["snippet"]["channelTitle"],
                    "view_count": video_details.get("viewCount", 0),
                    "like_count": video_details.get("likeCount", 0),
                    "comment_count": video_details.get("commentCount", 0)
                })

                if len(videos) >= max_results:
                    break

                time.sleep(0.1)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            print(f"Retrieved {len(videos)} videos so far...")
            time.sleep(1)

        except Exception as e:
            print(f"Error during video search: {e}")
            break

    return videos[:max_results]


# ollect Everything
def collect_youtube_data(keyword, max_videos=500):
    """Main function to collect video metadata and all comments (top + replies)."""
    print(f"Searching for up to {max_videos} videos about '{keyword}'...")
    videos = search_videos(keyword, max_videos)
    print(f"Found {len(videos)} videos")

    video_df = pd.DataFrame(videos)

    print("\nCollecting comments...")
    all_comments = []
    for i, vid in enumerate(videos):
        print(f"Getting comments from video {i+1}/{len(videos)}: {vid['title']}")
        comments = get_comments(vid["video_id"])
        print(f"Found {len(comments)} comments (including replies)")
        all_comments.extend(comments)
        time.sleep(1)

    comments_df = pd.DataFrame(all_comments)
    return video_df, comments_df


# Example Usage
if __name__ == "__main__":
    video_df, comments_df = collect_youtube_data("Makan Bergizi Gratis", max_videos=100)

    os.makedirs("../data", exist_ok=True)
    video_df.to_csv("../data/yt_mbg_videos.csv", index=False)
    print(f"\nVideo data saved: ({len(video_df)} videos)")
    comments_df.to_csv("../data/yt_mbg_comments.csv", index=False)
    print(f"Comments data saved: ({len(comments_df)} comments)")