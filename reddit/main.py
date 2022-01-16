# -*- coding: utf-8 -*-

import praw
import json

config = json.load(open(r".\config.json", 'r'))

reddit = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent="my user agent",
)

with open(r".\post_template.html", 'r') as fpost:
    POST_TEMPLATE = fpost.read()
    fpost.close()
    
with open(r".\reddit_template.html", 'r') as freddit:
    REDDIT_TEMPLATE = freddit.read()
    freddit.close()
    
    
def gen_post(template_vars):
    reddit_post = POST_TEMPLATE
    
    for key in template_vars:
        reddit_post = reddit_post.replace(key, str(template_vars[key]))
        
    return reddit_post


def gen_page(posts):
    page_template = REDDIT_TEMPLATE
    page_template = page_template.replace("{{POSTS}}", "\n".join(posts))
    return page_template



def _get_subreddit_content(subreddit="all", limit=30):
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        sub = submission.__dict__
        
        post_template_vars = {
            "{{POINTS}}": sub["ups"]  - sub["downs"],
            "{{TITLE}}": sub["title"],
            "{{IMAGE_URL}}": None if sub["is_self"] else sub["url"],
            "{{SUB_URL}}": sub["subreddit_name_prefixed"],
            "{{AUTHOR}}": sub["author"].name,
            "{{POST_URL}}": sub["url"],
            "{{THUMBNAIL_URL}}": sub["thumbnail"],
            "{{VIDEO_URL}}": sub["secure_media"].get("reddit_video", {}).get("fallback_url") if sub["secure_media"] is not None else None
        }
        
        reddit_post = gen_post(post_template_vars)
        
        posts.append(reddit_post)
        
    
    html_page = gen_page(posts)
    
    return html_page


def _get_post_content(comments_id):
    return "<html><body>Coucou it works!</body></html>"
    
    
    
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import logging
logger = logging.getLogger()


@app.get("/r/{subreddit}/comments/{comments_id}", response_class=HTMLResponse)
async def get_comments(subreddit: str = "all", comments_id: str = None):
    return _get_post_content(comments_id)



@app.get("/r/{subreddit}", response_class=HTMLResponse)
async def get_subreddit_content(subreddit: str = "all"):
    return _get_subreddit_content(subreddit)


@app.get("/", response_class=HTMLResponse)
async def get_all_content():
    return _get_subreddit_content()

    
import uvicorn

if __name__ == '__main__':
    uvicorn.run("main:app",
                host="localhost",
                port=8001,
                reload=True
                )
    