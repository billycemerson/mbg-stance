from googleapiclient.discovery import build
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)

def search_videos(keyword, max_results=20):
    """Search for videos on YouTube based on a keyword."""
    request = YOUTUBE.search().list(
        q=keyword,
        part="snippet",
        type="video",
        maxResults=max_results,
        relevanceLanguage="id"
    )
    response = request.execute()
    
    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        
        # Retrieve detailed video statistics
        video_details = get_video_details(video_id)
        
        videos.append({
            "video_id": video_id,
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "channel": item["snippet"]["channelTitle"],
            "view_count": video_details.get("viewCount", 0),
            "like_count": video_details.get("likeCount", 0),
            "comment_count": video_details.get("commentCount", 0)
        })
        
        time.sleep(0.1)  # Avoid hitting rate limit
    
    return videos


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
                # Get top-level comment
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "video_id": video_id,
                    "author": top_comment.get("authorDisplayName"),
                    "comment": top_comment.get("textDisplay"),
                    "like_count": top_comment.get("likeCount"),
                    "published_at": top_comment.get("publishedAt"),
                    "is_reply": False,
                    "parent_id": None
                })
                
                # Check for replies
                if item["snippet"].get("totalReplyCount", 0) > 0:
                    replies = get_replies(video_id, item["id"])
                    comments.extend(replies)
            
            next_page = response.get("nextPageToken")
            if not next_page:
                break
                
            time.sleep(1)  # Avoid quota issues
            
    except Exception as e:
        print(f"Error getting comments for video {video_id}: {e}")
    
    return comments


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


def collect_youtube_data(keyword, max_videos=10):
    """Main function to collect video metadata and all comments (top + replies)."""
    print("Searching for videos...")
    videos = search_videos(keyword, max_videos)
    
    video_df = pd.DataFrame(videos)
    
    print("\nCollecting comments...")
    all_comments = []
    for i, vid in enumerate(videos):
        print(f"Getting comments from video {i+1}/{len(videos)}: {vid['title']}")
        comments = get_comments(vid["video_id"])
        print(f"Found {len(comments)} total comments (including replies)")
        all_comments.extend(comments)
        time.sleep(1)
    
    comments_df = pd.DataFrame(all_comments)
    
    return video_df, comments_df


# Example usage
if __name__ == "__main__":
    video_df, comments_df = collect_youtube_data("Makan Bergizi Gratis", max_videos=100)

    # Save results
    video_df.to_csv("yt_mbg_videos.csv", index=False)
    print(f"\nVideo data saved: ({len(video_df)} videos)")
    comments_df.to_csv("yt_mbg_comments.csv", index=False)
    print(f"Comments data saved: ({len(comments_df)} comments)")