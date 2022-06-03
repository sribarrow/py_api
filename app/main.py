from curses.ascii import HT
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, requests, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# my_posts =[]

while True:
    try:
        conn = psycopg2.connect(host='localhost', 
                                database='fastapi', 
                                user='postgres', 
                                password='tru5tpgadm!N',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection to database successful.")
        break
    except Exception as e:
        print("Connection to database unsuccessful.")
        print(e)
        time.sleep(5)
    
class Post(BaseModel):
    """
    Post _summary_

    Args:
        BaseModel (_type_): _description_
    """
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

# my_posts.append({"id": "1",  "title": "first post", "content": "this is the first post"})
# my_posts.append({"id": "2", "title": "second post", "content": "this is the second post"})
# my_posts.append({"id": "3", "title": "third post", "content": "this is the third post"})

### generic functions

# def get_post(id):
#     post = [x for x in my_posts if int(x['id']) == id]
#     return post
    
# def get_post_index(id: int):
#     if len(my_posts) >=0 : 
#         for i, record in enumerate(my_posts):
#             if int(record['id']) == id:
#                 return i  

def get_all_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return posts

### routes
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    print(posts)
    return {"posts":posts}

@app.get("/")
def root(db: Session = Depends(get_db)): 
    """
    root _summary_

    Returns:
        _type_: _description_
    """
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"posts": posts}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"posts": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts(title, content) VALUES(%s, %s) RETURNING * """, (post.title, post.content))
    # new_post = cursor.fetchone()
    # conn.commit()
    return {"new_post" : "new_post"}

@app.get("/posts/latest")
def get_latest_post(response:Response):
    cursor.execute("""SELECT * from posts where id = (select max(id) from posts)""")
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"No posts found.")
    return {"payLoad": post}

@app.get("/posts/{id}")
def get_post_by_id(id: int, response: Response):
    cursor.execute("""SELECT * from posts where id = %s """, (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found.")
    return {"payLoad": post}

@app.delete("/posts/{id}")
def delete_post(id: int):
    # i= get_post_index(id)
    cursor.execute("""DELETE from posts where id = %s RETURNING * """,(str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found.")
    # my_posts.pop(i)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def put_update_post(id : int, post: Post):
    # i = get_post_index(id)
    cursor.execute("""UPDATE posts SET title=%s, content=%s where id = %s RETURNING * """, (post.title, post.content, str(id)))
    upd_post = cursor.fetchone()
    conn.commit()
    # post = post.dict()
    if upd_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found.")
    # my_posts[i] = post
    return {"payLoad": f"Post {id} updated."}
    