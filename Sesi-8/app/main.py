from fastapi import FastAPI
from api.v1 import users
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.user_summary = [
                        {
                            'id': 1,
                            'nama': 'Leanne Graham',
                            'email': 'Sincere@april.biz',
                            'kota': 'Gwenborough',
                            'jumlah_post': 10
                        },
                        {
                            'id': 2,
                            'nama': 'Ervin Howell',
                            'email': 'Shanna@melissa.tv',
                            'kota': 'Wisokyburgh',
                            'jumlah_post': 10
                        },
                        {
                            'id': 3,
                            'nama': 'Clementine Bauch',
                            'email': 'Nathan@yesenia.net',
                            'kota': 'McKenziehaven',
                            'jumlah_post': 10
                        },
                        {
                            'id': 4,
                            'nama': 'Patricia Lebsack',
                            'email': 'Julianne.OConner@kory.org',
                            'kota': 'South Elvis',
                            'jumlah_post': 10
                        },
                        {
                            'id': 5,
                            'nama': 'Chelsey Dietrich',
                            'email': 'Lucio_Hettinger@annie.ca',
                            'kota': 'Roscoeview',
                            'jumlah_post': 10
                        },
                        {
                            'id': 6,
                            'nama': 'Mrs. Dennis Schulist',
                            'email': 'Karley_Dach@jasper.info',
                            'kota': 'South Christy',
                            'jumlah_post': 10
                        },
                        {
                            'id': 7,
                            'nama': 'Kurtis Weissnat',
                            'email': 'Telly.Hoeger@billy.biz',
                            'kota': 'Howemouth',
                            'jumlah_post': 10
                        },
                        {
                            'id': 8,
                            'nama': 'Nicholas Runolfsdottir V',
                            'email': 'Sherwood@rosamond.me',
                            'kota': 'Aliyaview',
                            'jumlah_post': 10
                        },
                        {
                            'id': 9,
                            'nama': 'Glenna Reichert',
                            'email': 'Chaim_McDermott@dana.io',
                            'kota': 'Bartholomebury',
                            'jumlah_post': 10
                        },
                        {
                            'id': 10,
                            'nama': 'Clementina DuBuque',
                            'email': 'Rey.Padberg@karina.biz',
                            'kota': 'Lebsackbury',
                            'jumlah_post': 10
                        }]

    yield
    app.state.user_summary = []
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"messages":"hello world"}

@app.get("/health")
def health():
    return {"status":"ok"}

app.include_router(users.router, prefix="/api/v1")